import os
import json
import time
import matplotlib.pyplot as plt
import numpy as np
from loader import load_quixbugs
from safe.executor import run_test
from safe.classifier import classify_error
from safe.analyzer import extract_context, extract_function_code
from safe.strategy import select_strategy
from safe.fixer import generate_fix_safe, estimate_tokens
from safe.integrator import integrate_patch
from baseline.fixer import generate_fix_baseline
from utils import calculate_changed_lines, check_syntax_validity, detect_hallucinations, get_prompt_size

# Configuration
DATASET_PATH = "QuixBugs"
MAX_ITERATIONS = 5
BUG_LIMIT = 25 # 20-25 bugs as requested

def run_safe_experiment(bug):
    task_id = bug['task_id']
    original_code = bug['code']
    test_code = bug['tests']
    
    current_code = original_code
    logs = []
    success = False
    
    for i in range(MAX_ITERATIONS):
        print(f"  [SAFE] Iteration {i+1} for {task_id}...")
        
        # 1. Execute
        exec_result = run_test(current_code, test_code)
        if exec_result['success']:
            success = True
            break
            
        error_msg = exec_result['error']
        
        # 2. Classify
        categories = classify_error(error_msg)
        
        # 3. Analyze Context
        context = extract_context(error_msg, current_code)
        if not context:
            # Fallback if context extraction fails
            context = {
                "line": 0,
                "function_name": task_id,
                "snippet": current_code
            }
            
        # 4. Strategy
        strategies = select_strategy(categories)
        
        # 5. Localized Prompt & LLM
        error_line = context.get('line', None)
        
        # Clean error message to minimize tokens while preserving test case assertions
        if error_msg:
            lines = error_msg.strip().split("\n")
            important_lines = []
            if "Traceback" in lines[0]:
                important_lines.append(lines[0])
            important_lines.extend([l.strip() for l in lines[:-3] if "assert " in l])
            important_lines.extend(lines[-3:])
            clean_error = "\n".join(important_lines)
        else:
            clean_error = ""
        
        fix_code = generate_fix_safe(categories, current_code, error_line, clean_error, strategies)
        
        if not fix_code:
            break
            
        # Log prompt size (approximate)
        prompt_size = get_prompt_size(current_code + clean_error + str(categories))
        
        # 6. Patch Integration
        new_code = fix_code
        
        # Log this iteration
        logs.append({
            "iteration": i + 1,
            "prompt_size": prompt_size,
            "syntax_valid": check_syntax_validity(fix_code),
            "hallucination": detect_hallucinations(fix_code),
            "changed_lines": calculate_changed_lines(current_code, new_code)
        })
        
        current_code = new_code
        
    return {
        "bug_id": task_id,
        "method": "SAFE",
        "fixed": success,
        "iterations": len(logs) + (1 if success else 0),
        "total_changed_lines": calculate_changed_lines(original_code, current_code),
        "avg_prompt_size": sum(l['prompt_size'] for l in logs) / len(logs) if logs else 0,
        "syntax_valid_rate": sum(1 for l in logs if l['syntax_valid']) / len(logs) if logs else 1,
        "hallucination_detected": any(l['hallucination'] for l in logs),
        "final_code": current_code,
        "history": logs
    }

def run_baseline_experiment(bug):
    task_id = bug['task_id']
    original_code = bug['code']
    test_code = bug['tests']
    
    current_code = original_code
    logs = []
    success = False
    
    for i in range(MAX_ITERATIONS):
        print(f"  [Baseline] Iteration {i+1} for {task_id}...")
        
        # 1. Execute
        exec_result = run_test(current_code, test_code)
        if exec_result['success']:
            success = True
            break
            
        error_msg = exec_result['error']
        
        # 2. Naive Prompt
        fix_code = generate_fix_baseline(current_code, error_msg)
        
        if not fix_code:
            break
            
        # Log prompt size
        prompt_size = get_prompt_size(current_code + error_msg)
        
        # Baseline replaces entire code
        new_code = fix_code
        
        # Log this iteration
        logs.append({
            "iteration": i + 1,
            "prompt_size": prompt_size,
            "syntax_valid": check_syntax_validity(fix_code),
            "hallucination": detect_hallucinations(fix_code),
            "changed_lines": calculate_changed_lines(current_code, new_code)
        })
        
        current_code = new_code
        
    return {
        "bug_id": task_id,
        "method": "Baseline",
        "fixed": success,
        "iterations": len(logs) + (1 if success else 0),
        "total_changed_lines": calculate_changed_lines(original_code, current_code),
        "avg_prompt_size": sum(l['prompt_size'] for l in logs) / len(logs) if logs else 0,
        "syntax_valid_rate": sum(1 for l in logs if l['syntax_valid']) / len(logs) if logs else 1,
        "hallucination_detected": any(l['hallucination'] for l in logs),
        "final_code": current_code,
        "history": logs
    }

def generate_plots(results):
    print("\n📊 Generating and saving plots...")
    os.makedirs("results/graphs", exist_ok=True)
    
    baseline_res = [r for r in results if r['method'] == 'Baseline']
    safe_res = [r for r in results if r['method'] == 'SAFE']
    
    labels = ['Baseline', 'SAFE']
    
    # 1. Repair Success Rate
    baseline_success = sum(1 for r in baseline_res if r['fixed']) / len(baseline_res) * 100 if baseline_res else 0
    safe_success = sum(1 for r in safe_res if r['fixed']) / len(safe_res) * 100 if safe_res else 0
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, [baseline_success, safe_success], color=['#ff9999','#66b3ff'])
    plt.ylabel('Success Rate (%)')
    plt.title('Repair Success Rate Comparison')
    plt.ylim(0, 100)
    for i, v in enumerate([baseline_success, safe_success]):
        plt.text(i, v + 2, f"{v:.1f}%", ha='center')
    plt.savefig('results/graphs/repair_success_rate.png')
    plt.close()
    
    # 2. Patch Minimality
    baseline_changed = [r['total_changed_lines'] for r in baseline_res if r['fixed']] or [0]
    safe_changed = [r['total_changed_lines'] for r in safe_res if r['fixed']] or [0]
    
    baseline_changed_mean = np.mean(baseline_changed)
    safe_changed_mean = np.mean(safe_changed)
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, [baseline_changed_mean, safe_changed_mean], color=['#ffb3e6','#c2c2f0'])
    plt.ylabel('Avg Total Changed Lines')
    plt.title('Patch Minimality (Successful Fixes)')
    for i, v in enumerate([baseline_changed_mean, safe_changed_mean]):
        plt.text(i, v + 0.1, f"{v:.1f}", ha='center')
    plt.savefig('results/graphs/patch_minimality.png')
    plt.close()
    
    # 3. Syntax Validation Rate
    baseline_syntax = np.mean([r['syntax_valid_rate'] for r in baseline_res]) * 100 if baseline_res else 0
    safe_syntax = np.mean([r['syntax_valid_rate'] for r in safe_res]) * 100 if safe_res else 0
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, [baseline_syntax, safe_syntax], color=['#ffcc99','#99ff99'])
    plt.ylabel('Syntax Validity Rate (%)')
    plt.title('Syntax Validation Comparison')
    plt.ylim(0, 100)
    for i, v in enumerate([baseline_syntax, safe_syntax]):
        plt.text(i, v + 2, f"{v:.1f}%", ha='center')
    plt.savefig('results/graphs/syntax_validation.png')
    plt.close()
    
    # 4. Hallucination Rate
    baseline_hallu = sum(1 for r in baseline_res if r['hallucination_detected']) / len(baseline_res) * 100 if baseline_res else 0
    safe_hallu = sum(1 for r in safe_res if r['hallucination_detected']) / len(safe_res) * 100 if safe_res else 0
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, [baseline_hallu, safe_hallu], color=['#c2c2f0','#ffb3e6'])
    plt.ylabel('Hallucination Rate (%)')
    plt.title('Hallucination Rate Comparison')
    plt.ylim(0, 100)
    for i, v in enumerate([baseline_hallu, safe_hallu]):
        plt.text(i, v + 2, f"{v:.1f}%", ha='center')
    plt.savefig('results/graphs/hallucination_rate.png')
    plt.close()
    
    # 5. Iteration Comparison
    baseline_iters = [r['iterations'] for r in baseline_res] or [0]
    safe_iters = [r['iterations'] for r in safe_res] or [0]
    
    baseline_iters_mean = np.mean(baseline_iters)
    safe_iters_mean = np.mean(safe_iters)
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, [baseline_iters_mean, safe_iters_mean], color=['#ffcc99','#99ff99'])
    plt.ylabel('Avg Iterations Used')
    plt.title('Iteration Comparison')
    for i, v in enumerate([baseline_iters_mean, safe_iters_mean]):
        plt.text(i, v + 0.1, f"{v:.1f}", ha='center')
    plt.savefig('results/graphs/iteration_comparison.png')
    plt.close()
    
    # --- New Per-Bug Graphs ---
    
    # Extract data aligned by bug_id
    bug_ids = [r['bug_id'] for r in baseline_res]
    
    b_dict = {r['bug_id']: r for r in baseline_res}
    s_dict = {r['bug_id']: r for r in safe_res}
    
    # Prepare data arrays
    b_prompts = [b_dict[b]['avg_prompt_size'] for b in bug_ids]
    s_prompts = [s_dict[b]['avg_prompt_size'] for b in bug_ids]
    
    b_changed = [b_dict[b]['total_changed_lines'] for b in bug_ids]
    s_changed = [s_dict[b]['total_changed_lines'] for b in bug_ids]
    
    b_fixed = [1 if b_dict[b]['fixed'] else 0 for b in bug_ids]
    s_fixed = [1 if s_dict[b]['fixed'] else 0 for b in bug_ids]
    
    # Prompt efficiency: 1000 / (total tokens) if fixed else 0
    b_eff = [1000 / (b_dict[b]['avg_prompt_size'] * b_dict[b]['iterations'] + 1) if b_dict[b]['fixed'] else 0 for b in bug_ids]
    s_eff = [1000 / (s_dict[b]['avg_prompt_size'] * s_dict[b]['iterations'] + 1) if s_dict[b]['fixed'] else 0 for b in bug_ids]
    
    x = np.arange(len(bug_ids))
    width = 0.35
    
    def plot_per_bug(b_data, s_data, title, ylabel, filename, figsize=(14, 6)):
        plt.figure(figsize=figsize)
        plt.bar(x - width/2, b_data, width, label='Baseline', color='#ff9999')
        plt.bar(x + width/2, s_data, width, label='SAFE', color='#66b3ff')
        plt.ylabel(ylabel)
        plt.title(title)
        plt.xticks(x, bug_ids, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'results/graphs/{filename}')
        plt.close()
        
    # 6. Prompt Size per Bug
    plot_per_bug(b_prompts, s_prompts, 'Average Prompt Size per Bug', 'Avg Tokens', 'prompt_size_per_bug.png')
    
    # 7. Changed Lines per Bug
    plot_per_bug(b_changed, s_changed, 'Total Changed Lines per Bug', 'Lines Changed', 'changed_lines_per_bug.png')
    
    # 8. Fixed per Bug
    plot_per_bug(b_fixed, s_fixed, 'Fix Status per Bug (1=Fixed, 0=Failed)', 'Fixed Status', 'fixed_per_bug.png')
    
    # 9. Prompt Efficiency
    plot_per_bug(b_eff, s_eff, 'Prompt Efficiency per Bug (Fixed / Tokens * 1000)', 'Efficiency Score', 'prompt_efficiency_per_bug.png')

    print("✅ Plots saved to results/graphs/")

def main():
    print("🚀 Starting SAFE v2 Experiments...")
    bugs = load_quixbugs(DATASET_PATH)
    bugs = bugs[:BUG_LIMIT]
    
    results = []
    
    os.makedirs("results/logs", exist_ok=True)
    os.makedirs("results/examples", exist_ok=True)
    
    for bug in bugs:
        task_id = bug['task_id']
        print(f"\nProcessing bug: {task_id}")
        
        # Run Baseline
        baseline_res = run_baseline_experiment(bug)
        results.append(baseline_res)
        
        # Run SAFE
        safe_res = run_safe_experiment(bug)
        results.append(safe_res)
        
        # Save logs per bug
        os.makedirs("results/logs", exist_ok=True)
        os.makedirs("results/examples", exist_ok=True)
        with open(f"results/logs/{task_id}_baseline.json", "w") as f:
            json.dump(baseline_res, f, indent=2)
        with open(f"results/logs/{task_id}_safe.json", "w") as f:
            json.dump(safe_res, f, indent=2)
            
        # Save qualitative example
        with open(f"results/examples/{task_id}_comparison.txt", "w") as f:
            f.write(f"BUG: {task_id}\n")
            f.write("="*50 + "\n")
            f.write("ORIGINAL CODE:\n")
            f.write(bug['code'] + "\n\n")
            f.write("="*50 + "\n")
            f.write("BASELINE PATCH:\n")
            f.write(baseline_res['final_code'] + "\n\n")
            f.write("="*50 + "\n")
            f.write("SAFE PATCH:\n")
            f.write(safe_res['final_code'] + "\n\n")

    # Save all results
    with open("results/all_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    # Generate graphs
    generate_plots(results)
        
    print("\n✅ Experiments completed. Results saved to results/logs/ and graphs to results/graphs/")

if __name__ == "__main__":
    main()
