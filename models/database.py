"""
database.py

Handles all ChromaDB operations.

Author: Sai Raja
Project: HeritageGPT
"""

import logging

from chromadb import PersistentClient

from config import Config
from models.embedding_model import EmbeddingModel


class VectorDatabase:

    def __init__(self):
        """
        Initialize ChromaDB.
        """

        self.client = PersistentClient(
            path=Config.CHROMA_DB_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            metadata={
                "description": "HeritageGPT Knowledge Base"
            }
        )

        logging.info(
            f"Connected to collection: {Config.COLLECTION_NAME}"
        )

    ########################################################

    def add_document(
        self,
        doc_id,
        text,
        metadata
    ):

        embedding = EmbeddingModel.get_embedding(text)

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding.tolist()],
            metadatas=[metadata]
        )

    ########################################################

    def add_documents(
        self,
        ids,
        texts,
        metadatas
    ):

        embeddings = EmbeddingModel.get_embeddings(texts)

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings.tolist(),
            metadatas=metadatas
        )

    ########################################################

    def search(
        self,
        query,
        top_k=5
    ):

        query_embedding = EmbeddingModel.get_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )

        return results

    ########################################################

    def count(self):

        return self.collection.count()

    ########################################################

    def peek(self, limit=5):

        return self.collection.peek(limit)

    ########################################################

    def delete_all(self):

        self.client.delete_collection(
            Config.COLLECTION_NAME
        )

        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME
        )