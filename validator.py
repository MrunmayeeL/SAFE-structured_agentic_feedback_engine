from executor import run_code

def validate(code):
    result = run_code(code)
    return result["success"]