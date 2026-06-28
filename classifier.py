def classify_error(error):
    labels = []

    if "SyntaxError" in error:
        labels.append("SyntaxError")

    if "TypeError" in error:
        labels.append("TypeError")

    if "NoneType" in error:
        labels.append("NullReference")

    if "IndexError" in error:
        labels.append("IndexError")

    if "NameError" in error:
        labels.append("NameError")

    if "ImportError" in error or "ModuleNotFoundError" in error:
        labels.append("DependencyError")

    if not labels:
        labels.append("Unknown")

    return labels