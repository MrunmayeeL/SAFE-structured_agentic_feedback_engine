# from executor import run_code

# code = """
# x = None
# print(len(x))
# """

# result = run_code(code)

# print(result)
# working

# from classifier import classify_error

# error = "TypeError: object of type 'NoneType' has no len()"

# print(classify_error(error))

# working

# from analyzer import extract_context

# error = """
# Traceback (most recent call last):
#   File "temp.py", line 3
#     print(len(x))
# TypeError: object of type 'NoneType'
# """

# code = """
# x = None
# print(len(x))
# """

# print(extract_context(error, code))

#working

# from analyzer import analyze_propagation

# code = """
# def get_data():
#     return None

# def process():
#     data = get_data()
#     return len(data)
# """

# print(analyze_propagation(code))
# working

# from analyzer import extract_context, build_propagation_chain

# code = """
# def get_data():
#     return None

# def process():
#     data = get_data()
#     return len(data)
# """

# error = """
# File "temp.py", line 6
#     return len(data)
# TypeError: object of type 'NoneType'
# """

# context = extract_context(error, code)

# print(build_propagation_chain(code, context))

# working


# from analyzer import build_context_snippets, extract_context

# code = """
# def get_data():
#     return None

# def process():
#     data = get_data()
#     return len(data)
# """

# error = """
# File "temp.py", line 6
#     return len(data)
# TypeError
# """

# context = extract_context(error, code)

# print(build_context_snippets(code, context))

# working

from fixer import generate_fix

code = "x=None\nprint(len(x))"

error = "TypeError"

diagnosis = {"type": "TypeError"}

snippets = {
    "error_snippet": "print(len(x))",
    "propagation": ["x → None"]
}

output = generate_fix(code, error, diagnosis, snippets)

print(output)

# not working because first word becomes python