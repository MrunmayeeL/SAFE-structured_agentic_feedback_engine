def select_strategy(error_type):
    strategies = {
        "SyntaxError": ["fix missing brackets/parentheses","check indentation","remove invalid syntax","correct function/statement structure"],
        "TypeError": ["check data types", "validate inputs"],
        "NullReference": ["add null checks", "fix return values"],
        "IndexError": ["check list bounds"],
        "NameError": ["check variable definition/imports"],
        "DependencyError": ["install/import missing module"]
    }
    
    selected = []

    for label in error_type:
        if label in strategies:
            selected.extend(strategies[label])

    # remove duplicates
    return list(set(selected)) if selected else ["general fix"]