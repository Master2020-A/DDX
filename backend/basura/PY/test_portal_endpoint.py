import requests
import json

# Probar el endpoint del dashboard
paciente_id = "49bfb1e1-699c-4161-90cd-9162c226259c"
url = f"http://localhost:8612/api/portal-paciente/dashboard/{paciente_id}"

print(f"Probando endpoint: {url}")
print("-" * 80)

try:
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print("-" * 80)

    if response.status_code == 200:
        print("SUCCESS! Respuesta:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"ERROR {response.status_code}:")
        print(response.text)

except Exception as e:
    print(f"Error de conexión: {e}")

# Probar si el endpoint base existe
print("\n" + "=" * 80)
print("Probando endpoint base de portal-paciente...")
print("=" * 80)

try:
    # Probar listar citas
    url_citas = f"http://localhost:8612/api/portal-paciente/citas/{paciente_id}"
    print(f"\nProbando: {url_citas}")
    response = requests.get(url_citas)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        print(f"Citas encontradas: {len(response.json())}")
    else:
        print(f"Error: {response.text}")

except Exception as e:
    print(f"Error: {e}")

# Verificar que el servidor está corriendo
print("\n" + "=" * 80)
print("Verificando servidor...")
print("=" * 80)

try:
    response = requests.get("http://localhost:8612/docs")
    print(f"Servidor FastAPI está corriendo (Status: {response.status_code})")
except Exception as e:
    print(f"ERROR: Servidor no está corriendo - {e}")
