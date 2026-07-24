"""
rag_engine.py

Main RAG Pipeline for HeritageGPT.

Author: Sai Raja
Project: HeritageGPT
"""

import logging

from models.retriever import Retriever
from models.prompts import PromptBuilder
from models.llm import LLM


class RAGEngine:

    def __init__(self):

        self.retriever = Retriever()
        self.llm = LLM()

    ###########################################################

    def answer_question(
        self,
        question: str,
        top_k: int = 5
    ):
        """
        Complete RAG Pipeline.

        Returns:
            dict
        """

        logging.info(f"Question: {question}")

        ##################################################
        # Retrieve documents
        ##################################################

        documents = self.retriever.retrieve(
            query=question,
            top_k=top_k
        )

        ##################################################
        # No results found
        ##################################################

        if len(documents) == 0:

            prompt = PromptBuilder.no_context_prompt(question)

            answer = self.llm.generate(prompt)

            return {
                "question": question,
                "answer": answer,
                "sources": []
            }

        ##################################################
        # Build context
        ##################################################

        context = self.retriever.build_context(
            query=question,
            top_k=top_k
        )

        ##################################################
        # Create Prompt
        ##################################################

        prompt = PromptBuilder.build_prompt(
            context=context,
            question=question
        )

        ##################################################
        # Generate Answer
        ##################################################

        answer = self.llm.generate(prompt)

        ##################################################
        # Collect Sources
        ##################################################

        sources = []

        for item in documents:

            metadata = item["metadata"]

            sources.append({

                "title": metadata.get("title"),

                "district": metadata.get("district"),

                "category": metadata.get("category"),

                "score": item["score"]

            })

        ##################################################

        return {

            "question": question,

            "answer": answer,

            "sources": sources

        }