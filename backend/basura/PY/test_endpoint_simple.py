import asyncio
import sys

sys.path.insert(0, "C:/Users/Master/Documents/DDX/backend")

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

# Listar todas las rutas disponibles
print("=" * 80)
print("RUTAS DISPONIBLES EN LA APLICACIÓN:")
print("=" * 80)

portal_routes = []
for route in app.routes:
    if hasattr(route, "path") and hasattr(route, "methods"):
        if "portal" in route.path.lower():
            portal_routes.append(f"{list(route.methods)[0]:6} {route.path}")
            print(f"✅ {list(route.methods)[0]:6} {route.path}")

if not portal_routes:
    print("\n❌ NO SE ENCONTRARON RUTAS DEL PORTAL DEL PACIENTE")
    print("\nBuscando todas las rutas con /api/:")
    for route in app.routes:
        if hasattr(route, "path") and "/api/" in route.path:
            if hasattr(route, "methods"):
                print(f"   {list(route.methods)[0]:6} {route.path}")

print("\n" + "=" * 80)
print("PROBANDO ENDPOINT DEL DASHBOARD:")
print("=" * 80)

paciente_id = "49bfb1e1-699c-4161-90cd-9162c226259c"
url = f"/api/portal-paciente/dashboard/{paciente_id}"

print(f"\nURL: {url}")
response = client.get(url)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("✅ SUCCESS!")
    print(response.json())
elif response.status_code == 404:
    print("❌ 404 - Endpoint no encontrado")
    print(f"Detalle: {response.text}")
else:
    print(f"❌ Error {response.status_code}")
    print(response.text)
