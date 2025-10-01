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

    # Header con imagen adaptable al tema
    st.markdown("""
        <style>
        /* Mostrar logo oscuro por defecto (modo día) */
        .logo-light {
            display: block;
        }
        .logo-dark {
            display: none;
        }

        /* En modo oscuro, invertir */
        @media (prefers-color-scheme: dark) {
            .logo-light {
                display: none;
            }
            .logo-dark {
                display: block;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo para modo día
        st.markdown('<div class="logo-light">', unsafe_allow_html=True)
        st.image("ppaper-dia.png", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Logo para modo noche
        st.markdown('<div class="logo-dark">', unsafe_allow_html=True)
        st.image("ppaper.png", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

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
        if os.path.exists(INDEX_PATH):
            st.markdown("🟢 **Índice:** Listo")
        else:
            st.markdown("⚪ **Índice:** Sin crear")

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
    st.markdown("### 📤 Paso 1: Sube tu documento")

    uploaded_file = st.file_uploader(
        "Arrastra un PDF aquí o haz clic para seleccionar",
        type=["pdf"],
        help="El PDF se procesará automáticamente para búsquedas",
        label_visibility="collapsed"
    )

    # Procesar PDF si se sube
    db = None
    if uploaded_file is not None:
        # Guardar PDF temporalmente
        pdf_path = os.path.join("data", uploaded_file.name)
        os.makedirs("data", exist_ok=True)

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Ingerir PDF al índice con mejor feedback
        with st.spinner("🔄 Procesando tu documento..."):
            try:
                db = ingest_pdf_to_index(pdf_path, model_name=embeddings_model)
                st.success(f"✅ **{uploaded_file.name}** listo para consultas")
            except Exception as e:
                st.error(f"❌ Error procesando PDF: {e}")
                return

        # Vista previa del documento en un expander
        with st.expander("👁️ Ver vista previa del documento", expanded=False):
            try:
                preview_text = read_pdf(pdf_path)[:1500]
                st.text_area(
                    "Primeros 1500 caracteres",
                    value=preview_text,
                    height=250,
                    disabled=True,
                    label_visibility="collapsed"
                )
                total_chars = len(read_pdf(pdf_path))
                st.caption(f"📊 Documento completo: {total_chars:,} caracteres")
            except Exception as e:
                st.warning(f"⚠️ No se pudo generar vista previa: {e}")

        st.markdown("---")

    # Sección de consulta con mejor diseño
    st.markdown("### 💬 Paso 2: Haz tu pregunta")

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

    # Footer mejorado
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; padding: 1rem 0;'>
            <p style='color: #666; font-size: 0.9rem;'>
                Hecho con ❤️ usando <strong>Mistral AI</strong>, <strong>LangChain</strong> y <strong>FAISS</strong>
            </p>
            <p style='color: #999; font-size: 0.8rem; margin-top: 0.5rem;'>
                <a href='https://github.com/antuansabe/PaperWhisper' target='_blank' style='color: #FF4B4B; text-decoration: none;'>
                    ⭐ GitHub
                </a> •
                <a href='./QUICKSTART.md' style='color: #FF4B4B; text-decoration: none;'>
                    📖 Docs
                </a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
