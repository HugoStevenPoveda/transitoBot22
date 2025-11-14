#!/usr/bin/env python3
"""
Script de prueba para el endpoint /api/v1/anthropic
"""
import requests
import json

# URL del endpoint
BASE_URL = "http://localhost:8000"
ENDPOINT = f"{BASE_URL}/api/v1/anthropic"

# Request de prueba
test_request = {
    "context": {
        "system": "Eres un asistente experto en el Código Nacional de Tránsito de Colombia",
        "user": "Usuario consultando sobre infracciones de tránsito"
    },
    "pregunta": "¿Cuál es la multa por exceso de velocidad?",
    "entidades": [
        {
            "tipo": "infraccion",
            "valor": "exceso_velocidad"
        }
    ],
    "intencion": "consultar_multa"
}

print("=" * 60)
print("🧪 PRUEBA DEL ENDPOINT ANTHROPIC")
print("=" * 60)
print(f"\n📍 URL: {ENDPOINT}")
print(f"\n📤 Request:")
print(json.dumps(test_request, indent=2, ensure_ascii=False))

try:
    print("\n⏳ Enviando request...")
    response = requests.post(ENDPOINT, json=test_request, timeout=30)

    print(f"\n📊 Status Code: {response.status_code}")

    if response.status_code == 200:
        print("✅ SUCCESS!")
        result = response.json()
        print(f"\n📥 Response:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n🤖 Modelo usado: {result['model_used']}")
        print(f"⏱️ Tiempo de procesamiento: {result['processing_time']:.2f}s")
        print(f"\n💬 Respuesta:")
        print("-" * 60)
        print(result['answer'])
        print("-" * 60)
    else:
        print("❌ ERROR!")
        print(f"Response: {response.text}")

except requests.exceptions.ConnectionError:
    print("❌ ERROR: No se pudo conectar al servidor")
    print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print("   Ejecuta: python run.py")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 60)
