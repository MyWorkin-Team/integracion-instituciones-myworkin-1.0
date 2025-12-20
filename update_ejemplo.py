import requests

url = "http://127.0.0.1:8000/api/students/ulima/by-co-id-ps/PS100000"

payload = {
    "phone": "999888777",
    "coIdPs": "PS100002",
    "situacionLaboral": "1",
    "interesesLaborales": ["IT", "DATA"],
    "email": "test2012@gmail.com"
}

headers = {
    "Content-Type": "application/json"
}

response = requests.patch(url, json=payload, headers=headers)

print("Status code:", response.status_code)
print("Response:", response.json())
