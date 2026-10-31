"""
HeritageGPT - Multi-format dataset validator.

Scans HeritageGPT/datasets/ recursively and validates:
  - JSON: syntax, root shape, required HeritageGPT fields, record types,
          duplicate IDs, coordinate ranges, and empty values.
  - TXT: readability, UTF-8 decoding, non-empty content, and replacement chars.
  - CSV: readability, headers, row widths, empty rows/cells, duplicate rows.
  - PDF: readability, page count, extractable text, and empty pages.
  - DOCX: readability, paragraphs/tables, and non-empty content.

Reports are written to HeritageGPT/preprocessing/logs/.
The validator does not modify source datasets.
"""

import csv
import json
import logging
import os
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from colorama import Fore, init
    init(autoreset=True)
except ImportError:
    class _NoColor:
        def __getattr__(self, _name):
            return ""
    Fore = _NoColor()

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# ---------------------------------------------------------------------------
# Paths and configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATASET_FOLDER = PROJECT_ROOT / "datasets"
LOG_FOLDER = BASE_DIR / "logs"
LOG_FOLDER.mkdir(parents=True, exist_ok=True)

REPORT_FILE = LOG_FOLDER / "validation_report.txt"
JSON_REPORT_FILE = LOG_FOLDER / "validation_report.json"
LOG_FILE = LOG_FOLDER / "validate_data.log"

SUPPORTED_EXTENSIONS = {".json", ".txt", ".csv", ".pdf", ".docx"}

# Fields expected in the current flat Andhra Pradesh tourism dataset.
# Only core fields are errors when missing; descriptive/optional fields can be blank.
REQUIRED_FIELDS = [
    "id",
    "name",
    "latitude",
    "longitude",
    "tourism_type",
    "district",
]

OPTIONAL_FIELDS = [
    "subtitle",
    "town",
    "city",
    "pincode",
    "introduction",
    "overview",
    "significance",
    "how_to_reach",
    "highlights",
    "history",
    "best_time_to_visit",
    "best_time_to_visit_months",
    "categories",
    "experiences",
    "url",
    "meta_keywords",
    "meta_description",
    "weather",
    "cover_images",
    "gallery_images",
    "snippet_image",
    "near_by_places",
    "source",
    "source_url",
]

LATITUDE_KEYS = {"latitude", "lat"}
LONGITUDE_KEYS = {"longitude", "lon", "lng"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("heritage_validator")


def print_color(color: str, message: str) -> None:
    print(f"{color}{message}")


def new_report(relative_path: str) -> dict[str, Any]:
    return {
        "dataset": relative_path,
        "format": Path(relative_path).suffix.lower().lstrip(".").upper(),
        "status": "PASSED",
        "records": 0,
        "warnings": [],
        "errors": [],
        "notes": [],
    }


def add_error(report: dict[str, Any], message: str) -> None:
    report["errors"].append(message)
    report["status"] = "FAILED"


def add_warning(report: dict[str, Any], message: str) -> None:
    report["warnings"].append(message)


def add_note(report: dict[str, Any], message: str) -> None:
    report["notes"].append(message)


def check_empty_values(obj: Any, path: str, report: dict[str, Any]) -> None:
    """Warn on empty/null values without treating them automatically as errors."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else str(key)
            check_empty_values(value, child_path, report)
    elif isinstance(obj, list):
        if not obj:
            add_warning(report, f"Empty list: {path or '<root>'}")
        else:
            for index, item in enumerate(obj):
                check_empty_values(item, f"{path}[{index}]", report)
    elif obj is None:
        add_warning(report, f"Null value: {path}")
    elif isinstance(obj, str) and not obj.strip():
        add_warning(report, f"Empty string: {path}")


def find_coordinates(obj: Any, path: str = ""):
    """Yield (key, value, path) for latitude/longitude-like fields anywhere."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = str(key).lower()
            child_path = f"{path}.{key}" if path else str(key)
            if key_lower in LATITUDE_KEYS or key_lower in LONGITUDE_KEYS:
                yield key_lower, value, child_path
            if isinstance(value, (dict, list)):
                yield from find_coordinates(value, child_path)
    elif isinstance(obj, list):
        for index, item in enumerate(obj):
            yield from find_coordinates(item, f"{path}[{index}]")


def validate_coordinate_values(record: dict[str, Any], record_label: str,
                               report: dict[str, Any]) -> None:
    """Validate coordinate values supplied as numbers or numeric strings."""
    for key, value, path in find_coordinates(record):
        if value is None or (isinstance(value, str) and not value.strip()):
            add_warning(report, f"{record_label}: coordinate '{path}' is empty.")
            continue

        if isinstance(value, bool):
            add_error(report, f"{record_label}: coordinate '{path}' must be numeric.")
            continue

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            add_error(report, f"{record_label}: coordinate '{path}' must be numeric.")
            continue

        if key in LATITUDE_KEYS and not -90 <= numeric_value <= 90:
            add_error(report, f"{record_label}: invalid latitude at '{path}': {value}")
        if key in LONGITUDE_KEYS and not -180 <= numeric_value <= 180:
            add_error(report, f"{record_label}: invalid longitude at '{path}': {value}")


def validate_json(path: Path, report: dict[str, Any]) -> None:
    if path.stat().st_size == 0:
        report["status"] = "NOT STARTED"
        add_error(report, "Dataset file is empty.")
        return

    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        add_error(
            report,
            f"Invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}",
        )
        return
    except UnicodeDecodeError as exc:
        add_error(report, f"File is not valid UTF-8 text: {exc}")
        return
    except OSError as exc:
        add_error(report, f"Could not read file: {exc}")
        return

    if not isinstance(data, list):
        add_error(report, "Root element must be a JSON array of records.")
        return

    ids = []
    for index, record in enumerate(data, start=1):
        report["records"] += 1
        label = f"Record {index}"

        if not isinstance(record, dict):
            add_error(report, f"{label}: each record must be a JSON object, not "
                              f"{type(record).__name__}.")
            continue

        rid = record.get("id", f"Record-{index}")
        label = f"Record {index} (id={rid})"

        if "id" in record and record["id"] is not None:
            ids.append(str(record["id"]))
        else:
            add_error(report, f"{label}: missing or null 'id' field.")

        for field in REQUIRED_FIELDS:
            if field not in record:
                add_error(report, f"{label}: missing required field '{field}'.")
            elif record[field] is None:
                add_error(report, f"{label}: required field '{field}' is null.")
            elif isinstance(record[field], str) and not record[field].strip():
                add_error(report, f"{label}: required field '{field}' is empty.")

        # IDs should be present and usable; numeric or non-empty string IDs are okay.
        if "id" in record and record["id"] is not None:
            if isinstance(record["id"], (dict, list, bool)):
                add_error(report, f"{label}: 'id' must be a number or non-empty string.")

        # The current dataset stores latitude/longitude at the record's top level.
        # Validate their numeric content and legal ranges even when they are strings.
        validate_coordinate_values(record, label, report)

        # Empty optional fields are warnings, not schema errors.
        check_empty_values(record, "", report)


    duplicates = [item for item, count in Counter(ids).items() if count > 1]
    for duplicate in duplicates:
        add_error(report, f"Duplicate record ID: {duplicate}")

    if not data:
        add_warning(report, "JSON array contains no records.")


def validate_txt(path: Path, report: dict[str, Any]) -> None:
    try:
        with path.open("r", encoding="utf-8-sig", errors="replace") as handle:
            content = handle.read()
    except OSError as exc:
        add_error(report, f"Could not read text file: {exc}")
        return

    if path.stat().st_size == 0 or not content.strip():
        report["status"] = "NOT STARTED"
        add_error(report, "Text file is empty or contains only whitespace.")
        return

    if "\ufffd" in content:
        add_warning(report, "Text contains Unicode replacement characters; "
                            "check the source encoding.")
    lines = content.splitlines()
    report["records"] = len([line for line in lines if line.strip()])
    if not lines:
        add_warning(report, "No lines found.")
    add_note(report, f"Lines: {len(lines)}; non-empty lines: {report['records']}.")


def validate_csv(path: Path, report: dict[str, Any]) -> None:
    if path.stat().st_size == 0:
        report["status"] = "NOT STARTED"
        add_error(report, "CSV file is empty.")
        return

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            sample = handle.read(8192)
            handle.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample) if sample.strip() else csv.excel
            except csv.Error:
                dialect = csv.excel
            reader = csv.reader(handle, dialect)
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        add_error(report, f"Could not parse CSV: {exc}")
        return

    if not rows:
        report["status"] = "NOT STARTED"
        add_error(report, "CSV contains no rows.")
        return

    headers = [cell.strip() for cell in rows[0]]
    if not any(headers):
        add_error(report, "CSV header row is empty.")
        return

    if len(headers) != len(set(headers)):
        add_warning(report, "CSV contains duplicate column names.")

    if any(not header for header in headers):
        add_warning(report, "CSV contains one or more blank column names.")

    expected_width = len(headers)
    data_rows = rows[1:]
    report["records"] = len(data_rows)

    normalized_rows = set()
    for row_number, row in enumerate(data_rows, start=2):
        if not any(cell.strip() for cell in row):
            add_warning(report, f"Row {row_number} is empty.")
            continue
        if len(row) != expected_width:
            add_error(
                report,
                f"Row {row_number} has {len(row)} columns; expected {expected_width}.",
            )
        if any(not cell.strip() for cell in row):
            add_warning(report, f"Row {row_number} contains empty cells.")
        normalized = tuple(cell.strip() for cell in row)
        if normalized in normalized_rows:
            add_warning(report, f"Duplicate data row found at row {row_number}.")
        normalized_rows.add(normalized)

    if not data_rows:
        add_warning(report, "CSV has a header but no data rows.")
    add_note(report, f"Columns: {len(headers)}; data rows: {len(data_rows)}.")


def validate_pdf(path: Path, report: dict[str, Any]) -> None:
    if PdfReader is None:
        add_error(report, "PDF validation unavailable. Install dependency: "
                          "python -m pip install pypdf")
        return
    if path.stat().st_size == 0:
        report["status"] = "NOT STARTED"
        add_error(report, "PDF file is empty.")
        return

    try:
        reader = PdfReader(str(path))
        if reader.is_encrypted:
            try:
                result = reader.decrypt("")
            except Exception:
                result = 0
            if not result:
                add_error(report, "PDF is encrypted and cannot be opened without a password.")
                return

        page_count = len(reader.pages)
        report["records"] = page_count
        if page_count == 0:
            add_error(report, "PDF contains no pages.")
            return

        pages_with_text = 0
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = (page.extract_text() or "").strip()
            except Exception as exc:
                add_warning(report, f"Could not extract text from page {page_number}: {exc}")
                continue
            if text:
                pages_with_text += 1
            else:
                add_warning(report, f"Page {page_number} contains no extractable text.")

        if pages_with_text == 0:
            add_warning(report, "No selectable text found. If this is a scanned PDF, "
                                "OCR is required for text validation.")
        add_note(report, f"Pages: {page_count}; pages with extractable text: "
                         f"{pages_with_text}.")
    except Exception as exc:
        add_error(report, f"PDF is unreadable or malformed: {exc}")


def validate_docx(path: Path, report: dict[str, Any]) -> None:
    if Document is None:
        add_error(report, "DOCX validation unavailable. Install dependency: "
                          "python -m pip install python-docx")
        return
    if path.stat().st_size == 0:
        report["status"] = "NOT STARTED"
        add_error(report, "DOCX file is empty.")
        return

    try:
        document = Document(str(path))
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        table_rows = 0
        nonempty_table_rows = 0
        for table in document.tables:
            for row in table.rows:
                table_rows += 1
                if any(cell.text.strip() for cell in row.cells):
                    nonempty_table_rows += 1

        report["records"] = len(paragraphs) + nonempty_table_rows
        if not paragraphs and nonempty_table_rows == 0:
            add_warning(report, "DOCX opens successfully but contains no extractable "
                                "paragraph or table text.")
        add_note(
            report,
            f"Non-empty paragraphs: {len(paragraphs)}; tables: {len(document.tables)}; "
            f"non-empty table rows: {nonempty_table_rows}/{table_rows}.",
        )
    except Exception as exc:
        add_error(report, f"DOCX is unreadable or malformed: {exc}")


VALIDATORS = {
    ".json": validate_json,
    ".txt": validate_txt,
    ".csv": validate_csv,
    ".pdf": validate_pdf,
    ".docx": validate_docx,
}


def write_reports(reports: dict[str, dict[str, Any]], summary: dict[str, int],
                  total_records: int, total_errors: int, total_warnings: int) -> None:
    with REPORT_FILE.open("w", encoding="utf-8") as handle:
        handle.write("=" * 78 + "\n")
        handle.write("HERITAGEGPT MULTI-FORMAT VALIDATION REPORT\n")
        handle.write("=" * 78 + "\n\n")

        for relative_path, info in reports.items():
            handle.write("=" * 78 + "\n")
            handle.write(f"DATASET: {relative_path}\n")
            handle.write("=" * 78 + "\n")
            handle.write(f"Format  : {info['format']}\n")
            handle.write(f"Status  : {info['status']}\n")
            handle.write(f"Records : {info['records']}\n\n")

            handle.write("Errors\n" + "-" * 40 + "\n")
            if info["errors"]:
                for message in info["errors"]:
                    handle.write(f"- {message}\n")
            else:
                handle.write("No errors.\n")

            handle.write("\nWarnings\n" + "-" * 40 + "\n")
            if info["warnings"]:
                for message in info["warnings"]:
                    handle.write(f"- {message}\n")
            else:
                handle.write("No warnings.\n")

            if info["notes"]:
                handle.write("\nNotes\n" + "-" * 40 + "\n")
                for message in info["notes"]:
                    handle.write(f"- {message}\n")
            handle.write("\n")

        handle.write("=" * 78 + "\nSUMMARY\n")
        handle.write("=" * 78 + "\n")
        handle.write(f"Passed       : {summary['passed']}\n")
        handle.write(f"Failed       : {summary['failed']}\n")
        handle.write(f"Not Started  : {summary['not_started']}\n")
        handle.write(f"Files        : {len(reports)}\n")
        handle.write(f"Records      : {total_records}\n")
        handle.write(f"Errors       : {total_errors}\n")
        handle.write(f"Warnings     : {total_warnings}\n")

    payload = {
        "summary": {
            **summary,
            "files": len(reports),
            "records": total_records,
            "errors": total_errors,
            "warnings": total_warnings,
        },
        "datasets": list(reports.values()),
    }
    with JSON_REPORT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def main() -> int:
    print_color(Fore.CYAN, "=" * 70)
    print_color(Fore.CYAN, "HERITAGEGPT MULTI-FORMAT DATA VALIDATOR")
    print_color(Fore.CYAN, "=" * 70)

    if not DATASET_FOLDER.exists():
        print_color(Fore.RED, f"Dataset folder not found: {DATASET_FOLDER}")
        logger.error("Dataset folder not found: %s", DATASET_FOLDER)
        return 2

    files = sorted(
        path for path in DATASET_FOLDER.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        # Avoid accidentally validating temporary Microsoft Office lock files.
        and not path.name.startswith("~$")
    )

    if not files:
        print_color(Fore.YELLOW, f"No supported files found in {DATASET_FOLDER}")
        logger.warning("No supported dataset files found.")
        return 2

    reports: dict[str, dict[str, Any]] = {}
    summary = {"passed": 0, "failed": 0, "not_started": 0}
    total_records = 0

    for path in files:
        relative_path = str(path.relative_to(DATASET_FOLDER)).replace("\\", "/")
        report = new_report(relative_path)
        reports[relative_path] = report

        print_color(Fore.CYAN, f"Checking: {relative_path}")
        logger.info("Validating %s", relative_path)

        try:
            VALIDATORS[path.suffix.lower()](path, report)
        except Exception as exc:
            # One problematic file should not stop validation of other datasets.
            add_error(report, f"Unexpected validation error: {type(exc).__name__}: {exc}")
            logger.exception("Unexpected error validating %s", relative_path)

        if report["status"] == "NOT STARTED":
            summary["not_started"] += 1
        elif report["errors"]:
            report["status"] = "FAILED"
            summary["failed"] += 1
        else:
            report["status"] = "PASSED"
            summary["passed"] += 1

        total_records += report["records"]

        status_color = Fore.GREEN if report["status"] == "PASSED" else Fore.RED
        if report["status"] == "NOT STARTED":
            status_color = Fore.YELLOW
        print_color(status_color, f"  {report['status']} | records/pages/rows: {report['records']}")

    total_errors = sum(len(item["errors"]) for item in reports.values())
    total_warnings = sum(len(item["warnings"]) for item in reports.values())
    write_reports(reports, summary, total_records, total_errors, total_warnings)

    print_color(Fore.CYAN, "\n" + "=" * 70)
    print_color(Fore.CYAN, "VALIDATION SUMMARY")
    print_color(Fore.GREEN, f"Passed      : {summary['passed']}")
    print_color(Fore.RED, f"Failed      : {summary['failed']}")
    print_color(Fore.YELLOW, f"Not Started : {summary['not_started']}")
    print(f"Files       : {len(reports)}")
    print(f"Records     : {total_records}")
    print(f"Errors      : {total_errors}")
    print(f"Warnings    : {total_warnings}")
    print_color(Fore.GREEN, f"\nText report : {REPORT_FILE}")
    print_color(Fore.GREEN, f"JSON report : {JSON_REPORT_FILE}")
    print_color(Fore.GREEN, f"Log file    : {LOG_FILE}")

    # Non-zero exit code helps automation/CI identify failed validation.
    return 1 if summary["failed"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
