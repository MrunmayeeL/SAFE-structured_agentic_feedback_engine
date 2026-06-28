# from executor import run_code
# from classifier import classify_error
# from analyzer import extract_context, analyze_propagation
# from strategy import select_strategy
# from fixer import generate_fix

# def read_code_from_file(file_path):
#     try:
#         with open(file_path, "r") as f:
#             return f.read()
#     except Exception as e:
#         print("Error reading file:", e)
#         return ""
    
    
# def debug_loop(code, max_iter=3):
#     for i in range(max_iter):
#         print(f"\n--- Iteration {i+1} ---")

#         result = run_code(code)

#         if result["success"]:
#             print("✅ Code fixed!")
#             return code

#         error = result["error"]
#         print("Error:", error)

#         error_type = classify_error(error)
#         context = extract_context(error)
#         propagation = analyze_propagation(code)
#         strategy = select_strategy(error_type)

#         diagnosis = {
#             "type": error_type,
#             "context": context,
#             "propagation": propagation,
#             "strategy": strategy
#         }

#         print("Diagnosis:", diagnosis)

#         code = generate_fix(code, error, diagnosis)

#     print("❌ Failed to fix")
#     return code


# if __name__ == "__main__":
#     file_path = "test_cases/example1.py"
#     buggy_code = read_code_from_file(file_path)
#     final_code = debug_loop(buggy_code)
#     print("\nFinal Code:\n", final_code)



from executor import  run_code
from classifier import classify_error
from analyzer import extract_context, build_context_snippets
from strategy import select_strategy
from fixer import generate_fix
from loader import load_quixbugs


import json
import os

dataset_path = "QuixBugs"   

import difflib

def show_diff(old, new):
    print("\n===== CODE DIFF =====")
    for line in difflib.unified_diff(
        old.splitlines(),
        new.splitlines(),
        lineterm=""
    ):
        print(line)


def run_dataset(path, limit=5):
    tasks = load_quixbugs(path)
    results = []

    for task in tasks[:limit]:
        print(f"\n=== TASK: {task['task_id']} ===")

        success, steps = debug_loop(task["code"], task["tests"], task["task_id"])

        results.append({
            "task_id": task["task_id"],
            "success": success,
            "steps": steps,
        })

    return results

def save_trace(trace):
    os.makedirs("logs", exist_ok=True)

    file_name = trace["file"].replace("/", "_").replace(".py", "")
    path = f"logs/{file_name}.json"

    with open(path, "w") as f:
        json.dump(trace, f, indent=4)
        
        
def baseline_loop(function_code, tests, task_id, max_iter=3):
    from fixer import generate_fix

    for i in range(max_iter):
        print(f"\n--- Baseline Iteration {i+1} ---")

        full_code = function_code + "\n\n" + tests
        result = run_code(full_code)

        if result["success"]:
            print("✅ Baseline fixed code!")
            return True, i+1

        error = result["error"]
        print("Baseline Error:", error)

        new_function_code = generate_fix(
            function_code,
            error,
            "Fix this code",
            {
                "error_snippet": function_code,
                "propagation": []
            }
        )

        show_diff(function_code, new_function_code)
        function_code = new_function_code

    print("❌ Baseline failed")
    return False, max_iter


def read_code_from_file(file_path):
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print("Error reading file:", e)
        return ""


def debug_loop(function_code, tests, task_id="unknown", max_iter=3):
    trace = {
        "file": task_id,
        "iterations": []
    }

    for i in range(max_iter):
        print(f"\n--- Iteration {i+1} ---")

        full_code = function_code + "\n\n" + tests
        result = run_code(full_code)

        if result["success"]:
            print("Code fixed!")
            print("\n===== FINAL FIXED CODE =====\n")
            print(function_code)

            trace["final_success"] = True
            trace["steps"] = i + 1
            save_trace(trace)
            return True, i+1

        error = result["error"]

        if "timeout" in error.lower():
            print("⚠️ Timeout detected → likely infinite loop")

            new_function_code = generate_fix(
                function_code,
                "Timeout: infinite loop or non-terminating logic",
                {"type": ["Timeout"]},
                {
                    "error_snippet": function_code[:200],
                    "propagation": []
                }
            )

            show_diff(function_code, new_function_code)
            function_code = new_function_code
            continue

        print("Error:", error)

        error_type = classify_error(error)
        context = extract_context(error, function_code)
        strategy = select_strategy(error_type)

        diagnosis = {
            "type": error_type,
            "context": context,
            "strategy": strategy
        }

        snippets = build_context_snippets(function_code, context)

        print("Propagation:", snippets["propagation"])

        new_function_code = generate_fix(function_code, error, diagnosis, snippets)

        show_diff(function_code, new_function_code)

        print("\n🔧 GENERATED FIX:\n")
        print(new_function_code[:500])

        function_code = new_function_code

        if "assert" not in tests:
            print("❌ TEST CORRUPTION DETECTED")
            return False, i+1

        trace["iterations"].append({
            "iteration": i + 1,
            "error": error,
            "labels": error_type,
            "context": context,
            "propagation": snippets["propagation"],
            "strategy": strategy,
            "generated_code": function_code
        })

    print("❌ Failed to fix")
    trace["final_success"] = False
    trace["steps"] = max_iter
    save_trace(trace)

    return False, max_iter


def evaluate(results, name):
    total = len(results)
    success = sum(1 for r in results if r["success"])

    avg_steps = sum(r["steps"] for r in results) / total if total else 0
    success_steps = (
        sum(r["steps"] for r in results if r["success"]) / success
        if success else 0
    )

    print(f"\n===== {name} SUMMARY =====")
    print(f"Total Tasks: {total}")
    print(f"Success: {success}/{total}")
    print(f"Success Rate: {success/total:.2f}" if total else "N/A")
    print(f"Avg Steps (All): {avg_steps:.2f}")
    print(f"Avg Steps (Success Only): {success_steps:.2f}")

if __name__ == "__main__":
    path = "QuixBugs"   # your repo path

    print("\n===== YOUR SYSTEM =====")
    results1 = run_dataset(path)

    print("\n===== BASELINE =====")

    # baseline run
    from loader import load_quixbugs
    tasks = load_quixbugs(path)

    baseline_results = []

    for task in tasks[:5]:
        print(f"\n=== BASELINE TASK: {task['task_id']} ===")

        success, steps = baseline_loop(task["code"],task["tests"], task["task_id"])

        baseline_results.append({
            "task_id": task["task_id"],
            "success": success,
            "steps": steps
        })

    evaluate(results1, "YOUR SYSTEM")
    evaluate(baseline_results, "BASELINE")