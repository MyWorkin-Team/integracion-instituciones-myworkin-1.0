import requests
import random
from datetime import datetime, timezone, timedelta
from typing import List
import uuid
from datetime import date, timedelta
import random


BASE_URL = "http://localhost:8000/api"
ENDPOINT = f"{BASE_URL}/students/ulima"

UNIVERSITY = "UNIVERSIDAD DE LIMA"

FIRST_NAMES = ["Adriana", "Carlos", "Lucía", "Pedro", "María", "José", "Sofía", "Miguel"]
MIDDLE_NAMES = ["Yolanda", "Alonso", "Isabel", "Andrés", "Paola"]
LAST_NAMES = ["Abad", "Pérez", "Gómez", "Torres", "Rojas", "Vargas", "Mendoza"]
DEGREES = ["Administración", "Economía", "Marketing", "Ingeniería Industrial"]
SUBJECT_AREAS = ["Ciencias Empresariales", "Ingeniería", "Marketing y Comunicación"]
LANGUAGES = [["ES"], ["ES", "EN"]]
LABOR_SITUATIONS = ["1", "2", "3"]


def random_birthdate(start_year=1995, end_year=2005):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta_days = (end - start).days
    random_day = random.randint(0, delta_days)
    d = start + timedelta(days=random_day)
    return d.isoformat()  # devuelve "YYYY-MM-DD"


def generate_student(index: int) -> dict:
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    second_last = random.choice(LAST_NAMES)
    full_name = f"{first} {middle} {last} {second_last}"
    email = f"{first.lower()}.{last.lower()}{index}@test.com"
    university_email = f"{index}@aloe.ulima.edu.pe"
    phone_number = f"9{random.randint(10000000, 99999999)}"
    now = datetime.now(timezone.utc).isoformat()

    return {
        "id": str(uuid.uuid4()),
        "displayName": email,
        "email": email,
        "phone": phone_number,
        "role": "student",
        "status": "active",
        "university": UNIVERSITY,
        "verified": random.choice([True, False]),
        "hasCV": random.choice([True, False]),
        "usoPrimerHerramienta": random.choice([True, False]),
        "onboarding": {
            "completed": random.choice([True, False]),
            "skipped": random.choice([True, False]),
            "skippedAt": now
        },
        "createdAt": now,
        "updatedAt": now,
        "firstName": first,
        "middleName": middle,
        "lastName": last,
        "secondLastName": second_last,
        "fullName": full_name,
        "image": "https://ulima.edu.pe/photos/student.png",
        "birthdate": random_birthdate(),
        "gender": random.choice(["F", "M"]),
        "discapacidad": random.choice([True, False]),
        "alumni": random.choice([True, False]),
        "schoolStudentId": str(20190000 + index),
        "coPers": f"CO{100000+index}",
        "coIdPs": f"PS{100000+index}",
        "document": {
            "tipoDocumento": "DNI",
            "numeroDocumento": str(70000000 + index),
            "paisEmisionDocumento": "PE"
        },
        "address": {
            "street": f"Av. Test {index}",
            "city": "Lima",
            "dependentLocality": "Santiago de Surco",
            "state": "Lima",
            "zip": "15023",
            "country": "PE"
        },
        "contact": {
            "email": email,
            "emailUniversity": university_email,
            "emailAlternativo": f"{first.lower()}.alt{index}@gmail.com",
            "phone": phone_number,
            "telefonoAlternativo": f"9{random.randint(10000000, 99999999)}"
        },
        "academic": {
            "applicantType": "ESTUDIANTE",
            "degreeLevel": "PREGRADO",
            "degreeMode": "PRESENCIAL",
            "degreeAward": "BACHILLER",
            "degreeYear": str(random.randint(2022, 2025)),
            "degreePrimary": True,
            "degree": random.choice(DEGREES),
            "subjectArea": random.choice(SUBJECT_AREAS),
            "institucionEducacionSuperior": UNIVERSITY,
            "rankingUlima": random.choice(["PRIMER_SUPERIOR", "QUINTO_SUPERIOR"]),
            "ppa": f"{random.uniform(13, 18):.2f}",
            "cicloUltimaMatricula": f"2024-{random.randint(1, 2)}",
            "creditosAprobados": str(random.randint(100, 200)),
            "creditosMatriculados": str(random.randint(12, 30)),
            "fechaEgreso": "2024-12-15"
        },
        "studies": {
            "tienesColegiatura": random.choice([True, False]),
            "tienesMaestria": random.choice([True, False]),
            "tienesMaestriaExternaUl": random.choice([True, False])
        },
        "preferences": {
            "languages": random.choice(LANGUAGES),
            "receiveJobBlastEmail": True,
            "experientialLearning": random.choice([True, False])
        },
        "rights": {
            "canApplyJobs": True,
            "canDownloadCertificates": True,
            "canEditProfile": False
        },
        "situacionLaboral": random.choice(LABOR_SITUATIONS),
        "interesesLaborales": ["1", "3"]
    }


def main():
    success = 0
    for i in range(10):
        student = generate_student(i)
        response = requests.post(ENDPOINT, json=student)
        if response.status_code in (200, 201):
            success += 1
            print(f"✅ Student {i+1} creado: {student['fullName']}")
        else:
            print(f"❌ Error student {i+1}")
            print(response.status_code, response.text)
    print(f"\n🎉 {success}/25 estudiantes creados correctamente")


if __name__ == "__main__":
    main()
