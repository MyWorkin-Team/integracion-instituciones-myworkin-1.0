
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from app.core.limiter import limiter
from app.core.config import require_api_key

from app.delivery.schemas.employer_dto import EmployerDTO
from app.config.di_employer import update_by_tax_id_use_case, register_employer_use_case
from app.infrastructure.mapper.employer_mapper import employer_to_domain
from app.application.employer.update_employer_use_case import UpdateEmployerByTaxIdUseCase
from app.application.employer.register_employer_use_case import RegisterEmployerUseCase
from app.config.helpers import ok, fail
from app.core.dto.api_response import ApiResponse
from fastapi import HTTPException
from fastapi.params import Path
from app.core.errors.api_errors import ApiErrorCode
from app.config.di_employer import get_employer_by_tax_id_use_case
from app.application.employer.get_employer_by_tax_id_use_case import GetEmployerByTaxIdUseCase
from app.core.dependencies import validate_university_id

router = APIRouter()

@router.post(
    "/push/{university_id}",
    dependencies=[Depends(require_api_key), Depends(validate_university_id)],
    response_model=ApiResponse[dict]
)
@limiter.limit("3000/minute")
def upsert_employer(
    request: Request,
    body: EmployerDTO,
    university_id: str = Path(...),
    uc_update: UpdateEmployerByTaxIdUseCase = Depends(update_by_tax_id_use_case),
    uc_create: RegisterEmployerUseCase = Depends(register_employer_use_case)
):
    employer = employer_to_domain(body)

    
    # 🔴 Validación Correcta
    if employer.taxId is None or employer.taxId == "":
        # Si fail() ya devuelve un JSONResponse (con status y body listos)
        # NO USES .model_dump(), solo retorna la función
        return fail(
            status=400,
            code="INVALID_DATA",
            message="taxId is required for upsert"
        )

    # 1️⃣ UPDATE
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
    "/pull/{university_id}/{tax_id}",
    dependencies=[Depends(validate_university_id)],
    response_model=ApiResponse[dict],
)
def pull_employer(
    tax_id: str,
    university_id: str = Path(...),
    uc: GetEmployerByTaxIdUseCase = Depends(get_employer_by_tax_id_use_case)
):
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
