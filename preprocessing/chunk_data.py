
"""
chunk_data.py
HeritageGPT - JSON to RAG Chunk Converter
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLEAN_DIR = os.path.join(BASE_DIR, "cleaned_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "chunks")
LOG_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

MAX_CHUNK_SIZE = 800

logs = []

def record_to_text(record):
    lines = []
    for key, value in record.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        elif isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)

def split_text(text, size=MAX_CHUNK_SIZE):
    words = text.split()
    chunks = []
    current = []

    for word in words:
        current.append(word)
        if len(" ".join(current)) >= size:
            chunks.append(" ".join(current))
            current = []

    if current:
        chunks.append(" ".join(current))

    return chunks

print("=" * 60)
print("HERITAGEGPT CHUNK GENERATOR")
print("=" * 60)

for file in os.listdir(CLEAN_DIR):

    if not file.endswith(".json"):
        continue

    path = os.path.join(CLEAN_DIR, file)

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dataset_name = os.path.splitext(file)[0]
    output = []

    if not isinstance(data, list):
        data = [data]

    chunk_id = 1

    for record in data:

        text = record_to_text(record)
        chunks = split_text(text)

        for c in chunks:

            output.append({
                "chunk_id": f"{dataset_name.upper()}_{chunk_id:05d}",
                "record_id": record.get("id", ""),
                "category": dataset_name,
                "title": record.get("basic_information", {}).get("name", ""),
                "text": c,
                "metadata": {
                    "state": record.get("location", {}).get("state", ""),
                    "district": record.get("location", {}).get("district", "")
                }
            })

            chunk_id += 1

    out_path = os.path.join(OUTPUT_DIR, f"{dataset_name}_chunks.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

    print(f"✔ {dataset_name:20} -> {len(output)} chunks")
    logs.append(f"{dataset_name}: {len(output)} chunks")

log_file = os.path.join(LOG_DIR, "chunk_report.txt")

with open(log_file, "w", encoding="utf-8") as f:
    f.write("\n".join(logs))

print("\nChunk generation completed.")
print(f"Chunks : {OUTPUT_DIR}")
print(f"Report : {log_file}")
