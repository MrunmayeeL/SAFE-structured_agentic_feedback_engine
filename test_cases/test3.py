# type mismatch

def get_numbers():
    return "123"

def compute():
    nums = get_numbers()
    return sum(nums)

print(compute())