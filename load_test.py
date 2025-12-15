import requests
import time

URL = "http://localhost:8000/api/students/ucv"
HEADERS = {"Content-Type": "application/json"}

PAYLOAD = {
    "id": "12345678",
    "firstName": "Test",
    "lastName": "User",
    "email": "test.user@ulima.edu.pe",
    "careerCode": "ING-SIS"
}

TOTAL_REQUESTS = 15
DELAY_SECONDS = 1

for i in range(TOTAL_REQUESTS):
    r = requests.post(URL, json=PAYLOAD, headers=HEADERS)
    print(f"[{i+1}] Status:", r.status_code, r.text)
    time.sleep(DELAY_SECONDS)
