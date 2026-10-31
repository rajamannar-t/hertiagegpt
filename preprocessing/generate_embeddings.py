

import csv
import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from docx import Document
except ImportError:
    Document = None


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

CHUNKS_DIR = BASE_DIR / "chunks"
LOG_DIR = BASE_DIR / "logs"
DB_DIR = PROJECT_ROOT / "vector_db" / "chroma_db"

CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
DB_DIR.mkdir(parents=True, exist_ok=True)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# SAFETY: keep the test collection until you confirm the production collection
# name. This script does not delete existing collection records.
COLLECTION_NAME = "heritage_combined_test"

BATCH_SIZE = 64
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SUPPORTED_EXTENSIONS = {".json", ".txt", ".csv", ".pdf", ".docx"}

LOG_FILE = LOG_DIR / "generate_embeddings.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Text and chunk helpers
# ---------------------------------------------------------------------------
def clean_text(value: Any) -> str:
    """Convert a value to clean, searchable text."""
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    value = value.replace("\x00", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def split_text(text: str, chunk_size: int = CHUNK_SIZE,
               overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping character chunks."""
    text = clean_text(text)
    if not text:
        return []
    if chunk_size <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero.")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("CHUNK_OVERLAP must be >= 0 and less than CHUNK_SIZE.")

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        part = text[start:end].strip()
        if part:
            chunks.append(part)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def stable_id(source_relative: str, index: int, text: str) -> str:
    """Return a stable ID so reruns update matching records rather than duplicate."""
    digest = hashlib.sha256(
        f"{source_relative}|{index}|{text}".encode("utf-8")
    ).hexdigest()[:20]
    return f"hg_{digest}"


def metadata_value(value: Any, max_length: int = 1000) -> str:
    """Chroma metadata values must be scalar; normalize values to strings."""
    if value is None:
        return ""
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False)
    return clean_text(value)[:max_length]


def make_record(text: str, source_relative: str, index: int,
                original: dict[str, Any] | None = None) -> dict[str, Any]:
    original = original or {}
    source_name = Path(source_relative).name
    return {
        "chunk_id": clean_text(original.get("chunk_id")) or stable_id(
            source_relative, index, text
        ),
        "text": text,
        "record_id": metadata_value(original.get("record_id", "")),
        "category": metadata_value(original.get("category", "")),
        "title": metadata_value(original.get("title", source_name)),
        "district": metadata_value(original.get("district", "")),
        "source": metadata_value(original.get("source", source_relative)),
        "source_url": metadata_value(original.get("source_url", "")),
        "source_file": metadata_value(source_relative),
        "chunk_index": index,
    }


def records_from_json(data: Any, source_relative: str) -> list[dict[str, Any]]:
    """Support a list of existing chunk records, a single record, or nested JSON."""
    records: list[dict[str, Any]] = []

    if isinstance(data, dict) and isinstance(data.get("chunks"), list):
        data = data["chunks"]

    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        # A record-like object containing text/content/title fields.
        if any(k in data for k in ("text", "content", "description", "body")):
            items = [data]
        else:
            # Preserve nested objects as readable JSON text.
            items = [{"title": key, "text": value} for key, value in data.items()]
    else:
        items = [{"text": data}]

    for item_index, item in enumerate(items):
        if isinstance(item, dict):
            text_value = next(
                (item.get(k) for k in ("text", "content", "description", "body")
                 if item.get(k) not in (None, "")),
                None,
            )
            if text_value is None:
                # Turn a structured object into searchable text.
                text_value = " | ".join(
                    f"{key}: {value}" for key, value in item.items()
                    if value not in (None, "")
                )
            text = clean_text(text_value)
            metadata_source = item
        else:
            text = clean_text(item)
            metadata_source = {}

        if not text:
            continue

        # Existing chunks stay intact. Longer records are split if needed.
        parts = [text] if len(text) <= CHUNK_SIZE else split_text(text)
        for part_index, part in enumerate(parts):
            index = item_index if len(parts) == 1 else item_index * 100000 + part_index
            records.append(make_record(part, source_relative, index, metadata_source))

    return records


def read_plain_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def read_csv_text(path: Path) -> str:
    """Render each CSV row as labeled text, including column headers."""
    lines = []
    with path.open("r", encoding="utf-8-sig", newline="", errors="replace") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames:
            for row_number, row in enumerate(reader, start=1):
                fields = [
                    f"{clean_text(key)}: {clean_text(value)}"
                    for key, value in row.items()
                    if key and clean_text(value)
                ]
                if fields:
                    lines.append(f"Row {row_number}. " + "; ".join(fields))
        else:
            handle.seek(0)
            for row in csv.reader(handle):
                values = [clean_text(cell) for cell in row if clean_text(cell)]
                if values:
                    lines.append(" | ".join(values))
    return "\n".join(lines)


def read_pdf_text(path: Path) -> str:
    if PdfReader is None:
        raise RuntimeError("PDF support requires pypdf. Install it with: "
                           "python -m pip install pypdf")
    reader = PdfReader(str(path))
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = clean_text(page.extract_text() or "")
        if text:
            pages.append(f"Page {page_number}: {text}")
    if not pages:
        logger.warning(
            "No selectable text extracted from %s. Scanned PDFs require OCR.",
            path.name,
        )
    return "\n".join(pages)


def read_docx_text(path: Path) -> str:
    if Document is None:
        raise RuntimeError("DOCX support requires python-docx. Install it with: "
                           "python -m pip install python-docx")
    doc = Document(str(path))
    parts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            cells = [clean_text(cell.text) for cell in row.cells]
            if any(cells):
                parts.append(" | ".join(cells))
    return "\n".join(parts)


def load_file(path: Path) -> list[dict[str, Any]]:
    relative = str(path.relative_to(CHUNKS_DIR)).replace("\\", "/")
    suffix = path.suffix.lower()

    if suffix == ".json":
        with path.open("r", encoding="utf-8-sig") as handle:
            return records_from_json(json.load(handle), relative)

    if suffix == ".txt":
        raw_text = read_plain_text(path)
    elif suffix == ".csv":
        raw_text = read_csv_text(path)
    elif suffix == ".pdf":
        raw_text = read_pdf_text(path)
    elif suffix == ".docx":
        raw_text = read_docx_text(path)
    else:
        return []

    return [
        make_record(text, relative, index, {"title": path.stem})
        for index, text in enumerate(split_text(raw_text))
    ]


def discover_files() -> list[Path]:
    return sorted(
        path for path in CHUNKS_DIR.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and not path.name.startswith("~$")
    )


# ---------------------------------------------------------------------------
# Embedding and ChromaDB
# ---------------------------------------------------------------------------
def main() -> None:
    files = discover_files()
    if not files:
        raise FileNotFoundError(
            f"No supported files found in {CHUNKS_DIR}\n"
            f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    all_records: list[dict[str, Any]] = []
    for path in files:
        try:
            records = load_file(path)
            all_records.extend(records)
            logger.info("Read %s: %s text chunks", path.name, len(records))
        except Exception:
            logger.exception("Skipping file due to read/parse error: %s", path)

    if not all_records:
        raise ValueError(
            "No usable text chunks were found. Check the input files and logs."
        )

    # Resolve ID collisions within this run. If the same ID appears twice,
    # keep the first record and warn rather than accidentally overwriting it.
    unique_records: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for record in all_records:
        chunk_id = record["chunk_id"]
        if chunk_id in seen_ids:
            logger.warning("Duplicate chunk_id '%s'; skipping duplicate.", chunk_id)
            continue
        seen_ids.add(chunk_id)
        unique_records.append(record)

    logger.info("Total unique chunks to embed: %s", len(unique_records))
    logger.info("Loading embedding model: %s", MODEL_NAME)
    model = SentenceTransformer(MODEL_NAME)

    client = chromadb.PersistentClient(path=str(DB_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "HeritageGPT multi-format text embeddings"},
        # Explicitly use cosine distance to match normalized embeddings.
        # If the collection already exists, its existing metadata is retained.
    )

    for start in range(0, len(unique_records), BATCH_SIZE):
        batch = unique_records[start:start + BATCH_SIZE]
        texts = [item["text"] for item in batch]
        ids = [item["chunk_id"] for item in batch]

        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        metadatas = []
        for item in batch:
            metadatas.append({
                "record_id": item["record_id"],
                "category": item["category"],
                "title": item["title"],
                "district": item["district"],
                "source": item["source"],
                "source_url": item["source_url"],
                "source_file": item["source_file"],
                "chunk_index": int(item["chunk_index"]),
            })

        # Upsert makes reruns idempotent for matching IDs; no collection-wide
        # delete is performed. New or changed IDs are added; stale old IDs stay.
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info(
            "Embedded %s / %s chunks",
            min(start + len(batch), len(unique_records)),
            len(unique_records),
        )

    logger.info("Embedding generation completed.")
    logger.info("Collection: %s", COLLECTION_NAME)
    logger.info("Input files discovered: %s", len(files))
    logger.info("Unique chunks processed: %s", len(unique_records))
    logger.info("Total vectors currently in collection: %s", collection.count())
    logger.info("Log file: %s", LOG_FILE)


if __name__ == "__main__":
    main()
