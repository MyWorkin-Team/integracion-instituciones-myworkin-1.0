# import requests

# url = "http://127.0.0.1:8000/api/students/ulima/updated/PS100002"

# # payload = {
# #     "phone": "789789789",
# #     "situacionLaboral": "1",
# #     "interesesLaborales": ["IT", "DATA", "PROGRAMMING"],
# #     "email": "test2012@gmail.com",
# #     "city": "Trujiyork",
# #     "alumni": "true"
# # }

# payload = {
#     "country": "ES"
# }

# headers = {
#     "Content-Type": "application/json"
# }

# response = requests.patch(url, json=payload, headers=headers)

# print("Status code:", response.status_code)
# print("Response:", response.json())


import requests
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
BASE_URL = "http://127.0.0.1:8000/api/students/ulima/updated"
HEADERS = {"Content-Type": "application/json"}
TOTAL_REQUESTS = 500
MAX_WORKERS = 10

# -------------------------------------------------
# CATÁLOGOS DE DATOS (DTO ONLY)
# -------------------------------------------------
COUNTRIES = ["PE", "ES", "MX", "CO", "AR"]
CITIES = ["Lima", "Madrid", "CDMX", "Bogotá", "Buenos Aires"]
GENDERS = ["M", "F"]
LABOR_SITUATIONS = ["1", "2", "3"]
LANGUAGES = [["ES"], ["ES", "EN"]]
DEGREE_LEVELS = ["PREGRADO", "POSGRADO"]

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def random_co_id():
    return f"PS{random.randint(100000, 100299)}"


def generate_payload():
    """
    Genera un PATCH parcial SOLO con campos permitidos
    por StudentULimaDTO (no todos).
    """
    payload = {}

    # 📍 Dirección (frecuente)
    if random.random() < 0.6:
        payload["country"] = random.choice(COUNTRIES)

    if random.random() < 0.5:
        payload["city"] = random.choice(CITIES)

    # 👤 Datos personales
    if random.random() < 0.4:
        payload["gender"] = random.choice(GENDERS)

    if random.random() < 0.3:
        payload["discapacidad"] = random.choice([True, False])

    # 💼 Laboral
    if random.random() < 0.5:
        payload["situacionLaboral"] = random.choice(LABOR_SITUATIONS)

    if random.random() < 0.3:
        payload["interesesLaborales"] = random.sample(["1", "2", "3"], k=2)

    # 🎓 Académico
    if random.random() < 0.4:
        payload["degreeLevel"] = random.choice(DEGREE_LEVELS)

    if random.random() < 0.3:
        payload["ppa"] = str(round(random.uniform(13, 18), 2))

    # 🌍 Idiomas
    if random.random() < 0.3:
        payload["languages"] = random.choice(LANGUAGES)

    # ⚙️ Preferencias
    if random.random() < 0.2:
        payload["receiveJobBlastEmail"] = random.choice([True, False])

    return payload


def send_request(i: int):
    co_id = random_co_id()
    payload = generate_payload()

    if not payload:
        return i, co_id, None, "EMPTY_PAYLOAD"

    url = f"{BASE_URL}/{co_id}"

    try:
        response = requests.patch(
            url,
            json=payload,
            headers=HEADERS,
            timeout=5
        )
        return i, co_id, payload, response.status_code
    except Exception as e:
        return i, co_id, payload, str(e)


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    success = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(send_request, i) for i in range(TOTAL_REQUESTS)]

        for future in as_completed(futures):
            i, co_id, payload, result = future.result()

            if result in (200, 204):
                success += 1
            else:
                errors += 1
                print(f"❌ Req {i} | {co_id} | payload={payload} → {result}")

    print("\n✅ FINALIZADO")
    print(f"✔️ Éxitos : {success}")
    print(f"❌ Errores: {errors}")


if __name__ == "__main__":
    main()
