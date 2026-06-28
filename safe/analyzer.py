import re
import ast

def extract_context(error_msg, code):
    """
    Identifies the failing line and function from the traceback and extracts localized context.
    """
    # Find the last "File ..., line ..." in the traceback
    matches = list(re.finditer(r'File ".*?", line (\d+)(?:, in (\w+))?', error_msg))
    if not matches:
        return None
    
    last_match = matches[-1]
    line_no = int(last_match.group(1))
    function_name = last_match.group(2)
    
    # If function name is missing in traceback, try to find it via AST
    if not function_name:
        function_name = find_function_at_line(code, line_no)
        
    return {
        "line": line_no,
        "function_name": function_name,
        "snippet": get_localized_snippet(code, line_no, window=10)
    }

def find_function_at_line(code, line_no):
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.lineno <= line_no <= getattr(node, 'end_lineno', node.lineno):
                    return node.name
    except:
        pass
    return "unknown"

def get_localized_snippet(code, line_no, window=10):
    lines = code.splitlines()
    start = max(0, line_no - window - 1)
    end = min(len(lines), line_no + window)
    
    snippet_lines = []
    for i in range(start, end):
        prefix = "-> " if i + 1 == line_no else "   "
        snippet_lines.append(f"{prefix}{i+1}: {lines[i]}")
        
    return "\n".join(snippet_lines)

def extract_function_code(code, function_name):
    """
    Extracts the full source code of a specific function using AST.
    """
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                # Get the lines of the function
                lines = code.splitlines()
                # end_lineno is available in Python 3.8+
                end_lineno = getattr(node, 'end_lineno', len(lines))
                return "\n".join(lines[node.lineno-1:end_lineno])
    except:
        pass
    return None
