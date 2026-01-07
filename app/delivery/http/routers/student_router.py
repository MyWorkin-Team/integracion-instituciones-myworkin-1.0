from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from app.core.limiter import limiter
from app.config.di_student import get_student_by_id_use_case, register_student_use_case
from app.delivery.schemas.student_ulima_dto import StudentULimaDTO
from app.infrastructure.firebase.firebase_client import FirebaseUserAlreadyExists, FirebaseUserCreateError
from app.infrastructure.mapper.student_ulima_mapper import ulima_to_domain
from app.config.di_student import update_by_co_id_ps_use_case
from app.core.config import require_api_key

from fastapi.responses import JSONResponse
from app.core.errors.api_errors import ApiErrorCode
from app.config.helpers import ok, fail
from app.core.dto.api_response import ApiResponse, ApiError
router = APIRouter()

# -------------------------------------------------
# ULIMA
# -------------------------------------------------
# @router.post("/push/ulima")
# # @limiter.limit("1000/minute")
# async def register_ulima_student(
#     request: Request,
#     body: StudentULimaDTO
# ):
#     try:
#         uc = register_student_use_case()
#         result = uc.execute(ulima_to_domain(body))
#         return {"status": result}

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return {
#             "error": str(e),
#             "type": type(e).__name__
#         }

# @router.patch("/push/ulima/updated/{co_id_ps}", dependencies=[Depends(require_api_key)])
# @limiter.limit("3000/minute")
# async def update_ulima_student(co_id_ps: str, body: StudentULimaDTO):
#     uc = update_by_co_id_ps_use_case()
#     data = body.model_dump(exclude_unset=True)

#     updated = uc.execute(co_id_ps, data)
#     if not updated:
#         raise HTTPException(status_code=404, detail="Student not found")

#     return {
#         "status": "success",
#         "message": "Student updated successfully",
#         "co_id_ps": co_id_ps
#     }
@router.post(
    "/push/ulima",
    dependencies=[Depends(require_api_key)],
    response_model=ApiResponse[dict]
)
@limiter.limit("3000/minute")
async def upsert_ulima_student(
    request: Request,
    body: StudentULimaDTO
):
    student = ulima_to_domain(body)

    # 🔴 Validación
    if not student.coIdPs:
        return fail(
            status=400,
            code="INVALID_DATA",
            message="coIdPs is required for upsert"
        )

    # 1️⃣ UPDATE
    uc_update = update_by_co_id_ps_use_case()
    updated = uc_update.execute(
        student.coIdPs,
        student  # 👈 importante: JSON-safe
    )

    if updated:
        return ok(
            status=200,
            result="updated",
            message="Estudiante actualizado exitosamente",
            data={
                "coIdPs": student.coIdPs
            }
        )

    # 2️⃣ CREATE
    uc_create = register_student_use_case()
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



@router.get("/ulima")
async def test_route():
    return {
        "status": "ok",
        "message": "Te listo estudiantes de ulima"
    }


@router.get(
    "/pull/ulima/{student_id}",
    response_model=ApiResponse[dict]
)
async def pull_ulima_student(student_id: str):

    uc = get_student_by_id_use_case()
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
