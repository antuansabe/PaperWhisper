import os
from typing import List, Tuple

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from src.rag_engine import ingest_pdf_to_index, similarity_search, INDEX_PATH, DEFAULT_MODEL_NAME

load_dotenv()

st.set_page_config(page_title="PaperWhisper", page_icon="📄", layout="wide")

@st.cache_resource(show_spinner=False)
def get_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("OPENAI_API_KEY no configurada. Solo se habilita la parte de búsqueda.")
        return None
    return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"), temperature=0)


def main():
    st.title("📄 PaperWhisper – Conversa con tus PDFs")
    st.markdown("Sube un PDF, pregunta en lenguaje natural y obtén respuestas con contexto.")

    with st.sidebar:
        st.header("Ajustes")
        model_name = st.text_input("Modelo de embeddings (HF)", value=DEFAULT_MODEL_NAME)
        top_k = st.slider("Chunks relevantes (k)", min_value=1, max_value=10, value=4)
        if st.button("Limpiar índice FAISS"):
            if os.path.exists(INDEX_PATH):
                try:
                    for fname in os.listdir(INDEX_PATH):
                        os.remove(os.path.join(INDEX_PATH, fname))
                    os.rmdir(INDEX_PATH)
                except Exception:
                    pass
            st.experimental_rerun()

    uploaded_file = st.file_uploader("Sube un PDF", type=["pdf"], help="El tamaño del PDF puede afectar el tiempo de procesamiento")

    db = None
    if uploaded_file is not None:
        pdf_path = os.path.join("data", uploaded_file.name)
        os.makedirs("data", exist_ok=True)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        with st.spinner("Procesando PDF y construyendo/cargando índice FAISS..."):
            db = ingest_pdf_to_index(pdf_path, model_name=model_name)
        st.success("Índice listo.")

        # Mostrar preview de texto
        st.subheader("Vista previa del documento")
        st.caption("Primeros 1200 caracteres del documento para referencia")
        try:
            from src.rag_engine import read_pdf
            preview_text = read_pdf(pdf_path)[:1200]
            st.text_area("Contenido (parcial)", value=preview_text, height=200)
        except Exception as e:
            st.warning(f"No se pudo mostrar la vista previa: {e}")

    st.markdown("---")
    st.subheader("Consulta")
    query = st.text_input("Escribe tu pregunta sobre el PDF")
    llm = get_llm()

    if st.button("Preguntar", type="primary"):
        if db is None:
            st.error("Primero sube un PDF para construir el índice.")
            return
        if not query.strip():
            st.warning("Escribe una pregunta.")
            return

        with st.spinner("Buscando contexto relevante..."):
            results: List[Tuple[str, float]] = similarity_search(db, query, k=top_k)

        st.markdown("### Contexto utilizado (top-k)")
        for i, (chunk, score) in enumerate(results, start=1):
            with st.expander(f"Chunk #{i}  |  score={score:.4f}"):
                st.write(chunk)

        if llm is None:
            st.info("Configura OPENAI_API_KEY para habilitar la generación de respuestas.")
            return

        context = "\n\n".join([c for c, _ in results])
        prompt = (
            "Responde a la pregunta del usuario usando únicamente el contexto proporcionado.\n"
            "Si la respuesta no está en el contexto, responde 'No encuentro esa información en el PDF'.\n\n"
            f"Contexto:\n{context}\n\n"
            f"Pregunta: {query}\n"
        )
        with st.spinner("Generando respuesta con OpenAI..."):
            answer = llm.invoke(prompt).content

        st.markdown("### Respuesta")
        st.write(answer)


if __name__ == "__main__":
    main()
