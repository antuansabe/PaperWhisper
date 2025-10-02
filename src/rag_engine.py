"""
RAG Engine para PaperWhisper
Módulo principal que gestiona la lectura de PDFs, chunking, embeddings,
indexado con FAISS y búsqueda semántica.

PRIVACIDAD: Este módulo procesa documentos solo en memoria sin persistencia.
"""

import os
import pickle
import logging
from typing import List, Tuple, Optional
from io import BytesIO

from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Desactivar telemetría de HuggingFace para privacidad
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["HF_HUB_OFFLINE"] = "0"  # Permitir descarga inicial de modelos

# Configurar logging seguro (sin datos sensibles)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configuración por defecto
DEFAULT_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DATA_DIR = os.getenv("DATA_DIR", "./data")
INDEX_PATH = os.path.join(DATA_DIR, "faiss_index")
METADATA_PATH = os.path.join(DATA_DIR, "chunks_metadata.pkl")

# Parámetros de chunking
DEFAULT_CHUNK_SIZE = 900
DEFAULT_CHUNK_OVERLAP = 150


def read_pdf(file_path: str) -> str:
    """
    Lee y extrae todo el texto de un archivo PDF.

    Args:
        file_path: Ruta al archivo PDF

    Returns:
        Texto completo del PDF concatenado

    Raises:
        FileNotFoundError: Si el archivo no existe
        Exception: Si hay error al leer el PDF
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {file_path} no existe")

    try:
        reader = PdfReader(file_path)
        pages_text: List[str] = []

        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            except Exception as e:
                logger.warning(f"Error extrayendo página {page_num + 1}")
                pages_text.append("")

        full_text = "\n\n".join(pages_text)
        logger.info(f"PDF procesado: {len(reader.pages)} páginas")
        return full_text

    except Exception as e:
        raise Exception(f"Error leyendo PDF: {e}")


def read_pdf_from_buffer(pdf_buffer: BytesIO) -> str:
    """
    Lee y extrae todo el texto de un PDF desde memoria (BytesIO).

    PRIVACIDAD: No guarda el PDF en disco, procesa directamente desde memoria.

    Args:
        pdf_buffer: Buffer de bytes con el contenido del PDF

    Returns:
        Texto completo del PDF concatenado

    Raises:
        Exception: Si hay error al leer el PDF
    """
    try:
        reader = PdfReader(pdf_buffer)
        pages_text: List[str] = []

        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            except Exception:
                # No logear el error para no exponer metadata del PDF
                pages_text.append("")

        full_text = "\n\n".join(pages_text)
        logger.info(f"PDF procesado en memoria: {len(reader.pages)} páginas")
        return full_text

    except Exception as e:
        raise Exception(f"Error procesando PDF desde memoria: {e}")


def split_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """
    Divide el texto en fragmentos (chunks) con solapamiento.
    Usa RecursiveCharacterTextSplitter para mantener coherencia semántica.

    Args:
        text: Texto a dividir
        chunk_size: Tamaño máximo de cada chunk en caracteres
        chunk_overlap: Número de caracteres solapados entre chunks

    Returns:
        Lista de chunks de texto
    """
    if not text or not text.strip():
        raise ValueError("El texto no puede estar vacío")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", ".", "?", "!", ",", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_text(text)
    logger.info(f"Texto dividido en {len(chunks)} chunks")
    return chunks


def generate_embeddings(model_name: str = DEFAULT_MODEL_NAME) -> HuggingFaceEmbeddings:
    """
    Crea el objeto de embeddings de Hugging Face.
    Este objeto se usa para generar vectores tanto de chunks como de queries.

    Args:
        model_name: Nombre del modelo de sentence-transformers

    Returns:
        Instancia de HuggingFaceEmbeddings
    """
    logger.info(f"Cargando modelo de embeddings: {model_name}")
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},  # Cambiar a 'cuda' si tienes GPU
        encode_kwargs={'normalize_embeddings': True}  # Normalizar para mejor similaridad coseno
    )
    logger.info("Modelo de embeddings cargado")
    return embeddings


def build_faiss_index(chunks: List[str], embeddings: HuggingFaceEmbeddings) -> FAISS:
    """
    Construye un índice FAISS a partir de una lista de chunks.
    FAISS genera automáticamente los embeddings usando el objeto embeddings.

    Args:
        chunks: Lista de textos (chunks del documento)
        embeddings: Objeto de embeddings de Hugging Face

    Returns:
        Índice FAISS listo para búsquedas
    """
    if not chunks:
        raise ValueError("La lista de chunks no puede estar vacía")

    logger.info(f"Construyendo índice FAISS con {len(chunks)} chunks")

    # Crear documentos de LangChain (FAISS los necesita en este formato)
    documents = [Document(page_content=chunk) for chunk in chunks]

    # FAISS.from_documents genera embeddings automáticamente y construye el índice
    db = FAISS.from_documents(documents=documents, embedding=embeddings)

    logger.info("Índice FAISS construido exitosamente")
    return db


def save_index(db: FAISS, chunks: List[str], index_path: str = INDEX_PATH):
    """
    Guarda el índice FAISS y los chunks originales en disco.

    Args:
        db: Índice FAISS a guardar
        chunks: Lista de chunks originales (para referencia)
        index_path: Ruta donde guardar el índice
    """
    os.makedirs(os.path.dirname(index_path), exist_ok=True)

    # Guardar índice FAISS
    db.save_local(index_path)
    logger.info(f"Índice FAISS guardado en: {index_path}")

    # Guardar metadata (chunks originales) por si necesitamos reconstruir
    metadata_path = index_path.replace("faiss_index", "chunks_metadata.pkl")
    with open(metadata_path, "wb") as f:
        pickle.dump(chunks, f)
    logger.info(f"Metadata guardada")


def load_index(index_path: str = INDEX_PATH, embeddings: Optional[HuggingFaceEmbeddings] = None) -> FAISS:
    """
    Carga un índice FAISS previamente guardado desde disco.

    Args:
        index_path: Ruta del índice guardado
        embeddings: Objeto de embeddings (si no se provee, se crea uno nuevo)

    Returns:
        Índice FAISS cargado

    Raises:
        FileNotFoundError: Si el índice no existe
    """
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"No se encontró índice en: {index_path}")

    if embeddings is None:
        embeddings = generate_embeddings()

    logger.info("Cargando índice FAISS desde disco")
    db = FAISS.load_local(
        index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )
    logger.info("Índice FAISS cargado exitosamente")
    return db


def retrieve_relevant_chunks(
    db: FAISS,
    query: str,
    k: int = 4
) -> List[Tuple[str, float]]:
    """
    Busca los k chunks más relevantes para una query dada.

    Args:
        db: Índice FAISS
        query: Pregunta del usuario
        k: Número de chunks a recuperar

    Returns:
        Lista de tuplas (chunk_text, similarity_score)
        Score más bajo = mayor similaridad
    """
    if not query or not query.strip():
        raise ValueError("La query no puede estar vacía")

    # PRIVACIDAD: No logear la query del usuario
    logger.debug(f"Buscando {k} chunks relevantes")

    # similarity_search_with_score devuelve (Document, score)
    docs_and_scores = db.similarity_search_with_score(query, k=k)

    # Extraer contenido y scores
    results = [(doc.page_content, score) for doc, score in docs_and_scores]

    logger.debug(f"Encontrados {len(results)} chunks")
    return results


def ingest_pdf_to_index(
    pdf_path: str,
    index_path: str = INDEX_PATH,
    model_name: str = DEFAULT_MODEL_NAME,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    force_rebuild: bool = False,
    persist: bool = False
) -> FAISS:
    """
    Pipeline completo: lee PDF, chunking, embeddings, indexado FAISS.

    IMPORTANTE: Por defecto NO persiste el índice (persist=False) para evitar
    compartir datos entre usuarios en deploy. Cada sesión crea su propio índice en memoria.

    Args:
        pdf_path: Ruta al archivo PDF
        index_path: Ruta donde guardar/cargar el índice (solo si persist=True)
        model_name: Modelo de embeddings a usar
        chunk_size: Tamaño de cada chunk
        chunk_overlap: Solapamiento entre chunks
        force_rebuild: Si True, reconstruye el índice aunque exista
        persist: Si True, guarda el índice en disco (uso local). Si False, solo en memoria (deploy)

    Returns:
        Índice FAISS listo para búsquedas (en memoria)
    """
    embeddings = generate_embeddings(model_name)

    # Solo intentar cargar índice si persist=True y existe
    if persist and os.path.exists(index_path) and not force_rebuild:
        try:
            logger.info("Índice existente encontrado, cargando...")
            return load_index(index_path, embeddings)
        except Exception as e:
            logger.warning(f"Error cargando índice: reconstruyendo")

    # Pipeline completo: leer → chunkear → indexar
    logger.info("Iniciando pipeline de ingesta")
    text = read_pdf(pdf_path)
    chunks = split_into_chunks(text, chunk_size, chunk_overlap)
    db = build_faiss_index(chunks, embeddings)

    # Solo guardar en disco si persist=True
    if persist:
        save_index(db, chunks, index_path)
        logger.info("Índice guardado en disco")
    else:
        logger.info("Índice creado en memoria (no persistido)")

    logger.info("Pipeline completado exitosamente")
    return db


def ingest_pdf_from_buffer(
    pdf_buffer: BytesIO,
    model_name: str = DEFAULT_MODEL_NAME,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> FAISS:
    """
    Pipeline completo desde buffer en memoria: lee PDF, chunking, embeddings, indexado FAISS.

    PRIVACIDAD: No guarda NADA en disco. Todo el procesamiento es en memoria.
    Ideal para deploy en producción donde la privacidad es crítica.

    Args:
        pdf_buffer: Buffer de bytes con el contenido del PDF
        model_name: Modelo de embeddings a usar
        chunk_size: Tamaño de cada chunk
        chunk_overlap: Solapamiento entre chunks

    Returns:
        Índice FAISS en memoria (no persistido)
    """
    embeddings = generate_embeddings(model_name)

    # Pipeline completo en memoria: leer → chunkear → indexar
    logger.info("Procesando PDF desde memoria")
    text = read_pdf_from_buffer(pdf_buffer)
    chunks = split_into_chunks(text, chunk_size, chunk_overlap)
    db = build_faiss_index(chunks, embeddings)

    logger.info("Pipeline completado en memoria (100% privado)")
    return db


# Función de conveniencia para búsqueda (alias más semántico)
def similarity_search(db: FAISS, query: str, k: int = 4) -> List[Tuple[str, float]]:
    """
    Alias de retrieve_relevant_chunks para mantener compatibilidad.
    """
    return retrieve_relevant_chunks(db, query, k)
