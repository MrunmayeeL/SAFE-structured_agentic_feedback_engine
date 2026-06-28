# non existent key
def get_data():
    return {}

def process():
    d = get_data()
    return d["key"]

print(process())