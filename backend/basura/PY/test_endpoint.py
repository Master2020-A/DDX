"""Test rápido de endpoints"""
import requests

base_url = "http://localhost:8000"

print("\n🧪 Probando endpoints...\n")

# Test 1: Health check
try:
    response = requests.get(f"{base_url}/")
    print(f"✅ Root endpoint: {response.status_code}")
except Exception as e:
    print(f"❌ Root endpoint: {e}")

# Test 2: Camas
try:
    response = requests.get(
        f"{base_url}/api/hospitalizacion/camas",
        params={"limit": 10},
        headers={"Authorization": "Bearer tu_token_aqui"}
    )
    print(f"{'✅' if response.status_code == 200 else '❌'} Camas endpoint: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"❌ Camas endpoint: {e}")

# Test 3: Censo
try:
    response = requests.get(
        f"{base_url}/api/hospitalizacion/censo/actual",
        headers={"Authorization": "Bearer tu_token_aqui"}
    )
    print(f"{'✅' if response.status_code == 200 else '❌'} Censo endpoint: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text[:200]}")
except Exception as e:
    print(f"❌ Censo endpoint: {e}")

print("\n")
