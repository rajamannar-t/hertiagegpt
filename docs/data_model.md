# HeritageGPT Data Model

## Storage Layers

### 1. JSON Knowledge Base
Stores historical places, temples, forts, museums, festivals, food, and other reference data.

### 2. MongoDB
Stores users, favorites, reviews, trip plans, and feedback.

### 3. ChromaDB
Stores embeddings for semantic search and Retrieval-Augmented Generation (RAG).

## MongoDB Collections

- Users
- Favorites
- Reviews
- Trips
- Feedback

## ID Standards

- TMP000001 → Temple
- FOR000001 → Fort
- MUS000001 → Museum
- BEA000001 → Beach
- WAT000001 → Waterfall
- FES000001 → Festival
- FOO000001 → Food