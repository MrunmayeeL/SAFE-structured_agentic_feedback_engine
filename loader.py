import os
from test_builder import build_inline_test

class BugTask:
    def __init__(self, code, test_code, task_id):
        self.code = code
        self.test_code = test_code
        self.task_id = task_id


from test_converter import convert_test
import os

def load_quixbugs(path):
    tasks = []
    skip = ["breadth_first_search", "depth_first_search", "detect_cycle"]

    prog_dir = f"{path}/python_programs"
    test_dir = f"{path}/python_testcases"

    for file in os.listdir(prog_dir):
        if not file.endswith(".py"):
            continue

        task_id = file.replace(".py", "")
        if task_id in skip:
            continue

        # Load function code ONLY
        with open(f"{prog_dir}/{file}") as f:
            function_code = f.read()

        test_path = f"{test_dir}/test_{task_id}.py"

        if not os.path.exists(test_path):
            continue

        with open(test_path) as f:
            raw_test = f.read()

        # Convert test
        test_code = convert_test(task_id, raw_test)

        if not test_code:
            test_code = build_inline_test(task_id)

        if not test_code:
            print(f"[SKIPPED - NO TESTS] {task_id}")
            continue

        if "assert" not in test_code:
            print(f"[SKIPPED - INVALID TEST] {task_id}")
            continue

        # ✅ DO NOT combine
        tasks.append({
            "task_id": task_id,
            "code": function_code,   # ONLY function
            "tests": test_code       # ONLY tests
        })

    return tasks