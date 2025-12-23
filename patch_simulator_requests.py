import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "http://127.0.0.1:8000/api/students/ulima/updated"
HEADERS = {"Content-Type": "application/json"}

COUNTRIES = [
    "ES", "PE", "MX", "CO", "AR",
    "CL", "BR", "US", "FR", "DE",
    "IT", "PT", "EC", "BO", "UY"
]

def random_co_id():
    return f"PS{random.randint(100000, 100300):06d}"

def send_request(i):
    co_id = random_co_id()
    payload = {
        "country": random.choice(COUNTRIES)
    }

    url = f"{BASE_URL}/{co_id}"

    try:
        response = requests.patch(
            url,
            json=payload,
            headers=HEADERS,
            timeout=5
        )
        return i, co_id, payload["country"], response.status_code
    except Exception as e:
        return i, co_id, payload["country"], str(e)

success = 0
errors = 0

TOTAL_REQUESTS = 500

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]

    for future in as_completed(futures):
        i, co_id, country, result = future.result()

        if result in (200, 204):
            success += 1
        else:
            errors += 1
            print(f"❌ Req {i} | {co_id} | {country} → {result}")

print("✅ Finalizado")
print("✔️ Éxitos:", success)
print("❌ Errores:", errors)
