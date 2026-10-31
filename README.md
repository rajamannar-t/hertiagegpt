# HeritageGPT -- AI-Powered Heritage & Tourism Assistant

HeritageGPT is a Retrieval-Augmented Generation (RAG) application for
exploring the heritage and tourism of Andhra Pradesh, India. Users can
ask questions about temples, forts, beaches, festivals, caves, museums,
and other destinations. The system retrieves relevant information from a
curated knowledge base and uses a Groq-hosted language model to generate
context-aware answers with source references.

## Features

-   Conversational question answering about Andhra Pradesh heritage and
    tourism.
-   Retrieval-Augmented Generation (RAG) using ChromaDB and Sentence
    Transformers.
-   Semantic search over an indexed knowledge base.
-   Groq API integration for grounded answer generation.
-   Multi-format ingestion pipeline for JSON, TXT, CSV, PDF, and DOCX.
-   Stable chunk IDs and ChromaDB upserts to make repeated ingestion
    safer.
-   Source metadata and citations, including title, file, district,
    category, and URL when available.
-   Streamlit chat interface with example prompts and source references.

## Technology Stack

  Component          Technology
  ------------------ ------------------------------------------
  Language           Python
  UI                 Streamlit
  RAG                Retrieval-Augmented Generation
  Vector database    ChromaDB
  Embeddings         `sentence-transformers/all-MiniLM-L6-v2`
  LLM provider       Groq API
  Document formats   JSON, TXT, CSV, PDF, DOCX
  Configuration      python-dotenv

## Architecture

``` text
User
  |
  v
Streamlit Chat Interface
  |
  v
RAG Engine
  |
  +--> Retriever --> ChromaDB Vector Search
  |                       |
  |                       v
  |                Relevant Chunks
  |                       |
  +--> Prompt Builder <--+
              |
              v
        Groq-hosted LLM
              |
              v
    Answer + Source Metadata
              |
              v
       Streamlit Response
```

### Ingestion pipeline

``` text
Source files
(JSON / TXT / CSV / PDF / DOCX)
          |
          v
preprocessing/chunks/
          |
          v
Parsing and text extraction
          |
          v
Chunk preparation and metadata
          |
          v
Sentence Transformers embeddings
          |
          v
ChromaDB upsert
          |
          v
Searchable knowledge base
```

## Project Structure

``` text
HeritageGPT/
├── app.py
├── config.py
├── .env
├── datasets/
│   └── aptourism_places.json
├── models/
│   ├── database.py
│   ├── embedding_model.py
│   ├── retriever.py
│   ├── rag_engine.py
│   ├── prompts.py
│   └── llm.py
├── preprocessing/
│   ├── validate_data.py
│   ├── clean_data.py
│   ├── chunk_data.py
│   ├── ingest_knowledge_base.py
│   ├── chunks/
│   ├── cleaned_data/
│   └── logs/
└── vector_db/
    └── chroma_db/
```

The exact structure may vary slightly depending on your local project.

## Getting Started

### 1. Clone the repository

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd HeritageGPT
```

Replace the placeholder with your GitHub repository URL.

### 2. Create a virtual environment

**Windows PowerShell:**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

``` cmd
python -m venv .venv
.venv\Scriptsctivate.bat
```

**macOS / Linux:**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If a `requirements.txt` file is available:

``` bash
python -m pip install -r requirements.txt
```

The main packages used by the application and ingestion pipeline
include:

``` bash
python -m pip install streamlit chromadb sentence-transformers groq python-dotenv pypdf python-docx pandas
```

Install any other packages imported by your project modules.

### 4. Configure the Groq API key

Create a `.env` file in the project root:

``` env
GROQ_API_KEY=your_groq_api_key
```

Replace the placeholder with your own key. Never commit `.env` or expose
API keys in source code or public repositories.

### 5. Check the configuration

Review `config.py` and confirm that the embedding model, ChromaDB path,
collection name, and input directories match your project.

Example settings:

``` python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHROMA_DB_PATH = "vector_db/chroma_db"
COLLECTION_NAME = "heritage_combined_test"
TOP_K = 5
```

The ingestion and application code must use the same ChromaDB collection
and embedding model.

### 6. Prepare documents

Place processed chunk files in:

``` text
preprocessing/chunks/
```

The supplied ingestion pipeline processes supported files in this
directory and its subdirectories:

-   JSON
-   TXT
-   CSV
-   PDF
-   DOCX

Example:

``` text
preprocessing/
└── chunks/
    ├── tourism_places_chunks.json
    └── politica_chunks.txt
```

**Important:** The ingestion script reads from `preprocessing/chunks/`.
It does not automatically process every raw file in `datasets/`. Run
validation, cleaning, and chunking first when source files need
preprocessing.

### 7. Ingest documents into ChromaDB

Run from the project root:

``` bash
python preprocessing/ingest_knowledge_base.py
```

On Windows, this also works:

``` powershell
python preprocessing\ingest_knowledge_base.py
```

The script parses documents, creates embeddings, and upserts chunks into
the configured ChromaDB collection. Review the processing logs and
manifest in:

``` text
preprocessing/logs/
```

### 8. Launch the Streamlit application

``` bash
python -m streamlit run app.py
```

Open the local URL printed in the terminal, typically
`http://localhost:8501`.

## Example Questions

-   What are some famous historical places in Andhra Pradesh?
-   Explain the history and significance of a major temple in Andhra
    Pradesh.
-   Which beaches can I visit in Andhra Pradesh?
-   What is the best time to visit Araku Valley?
-   How can I reach a particular heritage destination?

Answers depend on the information present in the indexed knowledge base.

## Source Citations

The RAG engine returns source metadata with the answer. The Streamlit UI
can display the title or file name and a clickable URL when one is
available.

Example rendering:

``` python
for source in result.get("sources", []):
    label = source.get("title") or source.get("source_file") or "Source"
    source_file = source.get("source_file", "")
    source_url = source.get("source_url", "")

    st.markdown(f"**Source:** {label} (`{source_file}`)")

    if source_url.startswith(("https://", "http://")):
        st.markdown(f"[Open source]({source_url})")
```

Only display links present in retrieved metadata. Verify important
travel details with official tourism or destination sources.

## Troubleshooting

### No results are retrieved

1.  Confirm ingestion completed successfully.
2.  Confirm files are inside `preprocessing/chunks/`.
3.  Confirm ingestion and the app use the same ChromaDB path and
    collection name.
4.  Confirm the query embedding model matches the ingestion embedding
    model.
5.  Inspect `ingestion_manifest.json` and `ingestion.log` for failures.

### Updated source documents are not reflected

Run ingestion again. Stable IDs and upserts update matching chunks. If
the embedding model or chunking strategy changes, back up the vector
database and rebuild the collection to avoid mixing incompatible
embeddings or stale chunks.

### Duplicate or stale results appear

Records created by an older ingestion method may remain if they use
different IDs or lack source metadata. Back up the database before
cleanup. Do not delete the collection unless you intentionally want to
rebuild the complete knowledge base.

### Groq API errors

-   Check the `GROQ_API_KEY` value in `.env`.
-   Confirm the configured model is available to your account.
-   Check network connectivity and API limits.
-   Do not print API keys in logs or issue reports.

## Security

-   Keep `.env`, API keys, and private datasets out of version control.
-   Add `.env`, `.venv/`, generated logs, and local vector database
    files to `.gitignore` as appropriate.
-   Validate documents before indexing.
-   Do not expose private documents through a public deployment.
-   Treat retrieved document content as untrusted input; it must not
    override application instructions.

Example `.gitignore` entries:

``` gitignore
.env
.venv/
__pycache__/
*.py[cod]
.streamlit/secrets.toml
preprocessing/logs/
vector_db/chroma_db/
```

## Scope and Limitations

-   Answer quality depends on the accuracy, coverage, and freshness of
    the indexed documents.
-   HeritageGPT is a knowledge assistant, not an official tourism
    authority or real-time travel service.
-   Opening hours, ticket prices, transport availability, and other
    changing details should be verified with official sources.
-   Multi-format support depends on the parsing dependencies installed
    and the formats implemented by the ingestion script.
-   Evaluate retrieval relevance and answer faithfulness with a
    representative question set before production deployment.

## Future Enhancements

-   Automated evaluation of retrieval relevance and answer faithfulness.
-   Hybrid retrieval and reranking.
-   Ingestion monitoring and document update tracking.
-   Automated tests for parsing, chunking, retrieval, and citation
    generation.
-   Managed secrets, monitoring, and backups for deployment.

## Author

**Your Name**\
B.Tech -- Artificial Intelligence

Add your GitHub, LinkedIn, and contact details before publishing.

------------------------------------------------------------------------

*HeritageGPT --- Explore the heritage of Andhra Pradesh through
conversational AI.*
