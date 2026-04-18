from datetime import datetime
from app.config.di_student import init_firebase
from app.infrastructure.firebase.student_repository_adapter import (
    StudentRepositoryAdapter,
)
from app.application.student.upsert_student_use_case import UpsertStudentUseCase
from app.domain.model.student import Student
from app.infrastructure.cache.redis_cache import RedisCache


def upsert_student_job(university_id: str, student_dict: dict) -> str:
    app = init_firebase(university_id)
    repo = StudentRepositoryAdapter(app)
    uc = UpsertStudentUseCase(repo)

    # Handle datetime serialization
    if student_dict.get("createdAt") and isinstance(student_dict["createdAt"], str):
        student_dict["createdAt"] = datetime.fromisoformat(student_dict["createdAt"])
    if student_dict.get("updatedAt") and isinstance(student_dict["updatedAt"], str):
        student_dict["updatedAt"] = datetime.fromisoformat(student_dict["updatedAt"])

    student = Student(**student_dict)
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

    return result
