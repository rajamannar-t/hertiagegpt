


import csv
import html
import json
import re
from copy import deepcopy
from pathlib import Path

from docx import Document as WordDocument
from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DATASET_DIR = PROJECT_ROOT / "datasets"
OUTPUT_DIR = BASE_DIR / "cleaned_data"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "clean_data_report.txt"

SUPPORTED_EXTENSIONS = {".json", ".txt", ".csv", ".pdf", ".docx"}

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

log_lines = []


def clean_string(value):
    """Normalize whitespace and common punctuation spacing in a string."""
    if not isinstance(value, str):
        return value

    value = html.unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    value = value.replace(" ,", ",").replace(" .", ".")
    return value


def deduplicate_list(items):
    """Remove duplicate list items while preserving their original order."""
    seen = set()
    result = []

    for item in items:
        try:
            key = json.dumps(
                item, sort_keys=True, ensure_ascii=False
            ) if isinstance(item, (dict, list)) else str(item)
        except (TypeError, ValueError):
            key = repr(item)

        if key not in seen:
            seen.add(key)
            result.append(item)

    return result


def clean_object(obj):
    """Recursively clean JSON strings and remove duplicate list items."""
    if isinstance(obj, dict):
        return {key: clean_object(value) for key, value in obj.items()}

    if isinstance(obj, list):
        return deduplicate_list([clean_object(item) for item in obj])

    if isinstance(obj, str):
        return clean_string(obj)

    return obj


def clean_text(text):
    """Clean extracted text without collapsing meaningful line breaks."""
    text = html.unescape(text or "")
    lines = []

    for line in text.splitlines():
        line = re.sub(r"[ \t]+", " ", line).strip()
        line = line.replace(" ,", ",").replace(" .", ".")
        if line:
            lines.append(line)

    return "\n".join(lines)


def clean_json_file(source_path, output_path):
    with source_path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    cleaned = clean_object(deepcopy(data))

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(cleaned, file, indent=4, ensure_ascii=False)

    count = len(cleaned) if isinstance(cleaned, list) else 1
    return f"{count} JSON record(s)"


def clean_txt_file(source_path, output_path):
    text = source_path.read_text(encoding="utf-8-sig")
    output_path.write_text(clean_text(text), encoding="utf-8")
    return f"{len(text)} characters read"


def clean_csv_file(source_path, output_path):
    """Clean CSV cell strings and remove duplicate data rows."""
    with source_path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as source:
        reader = csv.reader(source)
        rows = list(reader)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return "empty CSV"

    cleaned_rows = []
    for row_index, row in enumerate(rows):
        cleaned_row = [
            clean_string(cell) if isinstance(cell, str) else cell
            for cell in row
        ]

        # Preserve the header. Deduplicate only data rows.
        if row_index == 0:
            cleaned_rows.append(cleaned_row)
        elif cleaned_row not in cleaned_rows[1:]:
            cleaned_rows.append(cleaned_row)

    with output_path.open(
        "w", encoding="utf-8-sig", newline=""
    ) as destination:
        writer = csv.writer(destination)
        writer.writerows(cleaned_rows)

    return f"{max(len(cleaned_rows) - 1, 0)} data row(s)"


def extract_pdf_text(source_path):
    reader = PdfReader(str(source_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(f"Page {page_number}\n{page_text}")

    return "\n\n".join(pages)


def clean_pdf_file(source_path, output_path):
    text = clean_text(extract_pdf_text(source_path))

    if not text:
        raise ValueError(
            "No selectable text found. If this is a scanned PDF, run OCR first."
        )

    styles = getSampleStyleSheet()
    story = []

    for paragraph_text in text.split("\n"):
        if paragraph_text.strip():
            safe_text = (
                paragraph_text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            story.append(Paragraph(safe_text, styles["BodyText"]))
            story.append(Spacer(1, 6))

    SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        title=f"Cleaned {source_path.stem}",
    ).build(story)

    return f"{len(text)} extracted characters"


def clean_docx_file(source_path, output_path):
    source_doc = WordDocument(str(source_path))
    cleaned_doc = WordDocument()

    # Preserve paragraph text and basic paragraph ordering.
    for paragraph in source_doc.paragraphs:
        text = clean_string(paragraph.text)
        if text:
            cleaned_doc.add_paragraph(text, style=paragraph.style.name)

    # Preserve tables as tables and clean each cell.
    for source_table in source_doc.tables:
        rows = len(source_table.rows)
        cols = len(source_table.columns)
        target_table = cleaned_doc.add_table(
            rows=rows,
            cols=cols,
        )

        try:
            target_table.style = source_table.style.name
        except (ValueError, AttributeError):
            pass

        for row_index, row in enumerate(source_table.rows):
            for col_index, cell in enumerate(row.cells):
                target_table.cell(row_index, col_index).text = (
                    clean_string(cell.text) or ""
                )

    cleaned_doc.save(str(output_path))
    return (
        f"{len(source_doc.paragraphs)} paragraph(s), "
        f"{len(source_doc.tables)} table(s)"
    )


CLEANERS = {
    ".json": clean_json_file,
    ".txt": clean_txt_file,
    ".csv": clean_csv_file,
    ".pdf": clean_pdf_file,
    ".docx": clean_docx_file,
}


def main():
    print("=" * 60)
    print("HERITAGEGPT MULTI-FORMAT DATA CLEANER")
    print("=" * 60)
    print(f"Project root : {PROJECT_ROOT}")
    print(f"Input folder : {DATASET_DIR}")
    print(f"Output folder: {OUTPUT_DIR}")

    if not DATASET_DIR.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {DATASET_DIR}\n"
            "Create a 'datasets' folder in your HeritageGPT project root "
            "and place your source files there."
        )

    files = [
        path for path in DATASET_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        print("\nNo supported files found.")
        print("Supported formats: JSON, TXT, CSV, PDF, DOCX")
        return

    success_count = 0
    failure_count = 0

    for source_path in files:
        relative_path = source_path.relative_to(DATASET_DIR)
        output_path = OUTPUT_DIR / relative_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Avoid accidentally processing output files if folders overlap.
        try:
            result = CLEANERS[source_path.suffix.lower()](
                source_path, output_path
            )
            message = (
                f"SUCCESS: {relative_path} -> "
                f"{output_path.relative_to(OUTPUT_DIR)} ({result})"
            )
            print(message)
            log_lines.append(message)
            success_count += 1

        except Exception as error:
            message = f"FAILED: {relative_path} ({type(error).__name__}: {error})"
            print(message)
            log_lines.append(message)
            failure_count += 1

    report = [
        "HERITAGEGPT DATA CLEANING REPORT",
        f"Input folder: {DATASET_DIR}",
        f"Output folder: {OUTPUT_DIR}",
        f"Files found: {len(files)}",
        f"Successful: {success_count}",
        f"Failed: {failure_count}",
        "",
        *log_lines,
    ]
    LOG_FILE.write_text("\n".join(report), encoding="utf-8")

    print("\nCleaning completed.")
    print(f"Successful files: {success_count}")
    print(f"Failed files    : {failure_count}")
    print(f"Cleaned datasets: {OUTPUT_DIR}")
    print(f"Report          : {LOG_FILE}")


if __name__ == "__main__":
    main()
