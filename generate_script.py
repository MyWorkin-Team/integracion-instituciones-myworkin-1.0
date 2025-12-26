import random
import uuid
import pandas as pd
from datetime import datetime, timezone, date, timedelta

# ---------------------------------
# CONFIG
# ---------------------------------
OUTPUT_FILE = "students_ulima_full.xlsx"
N_REGISTROS = 300
UNIVERSITY = "UNIVERSIDAD DE LIMA"

FIRST_NAMES = ["Adriana", "Carlos", "Lucía", "Pedro", "María", "José", "Sofía", "Miguel"]
MIDDLE_NAMES = ["Yolanda", "Alonso", "Isabel", "Andrés", "Paola"]
LAST_NAMES = ["Abad", "Pérez", "Gómez", "Torres", "Rojas", "Vargas", "Mendoza"]
DEGREES = ["Administración", "Economía", "Marketing", "Ingeniería Industrial"]
SUBJECT_AREAS = ["Ciencias Empresariales", "Ingeniería", "Marketing y Comunicación"]
LANGUAGES = ["ES", "ES,EN"]
LABOR_SITUATIONS = ["1", "2", "3"]

# ---------------------------------
# HELPERS
# ---------------------------------
def random_birthdate(start_year=1995, end_year=2005):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return (start + timedelta(days=random.randint(0, (end - start).days))).isoformat()


def generate_student(index: int) -> dict:
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    second_last = random.choice(LAST_NAMES)
    full_name = f"{first} {middle} {last} {second_last}"
    now = datetime.now(timezone.utc).isoformat()

    return {
        # ROOT
        "id": str(uuid.uuid4()),
        "displayName": f"{first.lower()}.{last.lower()}{index}@test.com",
        "email": f"{first.lower()}.{last.lower()}{index}@test.com",
        "phone": f"9{random.randint(10000000, 99999999)}",
        "role": "student",
        "status": "active",
        "university": UNIVERSITY,
        "verified": random.choice([True, False]),
        "hasCV": random.choice([True, False]),
        "usoPrimerHerramienta": random.choice([True, False]),
        "createdAt": now,
        "updatedAt": now,

        # ONBOARDING
        "onboarding_completed": random.choice([True, False]),
        "onboarding_skipped": random.choice([True, False]),
        "onboarding_skippedAt": now,

        # PERSONAL
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

        # IDS
        "schoolStudentId": str(20190000 + index),
        "coPers": f"CO{100000 + index}",
        "coIdPs": f"PS{100000 + index}",

        # DOCUMENT
        "document_tipoDocumento": "DNI",
        "document_numeroDocumento": str(70000000 + index),
        "document_paisEmisionDocumento": "PE",

        # ADDRESS
        "address_street": f"Av. Test {index}",
        "address_city": "Lima",
        "address_dependentLocality": "Santiago de Surco",
        "address_state": "Lima",
        "address_zip": "15023",
        "address_country": "PE",

        # CONTACT
        "contact_email": f"{first.lower()}.{last.lower()}{index}@test.com",
        "contact_emailUniversity": f"{index}@aloe.ulima.edu.pe",
        "contact_emailAlternativo": f"{first.lower()}.alt{index}@gmail.com",
        "contact_phone": f"9{random.randint(10000000, 99999999)}",
        "contact_telefonoAlternativo": f"9{random.randint(10000000, 99999999)}",

        # ACADEMIC
        "academic_applicantType": "ESTUDIANTE",
        "academic_degreeLevel": "PREGRADO",
        "academic_degreeMode": "PRESENCIAL",
        "academic_degreeAward": "BACHILLER",
        "academic_degreeYear": random.randint(2022, 2025),
        "academic_degreePrimary": True,
        "academic_degree": random.choice(DEGREES),
        "academic_subjectArea": random.choice(SUBJECT_AREAS),
        "academic_institucionEducacionSuperior": UNIVERSITY,
        "academic_rankingUlima": random.choice(["PRIMER_SUPERIOR", "QUINTO_SUPERIOR"]),
        "academic_ppa": round(random.uniform(13, 18), 2),
        "academic_cicloUltimaMatricula": f"2024-{random.randint(1,2)}",
        "academic_creditosAprobados": random.randint(100, 200),
        "academic_creditosMatriculados": random.randint(12, 30),
        "academic_fechaEgreso": "2024-12-15",

        # STUDIES
        "studies_tienesColegiatura": random.choice([True, False]),
        "studies_tienesMaestria": random.choice([True, False]),
        "studies_tienesMaestriaExternaUl": random.choice([True, False]),

        # PREFERENCES
        "preferences_languages": random.choice(LANGUAGES),
        "preferences_receiveJobBlastEmail": True,
        "preferences_experientialLearning": random.choice([True, False]),

        # RIGHTS
        "rights_canApplyJobs": True,
        "rights_canDownloadCertificates": True,
        "rights_canEditProfile": False,

        # LABOR
        "situacionLaboral": random.choice(LABOR_SITUATIONS),
        "interesesLaborales": "1,3",
    }


# ---------------------------------
# MAIN
# ---------------------------------
def main():
    data = [generate_student(i) for i in range(N_REGISTROS)]
    df = pd.DataFrame(data)
    df.to_excel(OUTPUT_FILE, index=False)

    print("✅ Excel generado correctamente")
    print(f"📄 Archivo: {OUTPUT_FILE}")
    print(f"👥 Registros: {N_REGISTROS}")


if __name__ == "__main__":
    main()
