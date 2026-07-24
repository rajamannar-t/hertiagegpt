
"""
clean_data.py
HeritageGPT - Data Cleaning Pipeline
"""

import os
import json
import re
from copy import deepcopy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATASET_DIR = os.path.join(PROJECT_ROOT, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "cleaned_data")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

log_lines = []

def clean_string(value):
    if not isinstance(value, str):
        return value
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" ,", ",").replace(" .", ".")
    return value

def deduplicate_list(lst):
    seen = set()
    result = []
    for item in lst:
        key = json.dumps(item, sort_keys=True, ensure_ascii=False) if isinstance(item,(dict,list)) else str(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def clean_object(obj):
    if isinstance(obj, dict):
        cleaned = {}
        for k,v in obj.items():
            cleaned[k] = clean_object(v)
        return cleaned

    if isinstance(obj, list):
        return deduplicate_list([clean_object(x) for x in obj])

    if isinstance(obj, str):
        return clean_string(obj)

    return obj

print("="*60)
print("HERITAGEGPT DATA CLEANER")
print("="*60)

for root,_,files in os.walk(DATASET_DIR):
    for file in files:

        if not file.endswith(".json"):
            continue

        path = os.path.join(root,file)
        dataset = os.path.splitext(file)[0]

        if os.path.getsize(path)==0:
            log_lines.append(f"{dataset}: skipped (empty file)")
            continue

        try:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            log_lines.append(f"{dataset}: skipped ({e})")
            continue

        cleaned = clean_object(deepcopy(data))

        out_file = os.path.join(OUTPUT_DIR,file)

        with open(out_file,"w",encoding="utf-8") as f:
            json.dump(cleaned,f,indent=4,ensure_ascii=False)

        count = len(cleaned) if isinstance(cleaned,list) else 1
        print(f"✔ {dataset:20} -> {count} records cleaned")
        log_lines.append(f"{dataset}: cleaned ({count} records)")

log_path = os.path.join(LOG_DIR,"clean_data_report.txt")
with open(log_path,"w",encoding="utf-8") as f:
    f.write("\n".join(log_lines))

print("\nCleaning completed.")
print(f"Cleaned datasets : {OUTPUT_DIR}")
print(f"Report           : {log_path}")
