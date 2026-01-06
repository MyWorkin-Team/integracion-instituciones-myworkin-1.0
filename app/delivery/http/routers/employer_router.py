
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from app.config.di_student import get_student_by_id_use_case
from app.core.limiter import limiter
from app.core.config import require_api_key

from app.delivery.schemas.employer_ulima_dto import EmployerULimaDTO
from app.config.di_employer import get_employer_by_tax_id_use_case, update_by_tax_id_use_case, register_employer_use_case
from app.infrastructure.mapper.employer_ulima_mapper import ulima_employer_to_domain

from app.config.helpers import ok, fail
from app.core.dto.api_response import ApiResponse
from fastapi import HTTPException

from fastapi.responses import JSONResponse
from app.core.errors.api_errors import ApiErrorCode

router = APIRouter()

@router.post(
    "/push/ulima",
    dependencies=[Depends(require_api_key)],
    response_model=ApiResponse[dict]
)
@limiter.limit("3000/minute")
async def upsert_ulima_employer(
    request: Request,
    body: EmployerULimaDTO
):
    employer = ulima_employer_to_domain(body)

    if not employer.taxId:
        response = fail(
            status=400,
            code=ApiErrorCode.INVALID_DATA,
            message="taxId is required for upsert"
        )
        return JSONResponse(
            status_code=400,
            content=response.model_dump(exclude_none=True)
        )

    # 1️⃣ UPDATE
    uc_update = update_by_tax_id_use_case()
    updated = uc_update.execute(
        employer.taxId,
        employer.to_firestore_dict()
    )

    if updated:
        return ok(
            status=200,
            result="updated",
            message="Employer actualizado exitosamente",
            data={
                "taxId": employer.taxId
            }
        )

    # 2️⃣ CREATE
    uc_create = register_employer_use_case()
    created_employer = uc_create.execute(employer)

    return ok(
        status=201,
        result="created",
        message="Employer creado exitosamente",
        data={
            "taxId": employer.taxId
        }
    )

@router.get(
    "/pull/ulima/{tax_id}",
    response_model=ApiResponse[dict]
)
async def pull_ulima_employer(tax_id: str):

    uc = get_employer_by_tax_id_use_case()
    employer = uc.execute(tax_id)

    if not employer:
        return fail(
            code="EMPLOYER_NOT_FOUND",
            message="No se encontró un empleador con el ID especificado",
            status=404
        )

    return ok(
        employer,
        message="Empleador obtenido correctamente"
    )
