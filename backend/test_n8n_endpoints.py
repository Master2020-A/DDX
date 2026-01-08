import requests
import sys

BASE_URL = "http://localhost:8612"


def test_endpoint(endpoint):
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        print(f"✅ {endpoint} -> {response.status_code}")
        return response.status_code
    except requests.exceptions.ConnectionError:
        print(f"❌ {endpoint} -> Backend no está corriendo")
        return None
    except Exception as e:
        print(f"❌ {endpoint} -> Error: {e}")
        return None


print("🔍 Verificando endpoints de N8N...\n")

endpoints = [
    "/api/n8n/config",
    "/api/n8n/config/stats",
    "/api/n8n/events",
    "/api/n8n/workflows/templates",
]

results = {}
for endpoint in endpoints:
    results[endpoint] = test_endpoint(endpoint)

print("\n📊 Resumen:")
if all(v is not None for v in results.values()):
    print("✅ Backend está corriendo")
    if all(v != 404 for v in results.values()):
        print("✅ Todos los endpoints están disponibles")
    else:
        print(
            "⚠️ Algunos endpoints devuelven 404 (puede ser normal si no hay configuración)"
        )
else:
    print("❌ Backend NO está corriendo. Inicia el backend con:")
    print("   cd backend")
    print("   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8612")
    sys.exit(1)
