"""
Script de prueba para validar el RAG engine de PaperWhisper
Ejecutar con: python test_rag_engine.py
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_imports():
    """Prueba que todas las dependencias se puedan importar"""
    print("🔍 Probando imports...")
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_mistralai import ChatMistralAI
        from pypdf import PdfReader
        import streamlit
        print("✅ Todos los imports exitosos")
        return True
    except ImportError as e:
        print(f"❌ Error en imports: {e}")
        return False


def test_embeddings():
    """Prueba la generación de embeddings"""
    print("\n🔍 Probando generación de embeddings...")
    try:
        from src.rag_engine import generate_embeddings

        embeddings = generate_embeddings()

        # Generar embedding de prueba
        test_text = "Este es un texto de prueba para embeddings"
        embedding = embeddings.embed_query(test_text)

        print(f"✅ Embedding generado: dimensión {len(embedding)}")
        return True
    except Exception as e:
        print(f"❌ Error generando embeddings: {e}")
        return False


def test_text_splitting():
    """Prueba el chunking de texto"""
    print("\n🔍 Probando división de texto...")
    try:
        from src.rag_engine import split_into_chunks

        test_text = """
        Este es un documento de prueba muy largo que necesita ser dividido en chunks.
        El proceso de chunking es fundamental para RAG porque permite buscar información
        de manera más granular. Cada chunk debe mantener coherencia semántica.
        """ * 10

        chunks = split_into_chunks(test_text, chunk_size=200, chunk_overlap=50)

        print(f"✅ Texto dividido en {len(chunks)} chunks")
        print(f"   Ejemplo de chunk: {chunks[0][:100]}...")
        return True
    except Exception as e:
        print(f"❌ Error en chunking: {e}")
        return False


def test_faiss_index():
    """Prueba la creación de un índice FAISS simple"""
    print("\n🔍 Probando creación de índice FAISS...")
    try:
        from src.rag_engine import generate_embeddings, build_faiss_index

        # Crear chunks de prueba
        test_chunks = [
            "Python es un lenguaje de programación de alto nivel",
            "FAISS es una biblioteca para búsqueda de similitud",
            "RAG combina recuperación y generación de texto",
            "Los embeddings representan texto como vectores"
        ]

        embeddings = generate_embeddings()
        db = build_faiss_index(test_chunks, embeddings)

        # Probar búsqueda
        results = db.similarity_search_with_score("¿Qué es Python?", k=2)

        print(f"✅ Índice FAISS creado con {len(test_chunks)} documentos")
        print(f"   Resultado de búsqueda: '{results[0][0].page_content}' (score: {results[0][1]:.4f})")
        return True
    except Exception as e:
        print(f"❌ Error en FAISS: {e}")
        return False


def test_mistral_connection():
    """Prueba la conexión con Mistral AI"""
    print("\n🔍 Probando conexión con Mistral AI...")

    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key or api_key == "your_mistral_api_key_here":
        print("⚠️  MISTRAL_API_KEY no configurada, saltando prueba de Mistral")
        return True

    try:
        from langchain_mistralai import ChatMistralAI

        llm = ChatMistralAI(
            model="mistral-small-latest",
            temperature=0,
            max_tokens=50
        )

        response = llm.invoke([
            {"role": "user", "content": "Di 'hola' en una palabra"}
        ])

        print(f"✅ Conexión con Mistral exitosa")
        print(f"   Respuesta: {response.content}")
        return True
    except Exception as e:
        print(f"❌ Error conectando con Mistral: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 SUITE DE PRUEBAS - PaperWhisper RAG Engine")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Embeddings", test_embeddings),
        ("Text Splitting", test_text_splitting),
        ("FAISS Index", test_faiss_index),
        ("Mistral Connection", test_mistral_connection)
    ]

    results = []
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))

    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print(f"\n🎯 Resultado: {passed}/{total} pruebas exitosas")

    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron!")
        return 0
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
