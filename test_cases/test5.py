#type none propogation

def f1():
    return None

def f2():
    return f1()

def f3():
    x = f2()
    return len(x)

print(f3())