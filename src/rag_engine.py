import os
from typing import List, Tuple

from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Cargar variables de entorno
load_dotenv()

DEFAULT_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DATA_DIR = os.getenv("DATA_DIR", "./data")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index")


def read_pdf(file_path: str) -> str:
    """Extrae texto de un PDF completo.

    Args:
        file_path: Ruta al archivo PDF
    Returns:
        Texto concatenado de todas las páginas
    """
    reader = PdfReader(file_path)
    pages_text: List[str] = []
    for page in reader.pages:
        try:
            pages_text.append(page.extract_text() or "")
        except Exception:
            pages_text.append("")
    return "\n\n".join(pages_text)


def chunk_text(text: str, chunk_size: int = 900, chunk_overlap: int = 150) -> List[str]:
    """Divide texto en chunks solapados para RAG.

    Args:
        text: Texto de entrada
        chunk_size: tamaño de cada chunk
        chunk_overlap: solapamiento entre chunks
    Returns:
        Lista de chunks
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", ".", "?", "!", ",", " "]
    )
    return splitter.split_text(text)


def build_embeddings(model_name: str = DEFAULT_MODEL_NAME):
    """Crea el objeto de embeddings de HF."""
    return HuggingFaceEmbeddings(model_name=model_name)


def create_or_load_index(text_chunks: List[str], index_path: str = INDEX_PATH, model_name: str = DEFAULT_MODEL_NAME) -> FAISS:
    """Crea o carga un índice FAISS local a partir de chunks.

    Si existe el índice en disco, lo carga; si no, lo construye y guarda.
    """
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    embeddings = build_embeddings(model_name)

    if os.path.exists(index_path):
        try:
            db = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
            return db
        except Exception:
            pass  # Si la carga falla, re-creamos el índice

    db = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    db.save_local(index_path)
    return db


def similarity_search(db: FAISS, query: str, k: int = 4) -> List[Tuple[str, float]]:
    """Devuelve los k chunks más similares con sus puntuaciones."""
    docs_and_scores = db.similarity_search_with_score(query, k=k)
    return [(doc.page_content, score) for doc, score in docs_and_scores]


def ingest_pdf_to_index(pdf_path: str, index_path: str = INDEX_PATH, model_name: str = DEFAULT_MODEL_NAME) -> FAISS:
    """Pipeline: lee PDF, chunea texto, crea/carga FAISS y devuelve el índice."""
    text = read_pdf(pdf_path)
    chunks = chunk_text(text)
    db = create_or_load_index(chunks, index_path=index_path, model_name=model_name)
    return db
