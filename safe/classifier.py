import re

def classify_error(error_msg):
    """
    Classifies the error message into one or more categories based on keywords and patterns.
    Supported labels: TypeError, IndexError, KeyError, ValueError, AttributeError, SyntaxError, NullReference, LogicError
    """
    labels = []
    
    # Predefined mapping of keywords to labels
    mapping = {
        "TypeError": "TypeError",
        "IndexError": "IndexError",
        "KeyError": "KeyError",
        "ValueError": "ValueError",
        "AttributeError": "AttributeError",
        "SyntaxError": "SyntaxError",
        "NoneType": "NullReference",
        "AssertionError": "LogicError",
        "Timeout": "LogicError"
    }
    
    for key, label in mapping.items():
        if key in error_msg:
            labels.append(label)
            
    if not labels:
        labels.append("LogicError") # Default for unknown errors (likely logic bugs)
        
    return list(set(labels))
