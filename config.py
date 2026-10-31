
"""
config.py

Configuration settings for HeritageGPT.

Author: Sai Raja
Project: HeritageGPT
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# ---------------------------------------------------
# Project Root Directory
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------

load_dotenv(BASE_DIR / ".env")


class Config:
    """
    Central configuration class.
    """

    # =================================================
    # API Keys
    # =================================================

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    # =================================================
    # LLM Configuration
    # =================================================

    MODEL_NAME = "openai/gpt-oss-20b"

    TEMPERATURE = 0.2

    MAX_TOKENS = 1024

    # =================================================
    # Embedding Model
    # =================================================

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # =================================================
    # ChromaDB
    # =================================================

    CHROMA_DB_PATH = str(BASE_DIR / "vector_db" / "chroma_db")

    # Combined tourism dataset collection
    COLLECTION_NAME = "heritage_combined_test"

    # =================================================
    # Retrieval
    # =================================================

    TOP_K = 5

    # =================================================
    # Dataset
    # =================================================

    DATASET_FOLDER = str(BASE_DIR / "datasets")

    KNOWLEDGE_FILE = (
        BASE_DIR / "datasets" / "aptourism_places.json"
    )

    CHUNK_FILE = (
        BASE_DIR
        / "preprocessing"
        / "chunks"
        / "atourism_places_chunks.json"
    )

    # =================================================
    # Logging
    # =================================================

    LOG_LEVEL = "INFO"

    LOG_FILE = str(BASE_DIR / "logs" / "heritage.log")

    # =================================================
    # Validation
    # =================================================

    SUPPORTED_CATEGORIES = [
        "Temple",
        "Fort",
        "Museum",
        "Festival",
        "Beach",
        "Waterfall",
        "Cave",
        "Wildlife",
        "Lake",
        "Hill Station",
        "Nature and Beauty",
        "Nature and Wildlife",
        "Religious",
        "Historic & Heritage"
    ]

    # =================================================
    # Application
    # =================================================

    APP_NAME = "HeritageGPT"

    VERSION = "1.0.0"
