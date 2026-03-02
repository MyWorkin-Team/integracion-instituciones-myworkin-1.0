
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from app.core.limiter import limiter
from app.core.config import require_api_key

from app.delivery.schemas.company_dto import CompanyDTO
from app.config.di_company import upsert_company_use_case, get_company_by_ruc_use_case
from app.infrastructure.mapper.company_mapper import company_to_domain
from app.application.company.upsert_company_use_case import UpsertCompanyUseCase
from app.application.company.get_company_by_tax_id_use_case import GetCompanyByTaxIdUseCase
from app.application.company.company_exceptions import CompanyUserEmailAlreadyExists
from app.core.errors.api_errors import ApiErrorCode
from app.config.helpers import ok, fail
from app.core.dto.api_response import ApiResponse
from fastapi import HTTPException
from fastapi.params import Path
from app.core.errors.api_errors import ApiErrorCode
from app.core.dependencies import validate_university_id

router = APIRouter()

@router.post(
    "/push",
    dependencies=[Depends(require_api_key), Depends(validate_university_id)],
    response_model=ApiResponse[dict]
)
@limiter.limit("3000/minute")
async def upsert_company(
    request: Request,
    body: CompanyDTO,
    uc: UpsertCompanyUseCase = Depends(upsert_company_use_case)
):
    company = company_to_domain(body)

    if company.ruc is None or company.ruc == "":
        return fail(
            status=400,
            code="INVALID_DATA",
            message="ruc is required for upsert"
        )

    # El UC ya maneja internamente si es creación o actualización
    try:
        result = uc.execute(company)

        message = "Company actualizado exitosamente" if result == "updated" else "Company creado exitosamente"
        status_code = 200 if result == "updated" else 201

        return ok(
            status=status_code,
            result=result,
            message=message,
            data={
                "ruc": company.ruc
            }
        )
    except CompanyUserEmailAlreadyExists as e:
        return fail(
            status=409,
            code=ApiErrorCode.EMAIL_ALREADY_EXISTS,
            message=str(e)
        )
    except Exception as e:
        return fail(
            status=500,
            code="UPSERT_ERROR",
            message=str(e)
        )

@router.post(
    "/pull",
    dependencies=[Depends(validate_university_id)],
    response_model=ApiResponse[dict],
)
async def pull_company(
    request: Request,
    uc: GetCompanyByTaxIdUseCase = Depends(get_company_by_ruc_use_case)
):
    try:
        body = await request.json()
        tax_id = body.get("tax_id") or body.get("ruc")
    except Exception:
        tax_id = None

    if not tax_id:
        return fail(
            code="INVALID_DATA",
            message="tax_id is required in body",
            status=400
        )

    # Usamos el tax_id del body como RUC
    company = uc.execute(tax_id)

    if not company:
        return fail(
            code="COMPANY_NOT_FOUND",
            message="No se encontró una empresa con el RUC especificado",
            status=404
        )

    return ok(
        company,
        message="Empresa obtenida correctamente"
    )
