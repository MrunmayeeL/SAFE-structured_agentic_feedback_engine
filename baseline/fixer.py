import requests
import json
import re

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5-coder:1.5b"

def generate_fix_baseline(full_file_code, traceback):
    """
    Generates a repair using the Naive Baseline prompt structure.
    """
    prompt = f"""Fix this Python code.

{full_file_code}

Error:
{traceback}

Return corrected code.
"""
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {
            "temperature": 0,
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
