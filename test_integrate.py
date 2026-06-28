import ast
original_code = """def find_in_sorted(arr, x):
    def binsearch(start, end):
        if start == end:
            return -1
        mid = start + (end - start) // 2
        if x < arr[mid]:
            return binsearch(start, mid)
        elif x > arr[mid]:
            return binsearch(mid, end)
        else:
            return mid

    return binsearch(0, len(arr))
"""

patched_function_code = """def find_in_sorted(arr, x):
def binsearch(start, end):
    if start > end:
        return -1
    mid = start + (end - start) // 2
    if x < arr[mid]:
        return binsearch(start, mid - 1)
    elif x > arr[mid]:
        return binsearch(mid + 1, end)
    else:
        return mid

    return binsearch(0, len(arr))
"""

try:
    original_tree = ast.parse(original_code)
    patch_tree = ast.parse(patched_function_code)
    
    function_name = 'find_in_sorted'
    new_func_node = None
    for node in ast.walk(patch_tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            new_func_node = node
            break
            
    if not new_func_node:
        for node in ast.walk(patch_tree):
            if isinstance(node, ast.FunctionDef):
                new_func_node = node
                break
                
    for node in ast.walk(original_tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            start_line = node.lineno - 1
            end_line = getattr(node, 'end_lineno', len(original_code.splitlines()))
            
            lines = original_code.splitlines()
            patched_func_str = ast.unparse(new_func_node)
            
            new_lines = lines[:start_line] + patched_func_str.splitlines() + lines[end_line:]
            res = "\n".join(new_lines)
            print("NEW CODE:")
            print(res)
            
            try:
                ast.parse(res)
                print("AST PARSE NEW CODE: SUCCESS")
            except Exception as e:
                print("AST PARSE NEW CODE FAILED:", e)
            break
except Exception as e:
    print("Integration error:", e)
