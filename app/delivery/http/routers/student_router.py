from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from dataclasses import asdict

from app.core.limiter import limiter
from app.config.di_student import get_student_by_dni_use_case, upsert_student_use_case
from app.core.config import require_api_key
from app.infrastructure.mapper.student_mapper import student_to_domain

from fastapi.responses import JSONResponse
from app.core.errors.api_errors import ApiErrorCode
from app.config.helpers import ok, fail
from app.core.dto.api_response import ApiResponse, ApiError

from fastapi import Path
from app.config.di_student import get_student_by_dni_use_case
from app.application.student.get_student_by_id_use_case import GetStudentByDniUseCase
from fastapi.params import Depends
from app.application.student.upsert_student_use_case import UpsertStudentUseCase
from app.core.dependencies import validate_university_id

from app.delivery.schemas.student_dto import StudentDTO
from app.infrastructure.firebase.firebase_client import FirebaseUserAlreadyExists
from rq import Queue
from app.infrastructure.queue.redis_client import get_redis_connection
from app.workers.student_tasks import upsert_student_job
from app.infrastructure.cache.redis_cache import RedisCache
from app.infrastructure.validation.firebase_validator import FirebaseValidator

router = APIRouter()


@router.post(
    "/push",
    dependencies=[Depends(require_api_key), Depends(validate_university_id)],
    response_model=ApiResponse[dict]
)
@limiter.limit("3000/minute")
async def upsert_student(
    request: Request,
    body: StudentDTO,
    university_id: str = Depends(validate_university_id)
):
    student = student_to_domain(body)

    if not student.dni:
        return fail(
            status=400,
            code="INVALID_DATA",
            message="dni is required for upsert"
        )

    # Validate email globally (Cascading: Redis → Firebase)
    if student.email:
        # Check Redis first
        exists_in_redis, redis_type = RedisCache.is_email_registered_globally(student.email)
        if exists_in_redis:
            return fail(
                status=409,
                code="DUPLICATE_EMAIL",
                message=f"Email {student.email} ya está registrado como {redis_type} en el sistema"
            )

        # Check Firebase (authority)
        exists_in_firebase, firebase_type = FirebaseValidator.email_exists_globally(student.email)
        if exists_in_firebase:
            return fail(
                status=409,
                code="DUPLICATE_EMAIL",
                message=f"Email {student.email} ya existe como {firebase_type} en el sistema"
            )

    # Enqueue job to RQ
    try:
        q = Queue("students", connection=get_redis_connection())
        student_dict = asdict(student)
        job = q.enqueue(upsert_student_job, university_id, student_dict)

        # Register in cache with full data after successful enqueue
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

        return ok(
            status=202,
            result="queued",
            message="Estudiante encolado para procesamiento",
            data={"job_id": job.id, "dni": student.dni}
        )
    except Exception as e:
        return fail(
            status=500,
            code="QUEUE_ERROR",
            message=f"Error al encolar el estudiante: {str(e)}"
        )


@router.post(
    "/pull",
    dependencies=[Depends(validate_university_id)],
    response_model=ApiResponse[dict]
)
async def pull_student(
    request: Request,
    uc: GetStudentByDniUseCase = Depends(get_student_by_dni_use_case)
):
    try:
        body = await request.json()
        dni = body.get("dni")
    except Exception:
        dni = None

    if not dni:
        return fail(
            code="INVALID_DATA",
            message="dni is required in body",
            status=400
        )

    student = uc.execute(dni)

    if not student:
        return fail(
            code="STUDENT_NOT_FOUND",
            message="No se encontró un estudiante con el DNI especificado",
            status=404
        )

    return ok(
        student,
        result="fetched",
        message="Estudiante obtenido correctamente"
    )
