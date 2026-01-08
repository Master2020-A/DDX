#!/usr/bin/env python3
"""
Script para verificar si el backend está corriendo
"""
import requests
import sys

def verificar_backend():
    """Verifica si el backend está accesible"""
    urls = [
        'http://localhost:8612/health',
        'http://localhost:8612/api/health',
        'http://localhost:8612/',
    ]
    
    print("=" * 80)
    print("🔍 VERIFICANDO BACKEND DDX")
    print("=" * 80)
    print()
    
    backend_activo = False
    
    for url in urls:
        print(f"Probando: {url}")
        try:
            response = requests.get(url, timeout=2)
            print(f"   ✅ RESPUESTA: {response.status_code}")
            print(f"   📄 Contenido: {response.text[:100]}")
            backend_activo = True
            break
        except requests.exceptions.ConnectionError:
            print(f"   ❌ No se puede conectar")
        except requests.exceptions.Timeout:
            print(f"   ⏱️ Timeout")
        except Exception as e:
            print(f"   ⚠️ Error: {e}")
        print()
    
    print("=" * 80)
    if backend_activo:
        print("✅ BACKEND ESTÁ CORRIENDO")
        print()
        print("El problema puede ser:")
        print("   1. CORS no configurado correctamente")
        print("   2. Frontend apuntando al puerto incorrecto")
        print("   3. Error en la ruta específica del frontend")
    else:
        print("❌ BACKEND NO ESTÁ CORRIENDO")
        print()
        print("Solución:")
        print("   1. Abrir terminal en: C:\\Users\\Master\\Documents\\DDX\\backend")
        print("   2. Activar entorno: conda activate ddx")
        print("   3. Ejecutar: uvicorn app.main:app --reload --port 8612")
    print("=" * 80)

if __name__ == "__main__":
    try:
        verificar_backend()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
