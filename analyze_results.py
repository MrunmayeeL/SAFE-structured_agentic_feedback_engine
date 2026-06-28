import json, os, glob

results_dir = "results/logs"
safe_files = glob.glob(f"{results_dir}/*_safe.json")

baseline_success = 0
safe_success = 0
baseline_tokens = 0
safe_tokens = 0

diff_tasks = []

for safe_file in safe_files:
    baseline_file = safe_file.replace("_safe.json", "_baseline.json")
    if not os.path.exists(baseline_file): continue
    
    with open(safe_file) as f: safe_res = json.load(f)
    with open(baseline_file) as f: base_res = json.load(f)
    
    b_fix = base_res.get("fixed", False)
    s_fix = safe_res.get("fixed", False)
    
    baseline_tokens += base_res.get("avg_prompt_size", 0) * base_res.get("iterations", 0)
    safe_tokens += safe_res.get("avg_prompt_size", 0) * safe_res.get("iterations", 0)
    
    if b_fix: baseline_success += 1
    if s_fix: safe_success += 1
    
    if b_fix and not s_fix:
        diff_tasks.append(f"{safe_res.get('bug_id')} (Baseline fixed in {base_res.get('iterations')}, SAFE failed in {safe_res.get('iterations')})")
    elif s_fix and not b_fix:
        diff_tasks.append(f"{safe_res.get('bug_id')} (SAFE fixed in {safe_res.get('iterations')}, Baseline failed in {base_res.get('iterations')})")

print(f"Baseline Success: {baseline_success}")
print(f"SAFE Success: {safe_success}")
print(f"Baseline tokens (approx): {baseline_tokens}")
print(f"SAFE tokens (approx): {safe_tokens}")
print("Differences:")
for t in diff_tasks: print(t)
