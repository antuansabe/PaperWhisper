# 🚀 Guía de Deploy - PaperWhisper

Esta guía te ayudará a deployar PaperWhisper en **Streamlit Cloud** (100% gratis).

---

## ✅ Pre-requisitos

- [x] Código en GitHub (ya lo tienes ✅)
- [x] Cuenta de GitHub  
- [ ] API Key de Mistral AI

---

## 📝 Paso a Paso: Deploy en Streamlit Cloud

### **Paso 1: Crear Cuenta en Streamlit Cloud**

1. Ve a: **https://share.streamlit.io/**
2. Click en **"Sign up"** o **"Continue with GitHub"**
3. Autoriza a Streamlit para acceder a tus repositorios

---

### **Paso 2: Crear Nueva App**

1. En el dashboard, click **"New app"**
2. Llena el formulario:

```
Repository: antuansabe/PaperWhisper
Branch: main
Main file path: app.py
App URL (opcional): paperwhisper
```

---

### **Paso 3: Configurar Secrets (MUY IMPORTANTE)**

Antes de deployar, click en **"Advanced settings..."**

En la sección **"Secrets"**, pega esto (**reemplaza con tu API key real de Mistral**):

```toml
MISTRAL_API_KEY = "tu_api_key_real_de_mistral"
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATA_DIR = "./data"
```

> ⚠️ **IMPORTANTE**: Estos "secrets" son como variables de entorno, pero en la nube.
> Nunca se subirán a GitHub ni serán visibles públicamente.

**¿Dónde obtener tu API key?**
1. Ve a: https://console.mistral.ai/
2. Login o crea cuenta (gratis)
3. Ve a "API Keys"
4. Click "Create new key"
5. Copia la key y pégala arriba

---

### **Paso 4: Deploy!**

1. Click **"Deploy!"**
2. Espera 2-3 minutos mientras se instalan las dependencias
3. Verás logs en tiempo real

Tu app estará live en: `https://paperwhisper.streamlit.app`

---

## 🔒 Seguridad

⚠️ **NUNCA** pongas tu API key real en archivos que se suban a GitHub  
✅ **SIEMPRE** usa Streamlit Secrets para las keys  
✅ **SIEMPRE** verifica que `.env` está en `.gitignore`

---

## 📱 Compartir

Una vez deployada, comparte tu app en LinkedIn con un post como:

```
🚀 Acabo de lanzar PaperWhisper - conversa con tus PDFs usando IA!

Pruébala: https://paperwhisper.streamlit.app
Código: https://github.com/antuansabe/PaperWhisper

#AI #Python #RAG #MistralAI
```

---

¡Listo para deploy! 🎉
