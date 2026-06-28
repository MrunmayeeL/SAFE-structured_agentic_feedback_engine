def build_inline_test(task_id):
    if task_id == "bitcount":
        return """
assert bitcount(0) == 0
assert bitcount(5) == 2
assert bitcount(255) == 8
"""

    elif task_id == "gcd":
        return """
assert gcd(12, 8) == 4
assert gcd(7, 3) == 1
"""

    elif task_id == "bucketsort":
        return """
assert bucketsort([3,1,2]) == [1,2,3]
"""
    
    # fallback
    return None

