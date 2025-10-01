
# 📄 PaperWhisper – Conversa con tus documentos

**PaperWhisper** es una aplicación de código abierto que convierte cualquier documento PDF en un asistente conversacional inteligente. Utiliza la técnica de **RAG (Retrieval-Augmented Generation)** para responder preguntas basándose únicamente en el contenido del documento cargado.

> _Convierte cualquier PDF en un asesor experto, disponible 24/7. Con PaperWhisper, entender documentos largos es tan simple como hacer una pregunta._

---

## 🚀 Demo

<p align="center">
  <img src="demo.gif" alt="Demo de PaperWhisper" width="600"/>
</p>

> También puedes probarlo aquí: [paperwhisper.streamlit.app](https://paperwhisper.streamlit.app) ← (actualiza con tu URL cuando esté listo)

---

## 🧠 ¿Cómo funciona?

1. 🧾 Subes un PDF desde la interfaz.
2. ✂️ El documento se divide en fragmentos de texto (chunks).
3. 🧬 Se generan embeddings semánticos de cada fragmento usando un modelo open-source de Hugging Face.
4. 📚 Los embeddings se almacenan en un índice local usando FAISS.
5. ❓ El usuario hace una pregunta en lenguaje natural.
6. 🔍 Se buscan los fragmentos más relevantes en el índice vectorial.
7. 🤖 Se genera una respuesta utilizando OpenAI (GPT-3.5 o GPT-4), con los fragmentos como contexto.

---

## 🧰 Stack tecnológico

| Componente        | Herramienta                            |
|-------------------|----------------------------------------|
| LLM               | OpenAI API (GPT-3.5 o GPT-4)           |
| Embeddings        | Hugging Face – `sentence-transformers` |
| Vector store      | FAISS (local)                          |
| Orquestación      | LangChain                              |
| Procesamiento PDF | PyPDF / LangChain                      |
| Interfaz Web      | Streamlit                              |

---

## 🧪 Fases del desarrollo

### Fase 1 – Preparación
- [x] Configurar entorno virtual e instalar dependencias
- [x] Configurar archivo `.env` con la API Key de OpenAI

### Fase 2 – Ingesta de documento
- [x] Carga del PDF
- [x] Extracción y chunking del contenido

### Fase 3 – Generación y almacenamiento de embeddings
- [x] Generar embeddings con Hugging Face
- [x] Indexar en FAISS

### Fase 4 – Flujo de pregunta-respuesta
- [x] Capturar pregunta
- [x] Buscar chunks relevantes
- [x] Enviar a OpenAI para generar respuesta

### Fase 5 – Interfaz y visualización
- [x] Crear interfaz con Streamlit
- [x] Mostrar pregunta, respuesta y contexto

### Fase 6 – Deploy y publicación
- [ ] Subir a Streamlit Cloud o Hugging Face Spaces
- [ ] Agregar URL en este README
- [ ] Compartir en LinkedIn

---

## 📦 Instalación

```bash
git clone https://github.com/tuusuario/PaperWhisper.git
cd PaperWhisper
pip install -r requirements.txt