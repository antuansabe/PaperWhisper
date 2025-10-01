# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PaperWhisper is a RAG (Retrieval-Augmented Generation) application that allows users to have conversations with their PDF documents. It uses:
- FAISS for local vector storage
- Hugging Face sentence-transformers for embeddings
- MISTRAL API for answer generation (optional)
- Streamlit for the web interface
- LangChain for orchestration

## Development Commands

### Setup and Installation
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env  # Then edit .env with your API keys
```

### Running the Application
```bash
streamlit run app.py
```

### Environment Variables
Required in `.env` (see `.env.example`):
- `MISTRAL_API_KEY` - For LLM response generation with Mistral AI (optional for search-only mode)
- `EMBEDDINGS_MODEL` - Hugging Face model for embeddings (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `DATA_DIR` - Directory for storing PDFs and FAISS index (default: `./data`)

## Architecture

### Core Components

**RAG Pipeline** (`src/rag_engine.py`)
- `read_pdf()` - Extracts text from PDF using pypdf with error handling per page
- `split_into_chunks()` - Splits text into overlapping chunks (900 chars, 150 overlap) using RecursiveCharacterTextSplitter
- `generate_embeddings()` - Creates HuggingFaceEmbeddings instance with normalized embeddings
- `build_faiss_index()` - Constructs FAISS index from chunks and embeddings
- `save_index()` - Persists FAISS index and chunk metadata to disk
- `load_index()` - Loads FAISS index from disk with embeddings validation
- `retrieve_relevant_chunks()` - Returns top-k similar chunks with similarity scores
- `ingest_pdf_to_index()` - Full pipeline from PDF to indexed FAISS store with force rebuild option

**Streamlit Interface** (`app.py`)
- PDF upload and local storage in `data/` directory
- FAISS index management (creation, loading, clearing via sidebar)
- Sidebar controls for embeddings model, Mistral model selection, and top-k chunks
- Document preview (first 1500 characters)
- Query interface with context display and similarity scores
- LLM response generation using Mistral AI when API key is configured
- `get_mistral_llm()` - Initializes ChatMistralAI with caching
- `generate_answer_with_mistral()` - Generates responses using RAG context and optimized prompts

### Data Flow

1. User uploads PDF via Streamlit
2. PDF saved to `data/{filename}`
3. Text extracted and chunked (with configurable size/overlap)
4. Embeddings generated and stored in FAISS index at `data/faiss_index/`
5. Chunk metadata saved as pickle file for reference
6. User query → embedding generation → similarity search → retrieve top-k chunks with scores
7. Chunks + query sent to Mistral AI with optimized RAG prompt → response displayed
8. FAISS index persisted to disk for reuse across sessions

### Key Design Decisions

- **Local-first**: FAISS index persists locally, no external vector DB needed
- **Graceful degradation**: App works for search without Mistral API key (search-only mode)
- **Model flexibility**: Both embeddings and Mistral models configurable via environment or UI
- **Chunk strategy**: RecursiveCharacterTextSplitter with multiple separators for semantic coherence
- **Normalized embeddings**: Embeddings are normalized for better cosine similarity performance
- **Metadata persistence**: Chunk metadata saved separately for potential reconstruction
- **Error resilience**: Per-page PDF extraction with error handling for corrupted pages
- **Caching**: Streamlit caches LLM instance with `@st.cache_resource` to avoid re-initialization
- **Optimized prompts**: RAG prompts instruct Mistral to respond only from context with clear guidelines

## Common Patterns

When extending the RAG engine:
- All embeddings operations go through `generate_embeddings()` to ensure consistency
- FAISS index is always loaded/saved at `INDEX_PATH` (defined in `rag_engine.py`)
- Text chunking parameters (size, overlap) are centralized in `split_into_chunks()`
- Use `force_rebuild=True` in `ingest_pdf_to_index()` to bypass cache and rebuild index
- Chunk metadata is automatically saved alongside FAISS index for debugging/reconstruction

When modifying the UI:
- Use `st.spinner()` for operations that take time (PDF processing, search, LLM calls)
- Store database instance in `db` variable after ingestion
- Check for `db is None` before search operations
- Handle missing API key gracefully with warnings/info messages
- Model selection in sidebar provides flexibility between Mistral model tiers
- Use `@st.cache_resource` for expensive initializations (LLM, embeddings)

When working with Mistral:
- System prompts emphasize responding only from provided context
- Temperature set to 0 for deterministic, factual responses
- max_tokens capped at 1024 to control response length
- Context chunks separated with clear delimiters (`---`) for better parsing
- Error handling wraps all LLM calls to prevent crashes
