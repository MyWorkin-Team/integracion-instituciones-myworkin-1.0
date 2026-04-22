import os
from datetime import datetime
from app.config.di_student import init_firebase
from app.infrastructure.firebase.student_repository_adapter import (
    StudentRepositoryAdapter,
)
from app.application.student.upsert_student_use_case import UpsertStudentUseCase
from app.domain.model.student import Student
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.embedding.generate_degree import generate_degree
from rq import Queue
from app.infrastructure.queue.redis_client import get_redis_connection


def upsert_student_job(university_id: str, student_dict: dict) -> str:
    from app.infrastructure.validation.firebase_validator import FirebaseValidator

    app = init_firebase(university_id)
    repo = StudentRepositoryAdapter(app)
    uc = UpsertStudentUseCase(repo, university_id=university_id)

    # Handle datetime serialization
    if student_dict.get("createdAt") and isinstance(student_dict["createdAt"], str):
        student_dict["createdAt"] = datetime.fromisoformat(student_dict["createdAt"])
    if student_dict.get("updatedAt") and isinstance(student_dict["updatedAt"], str):
        student_dict["updatedAt"] = datetime.fromisoformat(student_dict["updatedAt"])

    student = Student(**student_dict)

    # Validación de email (en background)
    dni_already_registered = RedisCache.is_dni_registered(student.dni, university_id)
    if student.email and not dni_already_registered:
        exists_in_redis, redis_type = RedisCache.is_email_registered_globally(student.email)
        if exists_in_redis:
            print(f"⚠️  Email duplicado: {student.email} registrado como {redis_type}")
            return "duplicate_email"

        exists_in_firebase, firebase_type = FirebaseValidator.email_exists_globally(student.email)
        if exists_in_firebase:
            print(f"⚠️  Email duplicado en Firebase: {student.email} como {firebase_type}")
            return "duplicate_email"

    result = uc.execute(student)

    # Register in cache with full data after successful Firebase write
    cache_data = {
        "university_id": university_id,
        "dni": student.dni,
        "email": student.email,
        "displayName": student.displayName,
        "career": student.career,
        "studentStatus": student.studentStatus,
        "createdAt": str(student.createdAt) if student.createdAt else None,
        "updatedAt": str(student.updatedAt) if student.updatedAt else None,
    }
    RedisCache.register_student(student.dni, student.email or "", university_id, cache_data)

    # Encolaar job para generar degree si hay career
    if student.career:
        q = Queue("students", connection=get_redis_connection())
        q.enqueue(
            generate_degree_job,
            university_id,
            student.dni,
            student.career,
            job_timeout=300
        )

    return result


def generate_degree_job(university_id: str, dni: str, career: str) -> str:
    """Genera el degree para un estudiante en background."""
    try:
        print(f"\n🔄 [DEGREE_JOB] Generando degree para {dni}")

        from app.config.di_student import get_student_by_dni_use_case
        from app.infrastructure.firebase.firebase_client import get_firestore
        import json

        app = init_firebase(university_id)
        repo = StudentRepositoryAdapter(app)
        db = repo.client

        # Obtener país
        countries_json = os.getenv("UNIVERSITY_COUNTRIES", "{}")
        countries = json.loads(countries_json)
        country = countries.get(university_id, "").lower()

        if not country:
            raise ValueError(f"País no configurado para {university_id}")

        # Construir catalogId
        catalog_id = f"myworkin-{country}-{university_id.lower()}"

        # Obtener catálogo desde CORE_COMMONS
        from firebase_admin import credentials, firestore as fb_firestore, get_app, initialize_app

        core_commons_creds = os.getenv("FIREBASE_SERVICE_ACCOUNT_CORE_COMMONS")
        if not core_commons_creds:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_CORE_COMMONS no configurada")

        try:
            core_app = get_app("CORE_COMMONS")
        except ValueError:
            cred_dict = json.loads(core_commons_creds)
            if "private_key" in cred_dict:
                cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
            cred = credentials.Certificate(cred_dict)
            core_app = initialize_app(cred, name="CORE_COMMONS")

        core_db = fb_firestore.client(app=core_app)
        catalog_doc = core_db.collection("tenant_config").document(catalog_id).get()

        if not catalog_doc.exists:
            raise ValueError(f"Catálogo no encontrado para {catalog_id}")

        catalog_data = catalog_doc.to_dict()
        careers_list = catalog_data.get("allCareers", [])

        if not careers_list:
            raise ValueError(f"Catálogo vacío para {catalog_id}")

        # Generar degree
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada")

        degree = generate_degree(career, careers_list, api_key)

        # Actualizar student en Firebase con el degree
        degree_dict = {
            "displayName": degree.displayName,
            "embedding": degree.embedding,
            "id": degree.id
        }

        db.collection("users").where(
            filter=db._client.collection("users").where(
                filter=type('Filter', (), {'field_path': 'dni', 'op_string': '==', 'value': dni})()
            ) if hasattr(db, '_client') else None
        )

        # Buscar y actualizar por DNI
        from google.cloud.firestore import FieldFilter
        docs = list(db.collection("users").where(
            filter=FieldFilter("dni", "==", dni)
        ).limit(1).stream())

        if docs:
            docs[0].reference.update({"degree": degree_dict})
            print(f"✅ Degree guardado para {dni}")
            return "success"
        else:
            print(f"⚠️  No se encontró estudiante con DNI {dni}")
            return "not_found"

    except Exception as e:
        print(f"❌ Error en generate_degree_job: {str(e)}")
        import traceback
        traceback.print_exc()
        return "error"
