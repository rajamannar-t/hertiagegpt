"""
retriever.py

Retrieves the most relevant documents from ChromaDB.

Author: Sai Raja
Project: HeritageGPT
"""

import logging
from models.database import VectorDatabase


class Retriever:

    def __init__(self):

        self.db = VectorDatabase()

    ##############################################################

    def retrieve(
        self,
        query: str,
        top_k: int = 5
    ):
        """
        Retrieve relevant documents.

        Returns:
            List[dict]
        """

        logging.info(f"Searching for: {query}")

        results = self.db.search(
            query=query,
            top_k=top_k
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved = []

        for doc, meta, distance in zip(
            documents,
            metadatas,
            distances
        ):

            retrieved.append({

                "text": doc,

                "metadata": meta,

                "score": round(distance, 4)

            })

        return retrieved

    ##############################################################

    def build_context(
        self,
        query: str,
        top_k: int = 5
    ):
        """
        Convert retrieved documents into
        one context string for the LLM.
        """

        retrieved = self.retrieve(query, top_k)

        context = ""

        for i, item in enumerate(retrieved, start=1):

            meta = item["metadata"]

            context += f"""
Document {i}

Title:
{meta.get('title','Unknown')}

Category:
{meta.get('category','Unknown')}

District:
{meta.get('district','Unknown')}

Content:
{item['text']}

----------------------------------------------------

"""

        return context.strip()

    ##############################################################

    def print_results(
        self,
        query: str,
        top_k: int = 5
    ):

        docs = self.retrieve(query, top_k)

        print("\nRelevant Documents\n")

        for i, doc in enumerate(docs, start=1):

            print("=" * 60)

            print(f"Result {i}")

            print("=" * 60)

            print("Title      :", doc["metadata"].get("title"))

            print("Category   :", doc["metadata"].get("category"))

            print("District   :", doc["metadata"].get("district"))

            print("Similarity :", doc["score"])

            print()

            print(doc["text"])

            print()