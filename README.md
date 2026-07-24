# HeritageGPT

HeritageGPT is an AI assistant for exploring the heritage and tourism of Andhra Pradesh. It uses a retrieval-augmented generation pipeline with ChromaDB, Sentence Transformers, and a Groq-hosted LLM to answer questions about temples, forts, beaches, festivals, caves, museums, and more.

## Features

- Chat with the knowledge base through a Streamlit UI.
- Run a simple terminal-based question/answer flow from `main.py`.
- Search curated heritage datasets with source citations.
- Rebuild the vector database from cleaned JSON data and chunks.

## Requirements

- Python 3.10+
- A Groq API key
- Internet access for downloading embedding models on first run

## Install

Create and activate a virtual environment, then install the dependencies used by the project:

```bash
pip install streamlit python-dotenv openai chromadb sentence-transformers colorama
```

## Configure

Create a `.env` file in the project root and add your Groq key:

```env
GROQ_API_KEY=your_api_key_here
```

## Run the app

Start the Streamlit interface:

```bash
streamlit run app.py
```

You can also use the CLI entry point:

```bash
python main.py
```

## Data Pipeline

If you want to rebuild the knowledge base from the raw datasets, the preprocessing flow is:

1. Validate the source JSON files with `preprocessing/validate_data.py`.
2. Convert cleaned records into chunks with `preprocessing/chunk_data.py`.
3. Generate embeddings and store them in ChromaDB with `preprocessing/generate_embeddings.py`.

## Project Structure

- `app.py` - Streamlit chat application
- `main.py` - CLI entry point
- `models/` - RAG engine, embeddings, LLM, retriever, and database helpers
- `components/` - Streamlit UI components
- `pages/` - Multi-page Streamlit screens
- `datasets/` - Heritage and tourism JSON data
- `preprocessing/` - Data validation, chunking, and embedding scripts
- `styles/` - Theme and CSS styling
- `docs/` - Architecture and schema notes

## Notes

- The repository includes a local ChromaDB store under `vector_db/`.
- The app currently targets Andhra Pradesh heritage and tourism content.
- If dependencies are missing on first run, install them in the active virtual environment and retry.
