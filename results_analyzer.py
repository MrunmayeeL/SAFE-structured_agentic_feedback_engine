import json
import os
import matplotlib.pyplot as plt
import pandas as pd

def generate_graphs(results):
    # Prepare data for plotting
    df = pd.DataFrame(results)
    
    # Group by method
    summary = df.groupby('method').agg({
        'fixed': 'sum',
        'total_changed_lines': 'mean',
        'syntax_valid_rate': 'mean',
        'avg_prompt_size': 'mean',
        'hallucination_detected': 'sum',
        'iterations': 'mean'
    }).reset_index()
    
    # Graph 1: Repair Success Comparison
    plt.figure(figsize=(8, 6))
    plt.bar(summary['method'], summary['fixed'], color=['blue', 'green'])
    plt.title('Repair Success Comparison')
    plt.ylabel('Fixed Bugs Count')
    plt.savefig('results/graphs/repair_success.png')
    plt.close()
    
    # Graph 2: Average Changed Lines
    plt.figure(figsize=(8, 6))
    plt.bar(summary['method'], summary['total_changed_lines'], color=['blue', 'green'])
    plt.title('Average Changed Lines (Patch Minimality)')
    plt.ylabel('Avg Changed Lines')
    plt.savefig('results/graphs/patch_minimality.png')
    plt.close()
    
    # Graph 3: Syntax Validity Rate
    plt.figure(figsize=(8, 6))
    plt.bar(summary['method'], summary['syntax_valid_rate'] * 100, color=['blue', 'green'])
    plt.title('Syntax Validity Rate')
    plt.ylabel('Rate (%)')
    plt.savefig('results/graphs/syntax_validity.png')
    plt.close()
    
    # Graph 4: Prompt Size Comparison
    plt.figure(figsize=(8, 6))
    plt.bar(summary['method'], summary['avg_prompt_size'], color=['blue', 'green'])
    plt.title('Average Prompt Size')
    plt.ylabel('Avg Character Count')
    plt.savefig('results/graphs/prompt_efficiency.png')
    plt.close()
    
    # Graph 5: Hallucination Rate
    plt.figure(figsize=(8, 6))
    plt.bar(summary['method'], summary['hallucination_detected'], color=['blue', 'green'])
    plt.title('Hallucination Rate')
    plt.ylabel('Count of Hallucinated Repairs')
    plt.savefig('results/graphs/hallucination_rate.png')
    plt.close()
    
    # Graph 6: Iteration Count
    plt.figure(figsize=(8, 6))
    plt.bar(summary['method'], summary['iterations'], color=['blue', 'green'])
    plt.title('Average Iterations to Repair')
    plt.ylabel('Avg Iterations')
    plt.savefig('results/graphs/iteration_comparison.png')
    plt.close()

def generate_tables(results):
    df = pd.DataFrame(results)
    
    # Overall comparison table
    summary = df.groupby('method').agg({
        'fixed': 'sum',
        'total_changed_lines': 'mean',
        'syntax_valid_rate': 'mean',
        'avg_prompt_size': 'mean',
        'hallucination_detected': 'sum',
        'iterations': 'mean'
    }).reset_index()
    
    summary.to_csv('results/tables/overall_comparison.csv', index=False)
    
    with open('results/tables/overall_comparison.md', 'w') as f:
        f.write("# Overall Comparison Table\n\n")
        f.write(summary.to_markdown(index=False))
        
    # Per-bug metrics table
    df_metrics = df[['bug_id', 'method', 'fixed', 'total_changed_lines', 'iterations']]
    df_metrics.to_csv('results/tables/per_bug_metrics.csv', index=False)
    
    with open('results/tables/per_bug_metrics.md', 'w') as f:
        f.write("# Per-Bug Metrics Table\n\n")
        f.write(df_metrics.to_markdown(index=False))

def main():
    if not os.path.exists('results/all_results.json'):
        print("No results found. Run experiment_runner.py first.")
        return
        
    with open('results/all_results.json', 'r') as f:
        results = json.load(f)
        
    os.makedirs("results/graphs", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)
    
    generate_graphs(results)
    generate_tables(results)
    print("✅ Graphs and tables generated in results/graphs/ and results/tables/")

if __name__ == "__main__":
    main()
