
# validate_data.py
import os
import json
from collections import Counter
from colorama import Fore, init

init(autoreset=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATASET_FOLDER = os.path.join(PROJECT_ROOT, "datasets")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_FOLDER, exist_ok=True)

REQUIRED_FIELDS = [
    "id",
    "basic_information",
    "location",
    "history",
    "architecture",
    "tourism",
    "ai_metadata"
]

dataset_reports = {}

summary = {
    "passed": 0,
    "failed": 0,
    "not_started": 0
}

total_records = 0
total_errors = 0
total_warnings = 0


def add_error(dataset, msg):
    global total_errors
    dataset_reports[dataset]["errors"].append(msg)
    total_errors += 1


def add_warning(dataset, msg):
    global total_warnings
    dataset_reports[dataset]["warnings"].append(msg)
    total_warnings += 1


def check_empty(obj, path, dataset):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_empty(v, f"{path}.{k}" if path else k, dataset)

    elif isinstance(obj, list):
        if len(obj) == 0:
            add_warning(dataset, f"Empty List : {path}")
        else:
            for item in obj:
                check_empty(item, path, dataset)

    elif obj is None:
        add_warning(dataset, f"NULL Value : {path}")

    elif isinstance(obj, str) and obj.strip() == "":
        add_warning(dataset, f"Empty String : {path}")


print(Fore.CYAN + "=" * 70)
print(Fore.CYAN + "HERITAGEGPT DATA VALIDATOR")
print(Fore.CYAN + "=" * 70)

if not os.path.exists(DATASET_FOLDER):
    print(Fore.RED + "Dataset folder not found.")
    raise SystemExit

for root, _, files in os.walk(DATASET_FOLDER):

    for file in files:

        if not file.endswith(".json"):
            continue

        dataset = os.path.splitext(file)[0]

        dataset_reports[dataset] = {
            "status": "PASSED",
            "records": 0,
            "errors": [],
            "warnings": []
        }

        filepath = os.path.join(root, file)

        print(Fore.CYAN + f"Checking : {dataset}")

        if os.path.getsize(filepath) == 0:
            dataset_reports[dataset]["status"] = "NOT STARTED"
            dataset_reports[dataset]["errors"].append("Dataset file is empty.")
            summary["not_started"] += 1
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

        except json.JSONDecodeError as e:
            dataset_reports[dataset]["status"] = "FAILED"
            add_error(dataset, f"Invalid JSON (Line {e.lineno}, Column {e.colno})")
            summary["failed"] += 1
            continue

        if not isinstance(data, list):
            dataset_reports[dataset]["status"] = "FAILED"
            add_error(dataset, "Root element must be a JSON array.")
            summary["failed"] += 1
            continue

        ids = []

        for index, record in enumerate(data, start=1):

            total_records += 1
            dataset_reports[dataset]["records"] += 1

            rid = record.get("id", f"Record-{index}")
            ids.append(rid)

            for field in REQUIRED_FIELDS:
                if field not in record:
                    add_error(dataset, f"Record {index} : Missing field '{field}'")

            loc = record.get("location", {})
            if isinstance(loc, dict):

                lat = loc.get("latitude")
                lon = loc.get("longitude")

                if isinstance(lat, (int, float)) and not (-90 <= lat <= 90):
                    add_error(dataset, f"{rid} : Invalid Latitude")

                if isinstance(lon, (int, float)) and not (-180 <= lon <= 180):
                    add_error(dataset, f"{rid} : Invalid Longitude")

            check_empty(record, "", dataset)

        dup = [x for x, c in Counter(ids).items() if c > 1]

        for d in dup:
            add_error(dataset, f"Duplicate ID : {d}")

        if dataset_reports[dataset]["errors"]:
            dataset_reports[dataset]["status"] = "FAILED"
            summary["failed"] += 1
        else:
            summary["passed"] += 1

report_file = os.path.join(LOG_FOLDER, "validation_report.txt")

with open(report_file, "w", encoding="utf-8") as f:

    f.write("=" * 70 + "\n")
    f.write("HERITAGEGPT VALIDATION REPORT\n")
    f.write("=" * 70 + "\n\n")

    for dataset, info in dataset_reports.items():

        f.write("=" * 70 + "\n")
        f.write(f"DATASET : {dataset.upper()}\n")
        f.write("=" * 70 + "\n")
        f.write(f"Status  : {info['status']}\n")
        f.write(f"Records : {info['records']}\n\n")

        if info["errors"]:
            f.write("Errors\n")
            f.write("-" * 40 + "\n")
            for err in info["errors"]:
                f.write(f"• {err}\n")
        else:
            f.write("No Errors\n")

        if info["warnings"]:
            f.write("\nWarnings\n")
            f.write("-" * 40 + "\n")
            for w in info["warnings"]:
                f.write(f"• {w}\n")

        f.write("\n")

    f.write("=" * 70 + "\n")
    f.write("SUMMARY\n")
    f.write("=" * 70 + "\n")
    f.write(f"Passed       : {summary['passed']}\n")
    f.write(f"Failed       : {summary['failed']}\n")
    f.write(f"Not Started  : {summary['not_started']}\n")
    f.write(f"Records      : {total_records}\n")
    f.write(f"Errors       : {total_errors}\n")
    f.write(f"Warnings     : {total_warnings}\n")

print(Fore.GREEN + "\nValidation completed.")
print(Fore.GREEN + f"Report saved to: {report_file}")
