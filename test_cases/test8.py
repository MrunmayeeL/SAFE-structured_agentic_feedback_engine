# /division by 0

def get_value():
    return 0

def process():
    x = get_value()
    return 10 / x

print(process())