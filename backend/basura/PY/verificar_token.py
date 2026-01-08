"""
Script para verificar el contenido del token y el usuario autenticado
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import decode_access_token

# Pega aquí el token que ves en localStorage del navegador
# Para obtenerlo: Abre DevTools -> Application -> Local Storage -> http://localhost:3000 -> token
TOKEN = input("Pega el token de localStorage: ").strip()

if TOKEN:
    payload = decode_access_token(TOKEN)
    if payload:
        print("\n✅ Token válido")
        print(f"Payload del token: {payload}")
        print(f"\nUser ID (sub): {payload.get('sub')}")
        print(f"Expira: {payload.get('exp')}")
    else:
        print("\n❌ Token inválido o expirado")
else:
    print("❌ No se proporcionó token")
