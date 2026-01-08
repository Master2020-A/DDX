import requests
import json

print("="*70)
print("PROBANDO LOGIN - Backend en http://localhost:8612")
print("="*70)

# Test 1: Admin
print("\n[TEST 1] Probando con admin@ddx.com...")
try:
    r = requests.post('http://localhost:8612/api/auth/login', 
                      json={'email': 'admin@ddx.com', 'password': 'Admin123!'})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("✅ LOGIN EXITOSO con admin@ddx.com")
        print(f"Token: {r.json()['access_token'][:50]}...")
    else:
        print(f"❌ FALLO: {r.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Master
print("\n[TEST 2] Probando con master@master.com...")
try:
    r = requests.post('http://localhost:8612/api/auth/login', 
                      json={'email': 'master@master.com', 'password': 'Master123!'})
    print(f"Status: {r.status_code}")
    if r.status_code == 200:
        print("✅ LOGIN EXITOSO con master@master.com")
    else:
        print(f"❌ FALLO: {r.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: El typo del log
print("\n[TEST 3] Probando con msater@master.com (el del log)...")
try:
    r = requests.post('http://localhost:8612/api/auth/login', 
                      json={'email': 'msater@master.com', 'password': 'Master123!'})
    print(f"Status: {r.status_code}")
    print(f"❌ FALLO: {r.json()}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("RECOMENDACIÓN:")
print("Si ninguno funciona, ejecuta: python crear_admin.py")
print("="*70)
