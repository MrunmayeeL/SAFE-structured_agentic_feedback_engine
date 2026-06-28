import sys
import subprocess
import os


def run_pytest(task_id):
    """Run pytest for a specific task (optimized)"""

    test_path = f"python_testcases/test_{task_id}.py"

    if not os.path.exists(os.path.join("QuixBugs", test_path)):
        return {
            "success": False,
            "stdout": "",
            "error": f"Test file not found: {test_path}"
        }

    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                test_path,
                "-q",              # 🔥 no verbose
                "--tb=short"
            ],
            capture_output=True,
            text=True,
            cwd="QuixBugs"            
        )

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "error": "Timeout"
        }

    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "error": result.stderr if result.stderr else result.stdout
    }


def run_code(code):
    """Execute Python code directly and capture output/errors"""
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "error": result.stderr if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "stdout": "",
            "error": "Execution timeout"
        }
    finally:
        os.unlink(temp_file)