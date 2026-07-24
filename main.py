"""
main.py

Entry point for HeritageGPT.

Author: Sai Raja
Project: HeritageGPT
"""

import logging
from models.rag_engine import RAGEngine


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def print_header():
    print("\n" + "=" * 70)
    print("🏛  HeritageGPT")
    print("AI Assistant for Andhra Pradesh Heritage & Tourism")
    print("=" * 70)


def print_help():
    print("\nYou can ask questions like:\n")

    examples = [
        "Tell me about Tirumala Temple",
        "History of Lepakshi Temple",
        "Famous forts in Andhra Pradesh",
        "Best temples to visit in Vijayawada",
        "Festivals celebrated at Srisailam",
        "How to reach Ahobilam?"
    ]

    for i, example in enumerate(examples, start=1):
        print(f"{i}. {example}")

    print("\nType 'exit' anytime to quit.\n")


def main():

    print_header()

    print_help()

    rag = RAGEngine()

    while True:

        question = input("\nYou ➜ ").strip()

        if not question:
            print("Please enter a question.")
            continue

        if question.lower() in ["exit", "quit"]:
            print("\nThank you for using HeritageGPT!")
            break

        print("\nSearching knowledge base...\n")

        try:

            result = rag.answer_question(question)

            print("=" * 70)
            print("HeritageGPT")
            print("=" * 70)

            print(result["answer"])

            if result["sources"]:

                print("\nSources")

                print("-" * 70)

                for source in result["sources"]:

                    print(
                        f"• {source['title']} "
                        f"({source['district']})"
                    )

            print("\n" + "=" * 70)

        except Exception as e:

            logging.exception(e)

            print("\nSomething went wrong!")

            print(e)


if __name__ == "__main__":
    main()