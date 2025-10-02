# 🔒 Política de Privacidad - PaperWhisper

**Última actualización:** Octubre 2025

---

## Resumen Ejecutivo

**PaperWhisper procesa tus documentos solo en memoria. No guardamos archivos en disco ni usamos tus datos para entrenar modelos.**

---

## ¿Qué datos procesamos?

Cuando usas PaperWhisper, procesamos:

1. **Archivos PDF que subes**: El contenido de tus documentos
2. **Preguntas que haces**: Tus consultas en lenguaje natural sobre los documentos
3. **Fragmentos relevantes**: Secciones del documento que son relevantes para tu pregunta

---

## ¿Cómo procesamos tus datos?

### 🟢 Procesamiento Local (100% en tu sesión)

**✅ Extracción de texto del PDF**
- El PDF se procesa **directamente desde memoria** (BytesIO)
- **NUNCA se guarda en disco**
- Solo existe en RAM durante el procesamiento

**✅ Generación de embeddings (vectores)**
- Usamos el modelo local `sentence-transformers/all-MiniLM-L6-v2` de HuggingFace
- El modelo se descarga **una sola vez** y se ejecuta localmente
- **No se envían datos a servidores externos** para generar embeddings
- Telemetría de HuggingFace desactivada explícitamente

**✅ Búsqueda semántica con FAISS**
- El índice FAISS se construye y mantiene **solo en memoria**
- La búsqueda de similitud se ejecuta **100% localmente**
- **No hay llamadas a servicios cloud** para búsquedas

### 🟡 Procesamiento Externo (Mistral AI)

**⚠️ Generación de respuestas con IA**

Para generar respuestas inteligentes, enviamos a Mistral AI:
- Los fragmentos más relevantes de tu documento (típicamente 4 fragmentos de ~900 caracteres cada uno)
- Tu pregunta

**Política de Mistral AI:**
- Mistral AI **puede usar estos datos para entrenar modelos**, a menos que:
  - Hayas solicitado **Zero Data Retention (ZDR)** para tu cuenta
  - O hayas optado-out explícitamente en la configuración de tu cuenta
- Para solicitar ZDR: contacta a `support@mistral.ai` o visita https://help.mistral.ai/
- Más información: https://mistral.ai/privacy-policy/

---

## ¿Guardamos tus archivos?

**NO.** Los PDFs:

1. ✅ Se procesan **solo en memoria** (nunca tocan el disco)
2. ✅ Se eliminan **inmediatamente** después del procesamiento
3. ✅ El índice FAISS solo existe durante tu sesión
4. ✅ Al cerrar la sesión o usar "Limpiar sesión", se fuerza garbage collection

---

## ¿Usamos tus datos para entrenar modelos?

**Nosotros NO.**

PaperWhisper no entrena modelos. Somos una aplicación de código abierto que:
- Usa modelos pre-entrenados de HuggingFace (localmente)
- Usa la API de Mistral AI (externamente)

**Pero Mistral AI SÍ puede**, según su política de privacidad actual (2025):

> "Mistral AI trains its artificial intelligence models in accordance with its Privacy Policy, unless (a) Customer opted-out of training or (b) uses a Mistral AI Product that is opted-out by default."

**Cómo evitarlo:**
- Solicita **Zero Data Retention (ZDR)** a Mistral AI
- O usa el modo "Solo búsqueda" (cuando esté disponible)

---

## Tus derechos (GDPR/CCPA)

### Derecho a eliminar datos
- Click en **"🗑️ Limpiar sesión"** en cualquier momento
- Esto elimina:
  - El índice FAISS de tu sesión
  - Referencias al nombre del archivo
  - Fuerza garbage collection para liberar memoria

### Derecho de acceso
- **No guardamos datos permanentes** en PaperWhisper
- Los únicos datos que persisten están en Mistral AI (según su política)

### Derecho de oposición
- Si no aceptas enviar fragmentos a Mistral AI, **no uses la funcionalidad de respuestas con IA**
- La búsqueda semántica (solo fragmentos relevantes) es 100% local

---

## Seguridad Técnica

### Medidas implementadas:

✅ **Procesamiento en memoria:**
- PDFs procesados con `BytesIO` (buffer en RAM)
- No se usan archivos temporales en disco

✅ **Aislamiento por sesión:**
- Cada usuario tiene su propio índice FAISS en `st.session_state`
- No hay contaminación cruzada entre usuarios

✅ **Logging seguro:**
- No se registran queries de usuarios
- No se logean fragmentos de documentos
- Solo metadata técnica (número de páginas, chunks, etc.)

✅ **Limpieza de memoria:**
- Garbage collection forzado al limpiar sesión
- Referencias eliminadas explícitamente

✅ **Telemetría desactivada:**
- `HF_HUB_DISABLE_TELEMETRY=1` para HuggingFace
- No se envía metadata de uso a terceros (excepto Mistral AI)

---

## Servicios de Terceros

### HuggingFace (Embeddings)
- **Qué usamos:** Modelo `sentence-transformers/all-MiniLM-L6-v2`
- **Ejecución:** Local (CPU)
- **Datos enviados:** Ninguno (modelo descargado una vez)
- **Telemetría:** Desactivada explícitamente

### Mistral AI (LLM)
- **Qué usamos:** API de Mistral AI (modelos small/medium/large)
- **Datos enviados:** Fragmentos relevantes + pregunta del usuario
- **Retención:** Según política de Mistral AI (solicita ZDR para evitarlo)
- **Más información:** https://mistral.ai/privacy-policy/

### Streamlit Cloud (Hosting)
- **Qué usamos:** Plataforma de deploy gratuita
- **Datos enviados:** Metadata de la aplicación (no contenido de PDFs)
- **Logs:** Streamlit puede tener logs de aplicación (no controlados por nosotros)
- **Más información:** https://streamlit.io/privacy-policy

---

## Comparación con Competidores

| Característica | PaperWhisper | ChatPDF / PDF.ai | Google Drive + Gemini |
|----------------|--------------|------------------|-----------------------|
| PDFs en disco | ❌ Nunca | ⚠️ Temporal | ✅ Permanente |
| Embeddings locales | ✅ 100% local | ❌ Cloud | ❌ Cloud |
| Datos para training | ⚠️ Solo Mistral AI | ✅ Sí (política) | ✅ Sí (política) |
| Open source | ✅ Sí | ❌ No | ❌ No |
| ZDR disponible | ✅ Sí (Mistral) | ❌ No | ❌ No |

---

## Recomendaciones para Máxima Privacidad

Si manejas **documentos altamente sensibles**:

1. ✅ **Solicita ZDR a Mistral AI** antes de usar la app
2. ✅ **Revisa que tu firewall** permita solo tráfico a `api.mistral.ai`
3. ✅ **Usa "Limpiar sesión"** después de cada documento
4. ⚠️ **Considera self-hosting** si necesitas control total (código open source)
5. ⚠️ **No uses documentos con información clasificada** sin autorización

---

## Actualizaciones de esta Política

Esta política puede actualizarse para reflejar:
- Cambios en servicios de terceros (especialmente Mistral AI)
- Nuevas funcionalidades de privacidad
- Feedback de la comunidad

Versión actual: **1.0 (Octubre 2025)**

---

## Contacto

Para preguntas sobre privacidad:
- **GitHub Issues:** https://github.com/antuansabe/PaperWhisper/issues
- **Email del proyecto:** (agregar si existe)

Para ejercer derechos GDPR con Mistral AI:
- **Soporte Mistral:** support@mistral.ai
- **Help Center:** https://help.mistral.ai/

---

## Código Abierto

PaperWhisper es **100% open source**. Puedes auditar el código en:

📂 https://github.com/antuansabe/PaperWhisper

**Archivos clave de privacidad:**
- `src/rag_engine.py` (procesamiento de PDFs)
- `app.py` (gestión de sesiones)

---

**🔒 Tu privacidad es nuestra prioridad. Si tienes dudas, revisa el código o pregúntanos.**
