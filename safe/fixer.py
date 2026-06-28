import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:1.5b"

def generate_fix_safe(bug_categories, full_code, error_line_no, traceback, strategies):
    """
    Generates a localized repair using an efficient SAFE prompt structure.
    """
    lines = full_code.splitlines()
    if error_line_no is not None and 0 < error_line_no <= len(lines) and "LogicError" not in bug_categories:
        lines[error_line_no - 1] += "  # <--- ERROR HERE"
    annotated_code = "\n".join(lines)

    cats = ", ".join(bug_categories)
    
    strats = ", ".join(strategies)
    prompt = f"""Fix code. Strategy: {strats}

{annotated_code}

Error:
{traceback}

Return the completely fixed code.
"""
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_predict": 4096
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        output = response.json()['message']['content']
        
        # Extract code block if model wrapped it
        code_match = re.search(r"```(?:python)?\n(.*?)\n```", output, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
            
        # Extract if model forgot to close the backticks
        code_match_incomplete = re.search(r"```(?:python)?\n(.*)", output, re.DOTALL)
        if code_match_incomplete:
            return code_match_incomplete.group(1).strip()
        
        return output.strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        return None

def estimate_tokens(text):
    # Rough estimate: 1 token ~= 4 characters for code
    return len(text) // 4
