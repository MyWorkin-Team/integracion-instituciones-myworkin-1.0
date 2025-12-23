import requests

url = "http://127.0.0.1:8000/api/students/ulima/updated/PS100002"

# payload = {
#     "phone": "789789789",
#     "situacionLaboral": "1",
#     "interesesLaborales": ["IT", "DATA", "PROGRAMMING"],
#     "email": "test2012@gmail.com",
#     "city": "Trujiyork",
#     "alumni": "true"
# }

payload = {
    "country": "ES"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.patch(url, json=payload, headers=headers)

print("Status code:", response.status_code)
print("Response:", response.json())
