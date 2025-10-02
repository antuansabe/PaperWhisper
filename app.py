"""
PaperWhisper - Interfaz Streamlit
Aplicación para conversar con documentos PDF usando RAG + Mistral AI
"""

import os
import gc
from typing import List, Tuple, Optional
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

from src.rag_engine import (
    ingest_pdf_from_buffer,
    similarity_search,
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

    # Google Analytics (movido aquí para evitar interferencia con renderizado)
    st.components.v1.html("""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-9MQTPC9RJK"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-9MQTPC9RJK');
    </script>
    """, height=0)

    # CSS para optimización móvil
    st.markdown("""
        <style>
        /* Optimización móvil */
        @media (max-width: 768px) {
            /* Reducir padding general */
            .main .block-container {
                padding-top: 1rem !important;
                padding-bottom: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            /* Reducir espacios entre secciones */
            .element-container {
                margin-bottom: 0.5rem !important;
            }

            /* Títulos más compactos */
            h1, h2, h3 {
                margin-top: 0.5rem !important;
                margin-bottom: 0.5rem !important;
            }

            /* File uploader más compacto */
            [data-testid="stFileUploader"] {
                padding: 0.5rem !important;
            }

            /* Botones full width en móvil */
            .stButton button {
                width: 100% !important;
            }

            /* Text areas más compactas */
            .stTextArea textarea {
                min-height: 80px !important;
            }

            /* Expanders más compactos */
            .streamlit-expanderHeader {
                font-size: 0.9rem !important;
            }
        }

        /* Logo responsive */
        @media (max-width: 768px) {
            img {
                max-width: 100% !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    # Header con logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("ppaper.png", use_container_width=True)

    st.markdown("---")

    # Mensaje de privacidad simple
    st.markdown(
        """
        <p style='text-align: center; color: #666; font-size: 0.9rem; margin: 0.5rem 0 1rem 0;'>
            🔒 Tus documentos se procesan <strong>solo en memoria</strong> — No guardamos archivos
        </p>
        """,
        unsafe_allow_html=True
    )

    # Sidebar - Configuración
    with st.sidebar:
        st.markdown("### ⚙️ Configuración")
        st.markdown("")

        # Sección de modelos
        with st.expander("🤖 Modelos de IA", expanded=True):
            # Modelo de Mistral
            mistral_model = st.selectbox(
                "Modelo de IA",
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

            # Modelo de embeddings (oculto por defecto)
            embeddings_model = os.getenv("EMBEDDINGS_MODEL", DEFAULT_MODEL_NAME)

        # Sección de parámetros
        with st.expander("🎛️ Parámetros", expanded=True):
            # Top-K chunks
            top_k = st.slider(
                "Fragmentos a recuperar",
                min_value=1,
                max_value=10,
                value=4,
                help="Número de fragmentos relevantes del documento"
            )

        st.markdown("---")

        # Botón para limpiar sesión
        if st.button("🗑️ Limpiar sesión", help="Elimina el documento actual y libera la memoria"):
            # Eliminar referencias
            st.session_state.faiss_db = None
            st.session_state.uploaded_filename = None
            st.session_state.session_id = None

            # Forzar garbage collection para liberar memoria
            gc.collect()

            st.success("✅ Sesión y memoria limpiadas")
            st.rerun()

        st.markdown("---")

        # Estado del sistema con mejor diseño
        st.markdown("### 📊 Estado del Sistema")

        # API Key status
        api_key = os.getenv("MISTRAL_API_KEY")
        if api_key and api_key != "your_mistral_api_key_here":
            st.markdown("🟢 **IA:** Conectada")
        else:
            st.markdown("🔴 **IA:** Desconectada")
            st.caption("Configura `MISTRAL_API_KEY` en `.env`")

        # Índice status
        if st.session_state.get("faiss_db") is not None:
            st.markdown("🟢 **Documento:** Cargado")
            if st.session_state.get("uploaded_filename"):
                st.caption(f"📄 {st.session_state.uploaded_filename}")
        else:
            st.markdown("⚪ **Documento:** Sin cargar")

        st.markdown("")

        # Info adicional
        with st.expander("ℹ️ Acerca de"):
            st.markdown("""
                **PaperWhisper** v1.0

                Conversa con tus documentos PDF usando:
                - 🤖 Mistral AI
                - 🔍 FAISS
                - 🧬 HuggingFace

                [GitHub](https://github.com/antuansabe/PaperWhisper) • [Docs](./QUICKSTART.md)
            """)

    # Main content con diseño mejorado
    st.markdown('<h3 style="margin-bottom: 0.5rem;">📤 Paso 1: Sube tu documento</h3>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Arrastra un PDF aquí o haz clic para seleccionar",
        type=["pdf"],
        help="El PDF se procesará automáticamente para búsquedas",
        label_visibility="collapsed"
    )

    # Inicializar session_state para el índice FAISS (aislamiento por usuario)
    if "faiss_db" not in st.session_state:
        st.session_state.faiss_db = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = None

    # Procesar PDF si se sube
    db = None
    if uploaded_file is not None:
        # Si es un archivo nuevo, recrear el índice
        if st.session_state.uploaded_filename != uploaded_file.name:
            # PRIVACIDAD: Procesar PDF directamente desde memoria (BytesIO)
            # No se guarda NADA en disco
            pdf_buffer = BytesIO(uploaded_file.getvalue())

            # Ingerir PDF al índice EN MEMORIA (100% privado)
            with st.spinner("🔄 Procesando tu documento en memoria..."):
                try:
                    db = ingest_pdf_from_buffer(
                        pdf_buffer,
                        model_name=embeddings_model
                    )
                    st.session_state.faiss_db = db
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.success(f"✅ **{uploaded_file.name}** procesado de forma segura (solo en memoria)")
                except Exception as e:
                    st.error(f"❌ Error procesando PDF: {e}")
                    return
        else:
            # Usar índice existente de la sesión
            db = st.session_state.faiss_db
            if db:
                st.success(f"✅ **{uploaded_file.name}** listo para consultas")

        # Vista previa del documento en un expander
        with st.expander("👁️ Ver vista previa del documento", expanded=False):
            try:
                # Leer directamente del uploaded_file buffer
                from io import BytesIO
                from pypdf import PdfReader

                pdf_bytes = BytesIO(uploaded_file.getvalue())
                reader = PdfReader(pdf_bytes)
                preview_text = ""
                for page in reader.pages[:3]:  # Primeras 3 páginas
                    preview_text += page.extract_text()

                preview_text = preview_text[:1500]
                st.text_area(
                    "Primeros 1500 caracteres",
                    value=preview_text,
                    height=250,
                    disabled=True,
                    label_visibility="collapsed"
                )

                # Contar caracteres totales
                total_text = ""
                pdf_bytes.seek(0)
                reader = PdfReader(pdf_bytes)
                for page in reader.pages:
                    total_text += page.extract_text()
                st.caption(f"📊 Documento completo: {len(total_text):,} caracteres")
            except Exception as e:
                st.warning(f"⚠️ No se pudo generar vista previa: {e}")

    # Sección de consulta con mejor diseño
    st.markdown('<h3 style="margin-top: 0.5rem; margin-bottom: 0.5rem;">💬 Paso 2: Haz tu pregunta</h3>', unsafe_allow_html=True)

    query = st.text_input(
        "Pregunta",
        placeholder="Ej: ¿Cuál es el tema principal del documento?",
        help="Pregunta en lenguaje natural sobre el contenido del PDF",
        label_visibility="collapsed"
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

        # Generar respuesta con Mistral primero (si está disponible)
        if llm is None:
            st.warning("⚠️ Configura `MISTRAL_API_KEY` en `.env` para habilitar respuestas con IA")
            st.info("📚 Mostrando solo búsqueda semántica:")
        else:
            st.markdown("### 🤖 Respuesta")

            with st.spinner("🤖 Generando respuesta..."):
                try:
                    answer = generate_answer_with_mistral(llm, query, results)

                    # Mostrar respuesta en un contenedor destacado
                    st.markdown(f"""
                        <div style='background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #FF4B4B;'>
                            {answer}
                        </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Error generando respuesta: {e}")

        # Mostrar contexto recuperado en expander
        st.markdown("")
        with st.expander(f"📚 Ver fragmentos relevantes ({len(results)} encontrados)", expanded=False):
            st.caption("Los fragmentos más similares a tu pregunta:")
            for i, (chunk, score) in enumerate(results, start=1):
                similarity_pct = (1 - score) * 100  # Convertir distancia a porcentaje
                st.markdown(f"**Fragmento {i}** — Relevancia: {similarity_pct:.1f}%")
                st.text(chunk)
                st.markdown("---")

    # Footer mejorado con mensaje de privacidad
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # Mensaje de privacidad destacado
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 1rem;'>
            <p style='color: #1f1f1f; font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem;'>
                🔒 Tu privacidad es importante
            </p>
            <p style='color: #666; font-size: 0.8rem; margin: 0; line-height: 1.5;'>
                <strong>PaperWhisper procesa tus documentos solo en memoria.</strong><br>
                No guardamos archivos en disco ni usamos tus datos para entrenar modelos.<br>
                Fragmentos relevantes se envían a Mistral AI únicamente para generar respuestas.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='text-align: center; padding: 0.5rem 0;'>
            <p style='color: #666; font-size: 0.85rem; margin-bottom: 0.3rem;'>
                Hecho con ❤️ usando <strong>Mistral AI</strong>, <strong>LangChain</strong> y <strong>FAISS</strong>
            </p>
            <p style='color: #999; font-size: 0.75rem; margin: 0;'>
                <a href='https://github.com/antuansabe/PaperWhisper' target='_blank' style='color: #FF4B4B; text-decoration: none;'>
                    ⭐ GitHub
                </a> •
                <a href='https://github.com/antuansabe/PaperWhisper/blob/main/PRIVACY.md' target='_blank' style='color: #FF4B4B; text-decoration: none;'>
                    🔒 Privacidad
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
