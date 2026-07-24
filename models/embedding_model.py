"""
embedding_model.py

Loads and manages the Sentence Transformer embedding model.

Author: Sai Raja
Project: HeritageGPT
"""

import logging
from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    """
    Singleton class for loading the embedding model only once.
    """

    _model = None

    @classmethod
    def load_model(cls, model_name: str = "all-MiniLM-L6-v2"):
        """
        Load SentenceTransformer model.

        Args:
            model_name (str): Name of the embedding model.

        Returns:
            SentenceTransformer
        """

        if cls._model is None:
            logging.info(f"Loading embedding model: {model_name}")
            cls._model = SentenceTransformer(model_name)

        return cls._model

    @classmethod
    def get_embedding(cls, text: str):
        """
        Generate embedding for a single text.

        Args:
            text (str)

        Returns:
            List[float]
        """

        model = cls.load_model()

        embedding = model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding

    @classmethod
    def get_embeddings(cls, texts: list):
        """
        Generate embeddings for multiple texts.

        Args:
            texts (List[str])

        Returns:
            numpy.ndarray
        """

        model = cls.load_model()

        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embeddings