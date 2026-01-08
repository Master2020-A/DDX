"""
Script de prueba para el endpoint de pre-diagnóstico
"""

import requests
import json

# URL del endpoint
url = "http://localhost:8612/api/prediagnostico/generar"

# Datos de prueba
data = {
    "paciente_id": "00000000-0000-0000-0000-000000000001",
    "sintomas": [
        {
            "descripcion": "Dolor de cabeza intenso",
            "intensidad": "severo",
            "duracion": "2 días",
            "frecuencia": "constante",
        },
        {"descripcion": "Fiebre", "intensidad": "moderado", "duracion": "1 día"},
    ],
    "antecedentes": "Hipertensión arterial controlada",
    "medicamentos_actuales": ["Losartán 50mg", "Aspirina 100mg"],
    "alergias": ["Penicilina"],
}

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN_HERE",  # Reemplazar con token real
}

print("🔄 Enviando request a:", url)
print("📦 Datos:", json.dumps(data, indent=2, ensure_ascii=False))

try:
    response = requests.post(url, json=data, headers=headers)

    print(f"\n📊 Status Code: {response.status_code}")
    print(f"📄 Response Headers: {dict(response.headers)}")

    if response.status_code == 200:
        print("\n✅ SUCCESS!")
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\n❌ ERROR {response.status_code}")
        print("Response:", response.text)

        try:
            error_detail = response.json()
            print("\nError detallado:")
            print(json.dumps(error_detail, indent=2, ensure_ascii=False))
        except:
            pass

except Exception as e:
    print(f"\n❌ Exception: {e}")
    import traceback

    traceback.print_exc()
