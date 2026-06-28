import subprocess
import sys
import os
import tempfile
import traceback

def run_test(code, test_code):
    """
    Executes the code with the provided tests and captures any errors.
    """
    full_code = code + "\n\n" + test_code
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(full_code)
        temp_file = f.name
        
    try:
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10 # QuixBugs should run fast
        )
        
        success = result.returncode == 0
        output = result.stdout
        error = result.stderr
        
        # If success is false but error is empty, check stdout (sometimes pytest or others output there)
        if not success and not error:
            error = output
            
        return {
            "success": success,
            "error": error if not success else None,
            "stdout": output
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "TimeoutExpired: Execution exceeded 10 seconds (likely infinite loop)",
            "stdout": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Internal Error: {str(e)}\n{traceback.format_exc()}",
            "stdout": ""
        }
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
