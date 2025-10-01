# 🚀 Guía de Inicio Rápido - PaperWhisper

## 📋 Prerrequisitos

- **Python 3.8+** instalado
- **Cuenta de Mistral AI** (gratuita): [console.mistral.ai](https://console.mistral.ai/)
- **Git** (opcional, para clonar el repo)

---

## ⚡ Instalación Rápida (Método 1: Automático)

```bash
# 1. Navegar al directorio del proyecto
cd paperwhisper

# 2. Ejecutar script de instalación
./setup.sh

# 3. Editar .env y agregar tu API key
nano .env  # o usa tu editor favorito

# 4. Ejecutar la app
source .venv/bin/activate
streamlit run app.py
```

---

## 🔧 Instalación Manual (Método 2)

### Paso 1: Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### Paso 2: Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 3: Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu MISTRAL_API_KEY
nano .env
```

Tu archivo `.env` debe verse así:

```env
MISTRAL_API_KEY=tu_api_key_aqui
EMBEDDINGS_MODEL=sentence-transformers/all-MiniLM-L6-v2
DATA_DIR=./data
```

### Paso 4: Ejecutar la aplicación

```bash
streamlit run app.py
```

La app se abrirá automáticamente en tu navegador en `http://localhost:8501`

---

## 🎯 Cómo Usar PaperWhisper

### 1️⃣ Subir un PDF

1. Haz clic en **"Sube un archivo PDF"**
2. Selecciona tu PDF (papers, documentos, libros, etc.)
3. Espera a que se procese (verás un spinner)
4. ✅ Verás "Documento procesado exitosamente"

### 2️⃣ Hacer Preguntas

1. Escribe tu pregunta en el campo de texto
2. Haz clic en **"🔍 Preguntar"**
3. Espera la búsqueda semántica
4. Revisa los fragmentos relevantes encontrados
5. Lee la respuesta generada por Mistral

### 3️⃣ Configurar Opciones (Sidebar)

**Modelo de embeddings:**
- Por defecto: `sentence-transformers/all-MiniLM-L6-v2`
- Puedes cambiar a otros modelos de Hugging Face

**Modelo de Mistral:**
- `mistral-small-latest` - Rápido y económico (recomendado)
- `mistral-medium-latest` - Balance calidad/precio
- `mistral-large-latest` - Máxima calidad
- `open-mistral-7b` - Open source, gratuito
- `open-mixtral-8x7b` - Open source, más potente

**Chunks relevantes (k):**
- Ajusta cuántos fragmentos recuperar (1-10)
- Más chunks = más contexto, pero puede ser ruidoso
- Recomendado: 3-5 chunks

### 4️⃣ Gestionar Índice

**Limpiar índice FAISS:**
- Útil si subes un nuevo PDF y quieres forzar reconstrucción
- Click en "🗑️ Limpiar índice FAISS" en sidebar

---

## 💡 Consejos de Uso

### Para Mejores Resultados

✅ **DO:**
- Hacer preguntas específicas y claras
- Usar términos que probablemente aparezcan en el documento
- Probar con diferentes valores de top-k si no encuentras respuestas
- Revisar los fragmentos recuperados para verificar relevancia

❌ **DON'T:**
- Hacer preguntas muy generales o ambiguas
- Esperar respuestas sobre información que no está en el PDF
- Subir PDFs escaneados sin OCR (no se extraerá texto)

### Tipos de Preguntas Efectivas

```
✅ "¿Cuál es la metodología utilizada en el estudio?"
✅ "¿Qué resultados se obtuvieron en el experimento X?"
✅ "¿Cuáles son las limitaciones mencionadas?"
✅ "¿Qué dice el documento sobre [tema específico]?"

❌ "Dime todo sobre el documento"
❌ "¿Es esto verdad?" (sin contexto específico)
❌ "¿Qué opinas del tema?" (el modelo no opina, solo cita)
```

---

## 🧪 Verificar Instalación

Ejecuta el script de pruebas:

```bash
python test_rag_engine.py
```

Deberías ver:

```
🧪 SUITE DE PRUEBAS - PaperWhisper RAG Engine
...
✅ PASS - Imports
✅ PASS - Embeddings
✅ PASS - Text Splitting
✅ PASS - FAISS Index
✅ PASS - Mistral Connection

🎯 Resultado: 5/5 pruebas exitosas
🎉 ¡Todas las pruebas pasaron!
```

---

## ❓ Solución de Problemas

### Error: "MISTRAL_API_KEY no configurada"

**Solución:** Edita tu archivo `.env` y agrega tu API key de Mistral.

```bash
# Obtén tu API key en: https://console.mistral.ai/
MISTRAL_API_KEY=tu_clave_aqui
```

### Error: "No se encontró índice en: data/faiss_index/"

**Solución:** Esto es normal la primera vez. El índice se creará al subir un PDF.

### Error: "Package X is not installed"

**Solución:** Reinstala las dependencias:

```bash
pip install -r requirements.txt
```

### La app no responde / se cuelga

**Posibles causas:**
1. PDF muy grande → Espera más tiempo o divide el PDF
2. Sin conexión a internet → Los embeddings se descargan la primera vez
3. Modelo de Mistral no responde → Verifica tu API key y cuota

### Los resultados no son relevantes

**Soluciones:**
- Aumenta el número de chunks (k) en el sidebar
- Reformula tu pregunta con términos más específicos
- Verifica que el PDF se procesó correctamente (revisa preview)
- Limpia el índice y reconstruye

---

## 🔒 Seguridad

⚠️ **IMPORTANTE:**
- **NUNCA** compartas tu `.env` o tu `MISTRAL_API_KEY`
- **NUNCA** commitees `.env` a git (ya está en `.gitignore`)
- Si expones tu API key, regenerala inmediatamente en console.mistral.ai

---

## 📊 Uso de API de Mistral

### Costos Aproximados (Enero 2025)

- **mistral-small-latest**: ~$0.002 / 1K tokens
- **mistral-medium-latest**: ~$0.006 / 1K tokens
- **mistral-large-latest**: ~$0.012 / 1K tokens
- **open-mistral-7b**: Gratis (con límites)
- **open-mixtral-8x7b**: Gratis (con límites)

💡 **Tip:** Usa `mistral-small-latest` para desarrollo. Es rápido y económico.

### Límites de Cuota

Si recibes error de cuota:
1. Verifica tu plan en [console.mistral.ai](https://console.mistral.ai/)
2. Cambia a un modelo open-source (gratuito)
3. Espera a que se renueve tu cuota

---

## 🎓 Recursos Adicionales

- **Documentación Mistral AI**: [docs.mistral.ai](https://docs.mistral.ai/)
- **LangChain Docs**: [python.langchain.com](https://python.langchain.com/)
- **FAISS**: [github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss)
- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io/)

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa `IMPLEMENTATION.md` para detalles técnicos
2. Revisa `CLAUDE.md` para arquitectura del proyecto
3. Ejecuta `test_rag_engine.py` para diagnóstico
4. Busca en Issues del repositorio
5. Crea un nuevo Issue con detalles del error

---

## 🎉 ¡Listo!

Ya estás listo para conversar con tus documentos. Empieza subiendo un PDF y haciendo preguntas.

**Happy RAG-ing! 📄✨**
