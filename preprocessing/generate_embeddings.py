"""
generate_embeddings.py
---------------------------------------------------
HeritageGPT - Embedding Generator

Reads chunked JSON files
Generates SentenceTransformer embeddings
Stores vectors in ChromaDB
Creates embedding report
---------------------------------------------------
"""

import json
import logging
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# ==================================================
# PROJECT PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

PROJECT_ROOT = BASE_DIR.parent

CHUNK_DIR = BASE_DIR / "chunks"

LOG_DIR = BASE_DIR / "logs"

DB_DIR = PROJECT_ROOT / "vector_db" / "chroma_db"

LOG_DIR.mkdir(exist_ok=True)

DB_DIR.mkdir(parents=True, exist_ok=True)

# ==================================================
# CONFIGURATION
# ==================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTION_NAME = "heritage_collection"

# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ==================================================
# LOAD MODEL
# ==================================================

logger.info("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

logger.info("Embedding model loaded successfully.")

# ==================================================
# CHROMADB
# ==================================================

client = chromadb.PersistentClient(path=str(DB_DIR))

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

logger.info(f"Connected to collection: {COLLECTION_NAME}")

# ==================================================
# PROCESS FILES
# ==================================================

report = []

json_files = sorted(CHUNK_DIR.glob("*.json"))

if not json_files:
    logger.warning("No chunk files found.")
    raise SystemExit()

for file_path in json_files:

    dataset = file_path.stem

    logger.info(f"Processing {dataset}")

    with open(file_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    added = 0
    skipped = 0

    for chunk in chunks:

        chunk_id = chunk["chunk_id"]

        existing = collection.get(ids=[chunk_id])

        if existing["ids"]:
            skipped += 1
            continue

        embedding = model.encode(
            chunk["text"],
            convert_to_numpy=True
        ).tolist()

        metadata = dict(chunk.get("metadata", {}))

        metadata["record_id"] = chunk.get("record_id", "")

        metadata["category"] = chunk.get("category", "")

        metadata["title"] = chunk.get("title", "")

        collection.add(
            ids=[chunk_id],
            documents=[chunk["text"]],
            embeddings=[embedding],
            metadatas=[metadata]
        )

        added += 1

    logger.info(f"{dataset}")
    logger.info(f"Added   : {added}")
    logger.info(f"Skipped : {skipped}")

    report.append(
        f"{dataset:20} Added={added:4}  Skipped={skipped:4}"
    )

# ==================================================
# REPORT
# ==================================================

report_path = LOG_DIR / "embedding_report.txt"

with open(report_path, "w", encoding="utf-8") as f:

    f.write("HERITAGEGPT EMBEDDING REPORT\n")

    f.write("=" * 60 + "\n\n")

    for line in report:
        f.write(line + "\n")

logger.info("=" * 60)
logger.info("Embedding generation completed.")
logger.info(f"Database : {DB_DIR}")
logger.info(f"Report   : {report_path}")
logger.info(f"Total vectors stored : {collection.count()}")
logger.info("=" * 60)