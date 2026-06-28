import json

with open('results/logs/find_in_sorted_safe.json') as f:
    data = json.load(f)
    print("FINAL CODE:")
    print(data['final_code'])
    print("HISTORY:")
    for h in data['history']:
        print(h)
