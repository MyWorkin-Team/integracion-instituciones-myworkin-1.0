from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from app.core.limiter import limiter
from app.config.di_student import get_student_by_id_use_case, register_student_use_case
from app.delivery.schemas.student_dto import StudentDTO
from app.infrastructure.firebase.firebase_client import FirebaseUserAlreadyExists, FirebaseUserCreateError
from app.config.di_student import update_by_co_id_ps_use_case
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
from app.application.student.update_student_use_case import UpdateStudentByCoIdPsUseCase
from app.application.student.register_student_use_case import RegisterStudentUseCase

router = APIRouter()


@router.post(
    "/push/{university_id}",
    dependencies=[Depends(require_api_key)],
    response_model=ApiResponse[dict]
)
@limiter.limit("3000/minute")
async def upsert_student(
    request: Request,
    body: StudentDTO,
    # ⬇️ INYECCIÓN DE DEPENDENCIAS AQUÍ ⬇️
    university_id: str = Path(...),
    uc_update: UpdateStudentByCoIdPsUseCase = Depends(update_by_co_id_ps_use_case),
    uc_create: RegisterStudentUseCase = Depends(register_student_use_case)
):
    student = student_to_domain(body)

    # 🔴 Validación
    if not student.coIdPs:
        return fail(
            status=400,
            code="INVALID_DATA",
            message="coIdPs is required for upsert"
        )

    # 1️⃣ UPDATE (Ya no llamas a la función, usas el parámetro uc_update)
    updated = uc_update.execute(student)

    if updated:
        return ok(
            status=200,
            result="updated",
            message="Estudiante actualizado exitosamente",
            data={"coIdPs": student.coIdPs}
        )

    # 2️⃣ CREATE (Usas el parámetro uc_create inyectado)
    try:
        uc_create.execute(student)

    except FirebaseUserAlreadyExists:
        return fail(
            status=409,
            code="AUTH_EMAIL_EXISTS",
            message="El email ya existe en Firebase Auth"
        )
    except FirebaseUserCreateError as e:
        return fail(
            status=500,
            code="AUTH_CREATE_ERROR",
            message=str(e)
        )

    return ok(
        status=201,
        result="created",
        message="Estudiante creado exitosamente",
        data={"coIdPs": student.coIdPs}
    )


@router.get(
    "/pull/{university_id}/{student_id}",
    response_model=ApiResponse[dict]
)
async def pull_student(
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
        message="Estudiante obtenido correctamente"
    )
