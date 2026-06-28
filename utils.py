import difflib
import ast
import re

def calculate_changed_lines(original, repaired):
    """
    Calculates the number of changed lines using unified diff.
    """
    diff = list(difflib.unified_diff(
        original.splitlines(),
        repaired.splitlines(),
        lineterm=""
    ))
    
    # Count lines starting with + or - (excluding the header)
    count = 0
    for line in diff:
        if (line.startswith("+") or line.startswith("-")) and not (line.startswith("+++") or line.startswith("---")):
            count += 1
    return count

def check_syntax_validity(code):
    """
    Checks if the code is syntactically valid by attempting to parse it into an AST.
    """
    try:
        ast.parse(code)
        return True
    except:
        return False

def detect_hallucinations(code):
    """
    Detects potential hallucinations like TODOs, placeholders, or fake helpers.
    """
    patterns = [
        r"#\s*TODO",
        r"#\s*FIXME",
        r"\.\.\.",
        r"pass\s*#",
        r"implement_here",
        r"your_code_here",
        r"fix_this",
        r"dummy_function"
    ]
    
    for pattern in patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return True
    return False

def get_prompt_size(prompt):
    """
    Returns the character count of the prompt.
    """
    return len(prompt)
