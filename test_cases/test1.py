# none type error, null propogation
def get_data():
    return None

def process():
    data = get_data()
    return len(data)

print(process())