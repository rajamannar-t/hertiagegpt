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

    MODEL_NAME = "llama-3.3-70b-versatile"

    TEMPERATURE = 0.2

    MAX_TOKENS = 1024

    # =================================================
    # Embedding Model
    # =================================================

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    # =================================================
    # ChromaDB
    # =================================================

    CHROMA_DB_PATH = "vector_db/chroma_db"

    COLLECTION_NAME = "heritage_collection"

    # =================================================
    # Retrieval
    # =================================================

    TOP_K = 5

    # =================================================
    # Dataset
    # =================================================

    DATASET_FOLDER = "datasets"

    # =================================================
    # Logging
    # =================================================

    LOG_LEVEL = "INFO"

    LOG_FILE = "logs/heritage.log"

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
        "Hill Station"
    ]

    # =================================================
    # Application
    # =================================================

    APP_NAME = "HeritageGPT"

    VERSION = "1.0.0"