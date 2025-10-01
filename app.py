"""
PaperWhisper - Interfaz Streamlit
Aplicación para conversar con documentos PDF usando RAG + Mistral AI
"""

import os
from typing import List, Tuple, Optional

import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

from src.rag_engine import (
    ingest_pdf_to_index,
    similarity_search,
    read_pdf,
    INDEX_PATH,
    DEFAULT_MODEL_NAME
)

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="PaperWhisper",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource(show_spinner=False)
def get_mistral_llm(model: str = "mistral-small-latest") -> Optional[ChatMistralAI]:
    """
    Inicializa el modelo de Mistral AI.
    Se cachea para evitar reinicializaciones.

    Args:
        model: Nombre del modelo de Mistral (mistral-small-latest, mistral-medium, etc.)

    Returns:
        Instancia de ChatMistralAI o None si no hay API key
    """
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        st.warning("⚠️ MISTRAL_API_KEY no configurada. Solo se habilitará búsqueda semántica.")
        return None

    try:
        return ChatMistralAI(
            model=model,
            temperature=0,  # Respuestas determinísticas
            max_tokens=1024,  # Límite de tokens en respuesta
        )
    except Exception as e:
        st.error(f"❌ Error inicializando Mistral: {e}")
        return None


def generate_answer_with_mistral(
    llm: ChatMistralAI,
    query: str,
    context_chunks: List[Tuple[str, float]]
) -> str:
    """
    Genera una respuesta usando Mistral AI con el contexto recuperado.

    Args:
        llm: Instancia de ChatMistralAI
        query: Pregunta del usuario
        context_chunks: Lista de (chunk_text, score) del RAG

    Returns:
        Respuesta generada por el LLM
    """
    # Construir contexto a partir de los chunks
    context = "\n\n---\n\n".join([chunk for chunk, _ in context_chunks])

    # Prompt optimizado para RAG
    system_prompt = """Eres un asistente experto que responde preguntas basándote ÚNICAMENTE en el contexto proporcionado.

Reglas importantes:
1. Responde SOLO con información presente en el contexto
2. Si la respuesta no está en el contexto, di: "No encuentro esa información en el documento"
3. Sé preciso y conciso
4. Cita fragmentos relevantes cuando sea útil
5. Si hay información parcial, indícalo claramente"""

    user_prompt = f"""Contexto del documento:
{context}

Pregunta del usuario:
{query}

Respuesta:"""

    # Invocar Mistral
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    try:
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        return f"❌ Error generando respuesta: {e}"


def main():
    """Función principal de la aplicación Streamlit"""

    # Header
    st.title("📄 PaperWhisper")
    st.markdown("### Conversa con tus documentos PDF usando RAG + Mistral AI")
    st.markdown("---")

    # Sidebar - Configuración
    with st.sidebar:
        st.header("⚙️ Configuración")

        # Modelo de embeddings
        embeddings_model = st.text_input(
            "Modelo de embeddings (Hugging Face)",
            value=os.getenv("EMBEDDINGS_MODEL", DEFAULT_MODEL_NAME),
            help="Modelo de sentence-transformers para generar embeddings"
        )

        # Modelo de Mistral
        mistral_model = st.selectbox(
            "Modelo de Mistral",
            options=[
                "mistral-small-latest",
                "mistral-medium-latest",
                "mistral-large-latest",
                "open-mistral-7b",
                "open-mixtral-8x7b"
            ],
            index=0,
            help="Modelo de Mistral AI a usar para generar respuestas"
        )

        # Top-K chunks
        top_k = st.slider(
            "Chunks relevantes (k)",
            min_value=1,
            max_value=10,
            value=4,
            help="Número de fragmentos a recuperar del documento"
        )

        st.markdown("---")

        # Botón para limpiar índice
        if st.button("🗑️ Limpiar índice FAISS", help="Elimina el índice guardado y fuerza reconstrucción"):
            if os.path.exists(INDEX_PATH):
                try:
                    import shutil
                    if os.path.isdir(INDEX_PATH):
                        shutil.rmtree(INDEX_PATH)
                    st.success("✅ Índice eliminado")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error eliminando índice: {e}")
            else:
                st.info("ℹ️ No hay índice para eliminar")

        st.markdown("---")
        st.markdown("### 📊 Estado")
        if os.path.exists(INDEX_PATH):
            st.success("✅ Índice FAISS presente")
        else:
            st.info("ℹ️ No hay índice guardado")

        # Verificar API key
        if os.getenv("MISTRAL_API_KEY"):
            st.success("✅ API Key de Mistral configurada")
        else:
            st.warning("⚠️ API Key de Mistral no encontrada")

    # Main content
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📤 Cargar documento")
        uploaded_file = st.file_uploader(
            "Sube un archivo PDF",
            type=["pdf"],
            help="El PDF se procesará y se creará un índice para búsquedas"
        )

    # Procesar PDF si se sube
    db = None
    if uploaded_file is not None:
        # Guardar PDF temporalmente
        pdf_path = os.path.join("data", uploaded_file.name)
        os.makedirs("data", exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Ingerir PDF al índice
        with st.spinner("🔄 Procesando PDF y construyendo índice FAISS..."):
            try:
                db = ingest_pdf_to_index(pdf_path, model_name=embeddings_model)
                st.success(f"✅ Documento '{uploaded_file.name}' procesado exitosamente")
            except Exception as e:
                st.error(f"❌ Error procesando PDF: {e}")
                return

        # Vista previa del documento
        with col2:
            st.subheader("👁️ Vista previa")
            try:
                preview_text = read_pdf(pdf_path)[:1500]
                st.text_area(
                    "Primeros caracteres del documento",
                    value=preview_text,
                    height=200,
                    disabled=True
                )
                st.caption(f"📊 Total: {len(read_pdf(pdf_path))} caracteres")
            except Exception as e:
                st.warning(f"⚠️ No se pudo generar vista previa: {e}")

    # Separador
    st.markdown("---")

    # Sección de consulta
    st.subheader("💬 Haz una pregunta")

    query = st.text_input(
        "Escribe tu pregunta sobre el documento",
        placeholder="Ej: ¿Cuál es el tema principal del documento?",
        help="La pregunta se buscará en el índice semántico del PDF"
    )

    # Inicializar LLM
    llm = get_mistral_llm(mistral_model)

    # Botón de consulta
    if st.button("🔍 Preguntar", type="primary", use_container_width=True):
        if db is None:
            st.error("❌ Primero debes subir un PDF para poder hacer preguntas")
            return

        if not query.strip():
            st.warning("⚠️ Por favor escribe una pregunta")
            return

        # Búsqueda de chunks relevantes
        with st.spinner("🔍 Buscando información relevante en el documento..."):
            try:
                results: List[Tuple[str, float]] = similarity_search(db, query, k=top_k)
            except Exception as e:
                st.error(f"❌ Error en búsqueda semántica: {e}")
                return

        # Mostrar contexto recuperado
        st.markdown("### 📚 Contexto recuperado")
        st.caption(f"Los {len(results)} fragmentos más relevantes del documento:")

        for i, (chunk, score) in enumerate(results, start=1):
            with st.expander(f"📄 Fragmento #{i} — Similaridad: {score:.4f}"):
                st.write(chunk)

        # Generar respuesta con Mistral (si está disponible)
        if llm is None:
            st.info("ℹ️ Configura `MISTRAL_API_KEY` en `.env` para habilitar generación de respuestas con IA")
            return

        st.markdown("### 🤖 Respuesta generada por Mistral")

        with st.spinner("🤖 Generando respuesta con Mistral AI..."):
            try:
                answer = generate_answer_with_mistral(llm, query, results)
                st.markdown(answer)
            except Exception as e:
                st.error(f"❌ Error generando respuesta: {e}")

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <p>Hecho con ❤️ usando Streamlit, LangChain, FAISS y Mistral AI</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
