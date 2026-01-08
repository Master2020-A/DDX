import requests
import json

try:
    # Hacer petición al endpoint de camas
    response = requests.get("http://localhost:8612/api/hospitalizacion/camas?limit=100")

    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers.get('content-type')}")
    print("\nResponse Body:")

    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(response.text)

except Exception as e:
    print(f"Error: {e}")
