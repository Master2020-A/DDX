"""
Script de diagnóstico para verificar el estado de los endpoints de N8N
"""

import httpx
import asyncio


async def diagnosticar_n8n():
    """Diagnosticar el estado de los endpoints de N8N"""

    base_url = "http://localhost:8612"

    endpoints = [
        "/api/n8n/config",
        "/api/n8n/config/stats",
        "/api/n8n/events",
        "/api/n8n/workflows/templates",
        "/docs",  # Para verificar que el backend está corriendo
    ]

    print("🔍 Diagnosticando endpoints de N8N...\n")

    async with httpx.AsyncClient() as client:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            try:
                print(f"Probando: {url}")
                response = await client.get(url, timeout=5.0)

                if response.status_code == 200:
                    print(f"  ✅ {response.status_code} - OK")
                elif response.status_code == 401:
                    print(
                        f"  ⚠️  {response.status_code} - Requiere autenticación (NORMAL)"
                    )
                elif response.status_code == 404:
                    print(f"  ❌ {response.status_code} - Endpoint NO ENCONTRADO")
                else:
                    print(f"  ⚠️  {response.status_code} - {response.text[:100]}")

            except httpx.ConnectError:
                print(f"  ❌ ERROR: No se puede conectar al backend")
                print(f"     ¿El backend está corriendo en {base_url}?")
                break
            except Exception as e:
                print(f"  ❌ ERROR: {str(e)}")

        print("\n" + "=" * 60)
        print("📊 RESUMEN:")
        print("=" * 60)

        # Verificar si el backend está corriendo
        try:
            response = await client.get(f"{base_url}/docs")
            if response.status_code == 200:
                print("✅ Backend está corriendo")
            else:
                print("❌ Backend no responde correctamente")
        except:
            print("❌ Backend NO está corriendo")
            print("\n🔧 SOLUCIÓN:")
            print("   Inicia el backend con:")
            print("   cd C:\\Users\\Master\\Documents\\DDX\\backend")
            print("   uvicorn app.main:app --reload --port 8612")
            return

        # Verificar endpoints de N8N
        try:
            response = await client.get(f"{base_url}/api/n8n/config")
            if response.status_code == 404:
                print("❌ Endpoints de N8N NO están cargados")
                print("\n🔧 POSIBLES CAUSAS:")
                print("   1. El router de N8N no se cargó correctamente")
                print("   2. Hay un error en app/api/n8n.py")
                print("   3. El router no está registrado en main.py")
                print("\n🔧 SOLUCIÓN:")
                print("   1. Revisa los logs del backend al iniciar")
                print("   2. Busca errores relacionados con 'n8n'")
                print("   3. Verifica que no haya errores de importación")
            elif response.status_code == 401:
                print("✅ Endpoints de N8N están cargados (requieren autenticación)")
            elif response.status_code == 500:
                print("⚠️  Endpoints de N8N cargados pero hay error interno")
                print(f"   Respuesta: {response.text[:200]}")
        except Exception as e:
            print(f"❌ Error al verificar endpoints: {e}")


if __name__ == "__main__":
    asyncio.run(diagnosticar_n8n())
