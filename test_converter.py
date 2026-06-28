import os
import json


def load_json_tests(task_id):
    path = f"QuixBugs/json_testcases/{task_id}.json"

    if not os.path.exists(path):
        return None

    data = []

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            try:
                data.append(json.loads(line))
            except Exception as e:
                print(f"[JSON ERROR] {task_id}: {e}")

    return data if data else None


def build_asserts(task_id, data):
    lines = []

    for case in data:

        # CASE 1: dict format
        if isinstance(case, dict):
            inp = case["input"]
            out = case["output"]

        # CASE 2: list format
        elif isinstance(case, list) and len(case) == 2:
            inp, out = case

        else:
            print(f"[SKIPPED - bad format] {task_id}: {case}")
            continue

        # 🔥 CRITICAL FIX HERE

        # If input is already a list of arguments → use directly
        if isinstance(inp, list):
            args = ", ".join(repr(x) for x in inp)
        else:
            args = repr(inp)

        lines.append(f"assert {task_id}({args}) == {repr(out)}")

    return "\n".join(lines)


def extract_asserts(test_code):
    lines = []

    for line in test_code.split("\n"):
        line = line.strip()

        if line.startswith("assert"):
            lines.append(line)

    return lines


def convert_test(task_id, test_code):
    # STEP 1: JSON (PRIMARY PATH)
    data = load_json_tests(task_id)

    if data:
        print(f"[CONVERTED - JSON] {task_id} → {len(data)} tests")
        return build_asserts(task_id, data)

    # STEP 2: fallback (simple assert extraction)
    asserts = extract_asserts(test_code)

    if asserts:
        print(f"[CONVERTED - ASSERT] {task_id} → {len(asserts)} tests")
        return "\n".join(asserts)

    # STEP 3: skip
    print(f"[SKIPPED - cannot convert] {task_id}")
    return None