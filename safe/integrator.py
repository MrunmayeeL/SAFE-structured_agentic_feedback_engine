import ast

def integrate_patch(original_code, patched_function_code, function_name):
    """
    Replaces a specific function in the original code with a new implementation using AST.
    """
    try:
        original_tree = ast.parse(original_code)
        patch_tree = ast.parse(patched_function_code)
        
        # Ensure function_name is valid (handles <module> or unknown from assertion errors)
        valid_func_names = [n.name for n in ast.walk(original_tree) if isinstance(n, ast.FunctionDef)]
        if function_name not in valid_func_names and valid_func_names:
            function_name = valid_func_names[0]
            
        # Find the function node in the patch
        new_func_node = None
        for node in ast.walk(patch_tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                new_func_node = node
                break
        
        if not new_func_node:
            # If function name doesn't match exactly, take the first function in the patch
            for node in ast.walk(patch_tree):
                if isinstance(node, ast.FunctionDef):
                    new_func_node = node
                    break
                    
        if not new_func_node:
            return original_code # Integration failed, no function found
            
        # Find the function in the original code and replace its lines
        for node in ast.walk(original_tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', len(original_code.splitlines()))
                
                lines = original_code.splitlines()
                patched_func_str = ast.unparse(new_func_node)
                
                new_lines = lines[:start_line] + patched_func_str.splitlines() + lines[end_line:]
                return "\n".join(new_lines)
                
        return original_code
    except Exception as e:
        print(f"Integration error: {e}")
        # Fallback to returning the original code if AST fails to prevent accumulating hallucinations
        return original_code
