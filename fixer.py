# from groq import Groq

# client = Groq(api_key="YOUR_API_KEY")

# def generate_fix(code, error, diagnosis):
#     prompt = f"""
# You are a precise debugging system.

# DIAGNOSIS:
# {diagnosis}

# CODE:
# {code}

# ERROR:
# {error}

# INSTRUCTIONS:
# - Fix the root cause
# - Do not over-modify
# - Keep structure same
# - Return ONLY valid Python code
# """

#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0
#     )

#     output = response.choices[0].message.content

#     # clean markdown if present
#     if "```" in output:
#         output = output.split("```")[1]

#     return output
def clean_extra_lines(code):
    cleaned = []
    for line in code.split("\n"):
        stripped = line.strip()

        # remove junk
        if stripped.startswith("# Example"):
            continue
        if stripped.startswith("print("):
            continue
        if stripped.startswith("assert "):
            continue
        if "input_data" in stripped:
            continue

        cleaned.append(line)

    return "\n".join(cleaned)


from groq import Groq

import os
from groq import Groq

# Load Groq API key from environment variables
api_key = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

def generate_fix(code, error, diagnosis, snippets):
    if not client:
        raise ValueError("Groq API client is not initialized. Please set the GROQ_API_KEY environment variable.")
    propagation_text = "\n".join(snippets.get("propagation", []))

    prompt = f"""
You are a precise debugging system.

CODE:
{code}

ERROR:
{error}

ERROR LOCATION:
{snippets.get("error_snippet")}

PROPAGATION TRACE:
{propagation_text}

DIAGNOSIS:
{diagnosis}

INSTRUCTIONS:
- Fix the ROOT CAUSE of the bug
- Prefer fixing source over patching symptom
- Do not over-modify
- Return ONLY valid Python code
- Do NOT remove existing logic unless it is being changed
- Do NOT leave incomplete functions
- Ensure the code is fully executable
- DO NOT modify or redefine test variables (e.g., input_data, expected)
- Only modify the original function implementation
"""

    response = client.chat.completions.create(
        model="qwen2.5-coder:1.5b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    output = response.choices[0].message.content

    if "```" in output:
        parts = output.split("```")
        if len(parts) >= 2:
            code_block = parts[1].strip()

            if code_block.startswith("python"):
                code_block = code_block[len("python"):]

            output = code_block.strip()

    # STEP 2: ALWAYS clean tokens (outside condition!)
    output = output.replace("<|python_tag|>", "")
    output = output.replace("<|endoftext|>", "")
    output = output.replace("```", "")
    output = clean_extra_lines(output)
            
    def extract_function_only(code):
        idx = code.find("def ")
        if idx != -1:
            return code[idx:]
        return code

    output = extract_function_only(output)

    # STEP 5: final cleanup
    output = output.strip()   
    if "def " not in output:
        print("⚠️ Invalid patch, returning original code")
        return code
    return output