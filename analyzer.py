# import re
# import ast

# def extract_context(error):
#     match = re.search(r'File "(.*?)", line (\d+)', error)
#     if match:
#         return {
#             "file": match.group(1),
#             "line": int(match.group(2))
#         }
#     return {}

# class VariableTracker(ast.NodeVisitor):
#     def __init__(self):
#         self.assignments = {}

#     def visit_Assign(self, node):
#         if isinstance(node.targets[0], ast.Name):
#             var = node.targets[0].id
#             self.assignments[var] = ast.dump(node.value)
#         self.generic_visit(node)

# def analyze_propagation(code):
#     try:
#         tree = ast.parse(code)
#         tracker = VariableTracker()
#         tracker.visit(tree)
#         return tracker.assignments
#     except:
#         return {}


# import re

# def get_line_from_code(code, line_no):
#     """
#     Extract exact line from source code using line number
#     """
#     try:
#         lines = code.split("\n")
#         if 0 < line_no <= len(lines):
#             return lines[line_no - 1].strip()
#     except:
#         pass
#     return None


# def extract_context(error, code):
#     """
#     Extract:
#     - file
#     - line number
#     - exact code line (best effort)
#     """

#     lines = error.split("\n")

#     file = None
#     line_no = None
#     code_line = None

#     # Step 1: Extract file + line number
#     for i, line in enumerate(lines):
#         match = re.search(r'File "(.*?)", line (\d+)', line)
#         if match:
#             file = match.group(1)
#             line_no = int(match.group(2))

#             # Step 2: Try extracting from actual source code (BEST METHOD)
#             code_line = get_line_from_code(code, line_no)

#             # Step 3: Fallback → use traceback next line
#             if not code_line and i + 1 < len(lines):
#                 code_line = lines[i + 1].strip()

#             break

#     return {
#         "file": file,
#         "line": line_no,
#         "code_line": code_line
#     }
    
    
import re
import ast

# ----------------------------
# CONTEXT EXTRACTION
# ----------------------------
def get_line_from_code(code, line_no):
    try:
        lines = code.split("\n")
        if 0 < line_no <= len(lines):
            return lines[line_no - 1].strip()
    except:
        pass
    return None


def extract_context(error, code):
    lines = error.split("\n")

    file = None
    line_no = None
    code_line = None

    for i, line in enumerate(lines):
        match = re.search(r'File "(.*?)", line (\d+)', line)
        if match:
            file = match.group(1)
            line_no = int(match.group(2))

            # BEST: extract from actual code
            code_line = get_line_from_code(code, line_no)

            # fallback to traceback
            if not code_line and i + 1 < len(lines):
                code_line = lines[i + 1].strip()

            break

    return {
        "file": file,
        "line": line_no,
        "code_line": code_line
    }


# ----------------------------
# AST VARIABLE TRACKING
# ----------------------------
class VariableTracker(ast.NodeVisitor):
    def __init__(self):
        self.assignments = {}

    def visit_Assign(self, node):
        if isinstance(node.targets[0], ast.Name):
            var = node.targets[0].id
            self.assignments[var] = ast.unparse(node.value)
        self.generic_visit(node)


def analyze_propagation(code):
    try:
        tree = ast.parse(code)
        tracker = VariableTracker()
        tracker.visit(tree)
        return tracker.assignments
    except:
        return {}


# ----------------------------
# FUNCTION RETURN TRACKING
# ----------------------------
def find_function_returns(code):
    try: 
        tree = ast.parse(code)
    except:
        return {}
    returns = {}

    class FuncVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            for n in ast.walk(node):
                if isinstance(n, ast.Return):
                    returns[node.name] = ast.unparse(n.value) if n.value else None

    FuncVisitor().visit(tree)
    return returns


# ----------------------------
# VARIABLE EXTRACTION
# ----------------------------
def extract_variables(code_line):
    return re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code_line or "")


# ----------------------------
# TRACE VARIABLE ORIGIN
# ----------------------------
def trace_variable_origin(var, assignments, func_returns):
    if var not in assignments:
        return None

    value = assignments[var]

    # function call case
    if "(" in value:
        func_name = value.split("(")[0]

        if func_name in func_returns:
            return f"{var} → {func_name}() → returns {func_returns[func_name]}"

    # direct assignment
    return f"{var} → {value}"


# ----------------------------
# BUILD PROPAGATION CHAIN
# ----------------------------
def build_propagation_chain(code, context):
    assignments = analyze_propagation(code)
    func_returns = find_function_returns(code)

    code_line = context.get("code_line", "")
    variables = extract_variables(code_line)

    chain = []

    for var in variables:
        origin = trace_variable_origin(var, assignments, func_returns)
        if origin:
            chain.append(origin)

    return chain


# ----------------------------
# SNIPPET BUILDER (FINAL)
# ----------------------------
def get_snippet(code, line_no, window=2):
    if line_no is None:
        return code[:200]   # fallback

    lines = code.split("\n")
    start = max(0, line_no - window - 1)
    end = min(len(lines), line_no + window)
    return "\n".join(lines[start:end])


def build_context_snippets(code, context):
    line_no = context.get("line")
    if line_no is None:
        return {
            "error_snippet": code[:200],
            "propagation": []
        }
    error_snippet = get_snippet(code, line_no)
    propagation_chain = build_propagation_chain(code, context)

    return {
        "error_snippet": error_snippet,
        "propagation": propagation_chain
    }