def select_strategy(error_types):
    """
    Maps error categories to repair heuristics.
    """
    strategy_map = {
        "TypeError": [
            "validate variable types",
            "check None values",
            "preserve existing logic"
        ],
        "IndexError": [
            "validate array bounds",
            "check empty collections"
        ],
        "KeyError": [
            "check if key exists in dictionary",
            "use .get() with default value"
        ],
        "ValueError": [
            "validate input format",
            "check value ranges"
        ],
        "AttributeError": [
            "verify object has attribute",
            "check for initialization issues"
        ],
        "SyntaxError": [
            "fix structural errors",
            "check for missing brackets or colons"
        ],
        "NullReference": [
            "add null checks",
            "ensure object is initialized before use"
        ],
        "LogicError": [
            "trace algorithm steps",
            "verify base cases in recursion",
            "check loop termination conditions"
        ]
    }
    
    selected_strategies = []
    for etype in error_types:
        if etype in strategy_map:
            selected_strategies.extend(strategy_map[etype])
            
    if not selected_strategies:
        selected_strategies.append("perform general logic repair")
        
    return list(set(selected_strategies))
