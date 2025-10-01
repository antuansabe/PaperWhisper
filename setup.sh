#!/bin/bash

# Script de instalación para PaperWhisper
# Configura el entorno virtual e instala todas las dependencias

echo "🚀 Iniciando instalación de PaperWhisper..."

# Verificar que Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 no está instalado"
    echo "Por favor instala Python 3.8 o superior"
    exit 1
fi

# Mostrar versión de Python
PYTHON_VERSION=$(python3 --version)
echo "✅ Python encontrado: $PYTHON_VERSION"

# Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source .venv/bin/activate

# Actualizar pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip --quiet

# Instalar dependencias
echo "📚 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

# Verificar instalación
echo ""
echo "🔍 Verificando instalación..."

# Listar paquetes clave instalados
echo "Paquetes instalados:"
pip list | grep -E "(streamlit|langchain|faiss|mistral|sentence-transformers)"

# Configurar .env si no existe
if [ ! -f ".env" ]; then
    echo ""
    echo "📝 Creando archivo .env desde .env.example..."
    cp .env.example .env
    echo "✅ Archivo .env creado"
    echo "⚠️  IMPORTANTE: Edita el archivo .env y agrega tu MISTRAL_API_KEY"
else
    echo "✅ Archivo .env ya existe"
fi

# Crear directorio data si no existe
if [ ! -d "data" ]; then
    mkdir -p data
    echo "✅ Directorio data/ creado"
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Edita el archivo .env y agrega tu MISTRAL_API_KEY"
echo "   2. Activa el entorno virtual: source .venv/bin/activate"
echo "   3. Ejecuta la aplicación: streamlit run app.py"
echo ""
