import json
import glob
import os
from experiment_runner import generate_plots

results = []
log_files = glob.glob('results/logs/*.json')

# First collect all task_ids to ensure we get both baseline and safe
tasks = set()
for f in log_files:
    basename = os.path.basename(f)
    if '_baseline.json' in basename:
        tasks.add(basename.replace('_baseline.json', ''))
    elif '_safe.json' in basename:
        tasks.add(basename.replace('_safe.json', ''))

for task in tasks:
    b_file = f'results/logs/{task}_baseline.json'
    s_file = f'results/logs/{task}_safe.json'
    
    if os.path.exists(b_file):
        with open(b_file) as f:
            results.append(json.load(f))
            
    if os.path.exists(s_file):
        with open(s_file) as f:
            results.append(json.load(f))

generate_plots(results)
