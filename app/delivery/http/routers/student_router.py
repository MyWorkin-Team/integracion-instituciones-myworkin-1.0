from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from app.core.limiter import limiter
from app.config.di_student import get_student_by_id_use_case, upsert_student_use_case
from app.core.config import require_api_key
from app.infrastructure.mapper.student_mapper import student_to_domain

from fastapi.responses import JSONResponse
from app.core.errors.api_errors import ApiErrorCode
from app.config.helpers import ok, fail
from app.core.dto.api_response import ApiResponse, ApiError

from fastapi import Path
from app.config.di_student import get_student_by_id_use_case
from app.application.student.get_student_by_id_use_case import GetStudentByIdUseCase
from fastapi.params import Depends  
from app.application.student.upsert_student_use_case import UpsertStudentUseCase
from app.core.dependencies import validate_university_id

from app.delivery.schemas.student_dto import StudentDTO
from app.infrastructure.firebase.firebase_client import FirebaseUserAlreadyExists

router = APIRouter()


@router.post(
    "/push/{university_id}",
    dependencies=[Depends(require_api_key), Depends(validate_university_id)],
    response_model=ApiResponse[dict]
)
@limiter.limit("3000/minute")
def upsert_student(
    request: Request,
    body: StudentDTO,
    university_id: str = Path(...),
    uc_upsert: UpsertStudentUseCase = Depends(upsert_student_use_case)
):
    student = student_to_domain(body)

    # 🔴 Validación
    if not student.dni:
        return fail(
            status=400,
            code="INVALID_DATA",
            message="dni is required for upsert"
        )

    # 1️⃣ UPSERT (Creation or Update)
    try:
        result = uc_upsert.execute(student)
        
        status_code = 201 if result == "created" else 200
        message = "Estudiante creado exitosamente" if result == "created" else "Estudiante actualizado exitosamente"

        return ok(
            status=status_code,
            result=result,
            message=message,
            data={"dni": student.dni}
        )

    except FirebaseUserAlreadyExists:
        return fail(
            status=409,
            code="AUTH_EMAIL_EXISTS",
            message="El email ya existe en Firebase Auth"
        )
    except Exception as e:
        return fail(
            status=500,
            code="UPSERT_ERROR",
            message=str(e)
        )


@router.get(
    "/pull/{university_id}/{student_id}",
    dependencies=[Depends(validate_university_id)],
    response_model=ApiResponse[dict]
)
def pull_student(
    student_id: str,
    university_id: str = Path(...),
    uc: GetStudentByIdUseCase = Depends(get_student_by_id_use_case)
):
    student = uc.execute(student_id)

    if not student:
        return fail(
            code="STUDENT_NOT_FOUND",
            message="No se encontró un estudiante con el ID especificado",
            status=404
        )

    return ok(
        student,
        result="fetched",
        message="Estudiante obtenido correctamente"
    )
