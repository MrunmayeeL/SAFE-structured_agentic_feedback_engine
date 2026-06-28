import ast
with open('QuixBugs/python_programs/find_in_sorted.py') as f:
    code = f.read()

tree = ast.parse(code)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'find_in_sorted':
        print(ast.unparse(node))
        break
