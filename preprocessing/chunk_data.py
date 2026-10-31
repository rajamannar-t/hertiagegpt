import csv
import html
import json
import re
from pathlib import Path

from docx import Document as WordDocument
from pypdf import PdfReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


# chunk_data.py is inside HeritageGPT/preprocessing/
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

# Input files are expected in HeritageGPT/datasets/
INPUT_DIR = PROJECT_DIR / "datasets"

# Generated files are saved in HeritageGPT/preprocessing/chunks/
OUTPUT_DIR = BASE_DIR / "chunks"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SUPPORTED_FORMATS = {".json", ".txt", ".csv", ".pdf", ".docx"}


def clean_text(value):
    """Convert values to readable text and normalize whitespace."""
    if value is None:
        return ""
    value = html.unescape(str(value))
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def split_text(text):
    """Split text into overlapping character-based chunks."""
    text = text.strip()
    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        if end < len(text):
            boundary = text.rfind(" ", start, end)
            if boundary > start:
                end = boundary

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(start + 1, end - CHUNK_OVERLAP)

    return chunks


def read_json(path):
    """Read JSON and convert it to text while preserving its information."""
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)
    return json.dumps(data, ensure_ascii=False, indent=2)


def read_txt(path):
    return path.read_text(encoding="utf-8-sig")


def read_csv(path):
    """Convert CSV rows into readable text, retaining column names."""
    rows_as_text = []
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            parts = [
                f"{key}: {value}"
                for key, value in row.items()
                if key and value is not None and str(value).strip()
            ]
            if parts:
                rows_as_text.append(" | ".join(parts))
    return "\n".join(rows_as_text)


def read_pdf(path):
    """Extract selectable text from PDF pages; scanned PDFs may need OCR."""
    reader = PdfReader(str(path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        if page_text.strip():
            pages.append(f"Page {page_number}\n{page_text}")

    return "\n\n".join(pages)


def read_docx(path):
    """Extract paragraphs and table rows from a DOCX document."""
    document = WordDocument(str(path))
    parts = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            parts.append(paragraph.text)

    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))

    return "\n".join(parts)


READERS = {
    ".json": read_json,
    ".txt": read_txt,
    ".csv": read_csv,
    ".pdf": read_pdf,
    ".docx": read_docx,
}


def write_json(output_path, chunks, source_name):
    records = [
        {
            "chunk_id": f"{source_name}_{index:04d}",
            "source_file": source_name,
            "chunk_index": index,
            "text": chunk,
        }
        for index, chunk in enumerate(chunks, start=1)
    ]
    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_txt(output_path, chunks, source_name):
    with output_path.open("w", encoding="utf-8") as file:
        for index, chunk in enumerate(chunks, start=1):
            file.write(f"Source file: {source_name}\n")
            file.write(f"Chunk: {index}\n\n")
            file.write(chunk)
            file.write("\n\n" + "=" * 60 + "\n\n")


def write_csv(output_path, chunks, source_name):
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        fields = ["chunk_id", "source_file", "chunk_index", "text"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for index, chunk in enumerate(chunks, start=1):
            writer.writerow({
                "chunk_id": f"{source_name}_{index:04d}",
                "source_file": source_name,
                "chunk_index": index,
                "text": chunk,
            })


def write_docx(output_path, chunks, source_name):
    document = WordDocument()
    document.add_heading(f"Chunks from {source_name}", level=1)

    for index, chunk in enumerate(chunks, start=1):
        document.add_heading(f"Chunk {index}", level=2)
        document.add_paragraph(chunk)

    document.save(str(output_path))


def write_pdf(output_path, chunks, source_name):
    styles = getSampleStyleSheet()
    story = [Paragraph(f"Chunks from {source_name}", styles["Title"])]
    story.append(Spacer(1, 0.2 * inch))

    for index, chunk in enumerate(chunks, start=1):
        story.append(Paragraph(f"Chunk {index}", styles["Heading2"]))
        safe_text = (
            html.escape(chunk)
            .replace("\n", "<br/>")
        )
        story.append(Paragraph(safe_text, styles["BodyText"]))
        story.append(Spacer(1, 0.15 * inch))

    SimpleDocTemplate(str(output_path)).build(story)


WRITERS = {
    ".json": write_json,
    ".txt": write_txt,
    ".csv": write_csv,
    ".docx": write_docx,
    ".pdf": write_pdf,
}


def process_file(input_path):
    extension = input_path.suffix.lower()

    try:
        text = READERS[extension](input_path)
        text = text.strip()

        if not text:
            print(f"SKIPPED (no extractable text): {input_path}")
            return 0

        chunks = split_text(text)
        output_path = OUTPUT_DIR / f"{input_path.stem}_chunks{extension}"

        WRITERS[extension](output_path, chunks, input_path.name)

        print(
            f"SUCCESS: {input_path.name} -> {output_path.name} "
            f"({len(chunks)} chunks)"
        )
        return len(chunks)

    except Exception as error:
        print(f"ERROR processing {input_path.name}: {error}")
        return 0


def main():
    print("=" * 60)
    print("HERITAGEGPT UNIVERSAL CHUNK GENERATOR")
    print("=" * 60)
    print(f"Project folder : {PROJECT_DIR}")
    print(f"Input folder   : {INPUT_DIR}")
    print(f"Output folder  : {OUTPUT_DIR}")

    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Input folder not found: {INPUT_DIR}\n"
            "Create a 'datasets' folder in your HeritageGPT project root "
            "and put your source files inside it."
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Search recursively, but avoid reprocessing generated chunk files.
    input_files = [
        path for path in INPUT_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_FORMATS
        and not path.stem.endswith("_chunks")
    ]

    if not input_files:
        print("No supported input files found.")
        print("Supported formats: JSON, TXT, CSV, PDF, DOCX")
        return

    total_chunks = 0
    for input_path in input_files:
        total_chunks += process_file(input_path)

    print("-" * 60)
    print(f"Files found       : {len(input_files)}")
    print(f"Total chunks made : {total_chunks}")
    print(f"Output directory  : {OUTPUT_DIR}")
    print("Finished.")


if __name__ == "__main__":
    main()
