import pandas as pd
from dataclasses import asdict
from datetime import datetime
from typing import List
import firebase_admin
from firebase_admin import credentials, firestore

from app.domain.model.student import Student  # donde tienes tu dataclass


# --------------------------------
# CONFIG
# --------------------------------
EXCEL_FILE = "students_ulima_full.xlsx"
COLLECTION_NAME = "students"
SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"


# --------------------------------
# FIREBASE INIT
# --------------------------------
cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
firebase_admin.initialize_app(cred)
db = firestore.client()


# --------------------------------
# HELPERS
# --------------------------------
def parse_datetime(value):
    if pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def parse_list(value) -> List[str] | None:
    if pd.isna(value):
        return None
    if isinstance(value, list):
        return value
    return str(value).split(",")


def row_to_student(row: pd.Series) -> Student:
    return Student(
        # Identidad
        id=row["id"],
        displayName=row["displayName"],
        email=row["email"],
        phone=row["phone"],
        firstName=row["firstName"],
        middleName=row["middleName"],
        lastName=row["lastName"],
        secondLastName=row["secondLastName"],
        fullName=row["fullName"],
        image=row["image"],
        birthdate=row["birthdate"],
        gender=row["gender"],
        discapacidad=row["discapacidad"],
        alumni=row["alumni"],

        # Estado
        role=row["role"],
        status=row["status"],
        university=row["university"],
        verified=row["verified"],
        hasCV=row["hasCV"],
        usoPrimerHerramienta=row["usoPrimerHerramienta"],

        # Onboarding
        onboarding_completed=row["onboarding_completed"],
        onboarding_skipped=row["onboarding_skipped"],
        onboarding_skippedAt=parse_datetime(row["onboarding_skippedAt"]),

        # Fechas
        createdAt=parse_datetime(row["createdAt"]),
        updatedAt=parse_datetime(row["updatedAt"]),

        # IDs
        schoolStudentId=row["schoolStudentId"],
        coPers=row["coPers"],
        coIdPs=row["coIdPs"],

        # Documento
        tipoDocumento=row["document_tipoDocumento"],
        numeroDocumento=row["document_numeroDocumento"],
        paisEmisionDocumento=row["document_paisEmisionDocumento"],

        # Dirección
        street=row["address_street"],
        city=row["address_city"],
        dependentLocality=row["address_dependentLocality"],
        state=row["address_state"],
        zip=row["address_zip"],
        country=row["address_country"],

        # Académico
        applicantType=row["academic_applicantType"],
        degreeLevel=row["academic_degreeLevel"],
        degreeMode=row["academic_degreeMode"],
        degreeAward=row["academic_degreeAward"],
        degreeYear=str(row["academic_degreeYear"]),
        degreePrimary=row["academic_degreePrimary"],
        degree=row["academic_degree"],
        subjectArea=row["academic_subjectArea"],
        institucionEducacionSuperior=row["academic_institucionEducacionSuperior"],
        rankingUlima=row["academic_rankingUlima"],
        ppa=str(row["academic_ppa"]),
        cicloUltimaMatricula=row["academic_cicloUltimaMatricula"],
        creditosAprobados=str(row["academic_creditosAprobados"]),
        creditosMatriculados=str(row["academic_creditosMatriculados"]),
        fechaEgreso=row["academic_fechaEgreso"],

        # Estudios
        tienesColegiatura=row["studies_tienesColegiatura"],
        tienesMaestria=row["studies_tienesMaestria"],
        tienesMaestriaExternaUl=row["studies_tienesMaestriaExternaUl"],

        # Preferencias
        languages=parse_list(row["preferences_languages"]),
        receiveJobBlastEmail=row["preferences_receiveJobBlastEmail"],
        experientialLearning=row["preferences_experientialLearning"],

        # Derechos
        canApplyJobs=row["rights_canApplyJobs"],
        canDownloadCertificates=row["rights_canDownloadCertificates"],
        canEditProfile=row["rights_canEditProfile"],

        # Laboral
        situacionLaboral=row["situacionLaboral"],
        interesesLaborales=parse_list(row["interesesLaborales"]),
    )


def student_to_firestore(student: Student) -> dict:
    data = asdict(student)

    # 🔥 Limpieza: Firestore odia None
    return {k: v for k, v in data.items() if v is not None}


# --------------------------------
# MAIN
# --------------------------------
def main():
    df = pd.read_excel(EXCEL_FILE)

    success = 0
    for _, row in df.iterrows():
        student = row_to_student(row)
        data = student_to_firestore(student)

        db.collection(COLLECTION_NAME).document(student.id).set(data)
        success += 1

    print(f"🔥 {success} estudiantes cargados en Firestore")


if __name__ == "__main__":
    main()
