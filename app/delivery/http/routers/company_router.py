
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from dataclasses import asdict

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
from rq import Queue
from app.infrastructure.queue.redis_client import get_redis_connection
from app.workers.company_tasks import upsert_company_job
from app.infrastructure.cache.redis_cache import RedisCache

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
    university_id: str = Depends(validate_university_id)
):
    company = company_to_domain(body)

    if company.ruc is None or company.ruc == "":
        return fail(
            status=400,
            code="INVALID_DATA",
            message="ruc is required for upsert"
        )

    # Validate RUC is not already registered
    if RedisCache.is_ruc_registered(company.ruc, university_id):
        return fail(
            status=409,
            code="DUPLICATE_RUC",
            message=f"RUC {company.ruc} ya está registrado para esta universidad"
        )

    # Validate company emails are not already registered
    if company.users_companies:
        for user in company.users_companies:
            if user.email and RedisCache.is_email_registered(user.email, university_id, "company"):
                return fail(
                    status=409,
                    code="DUPLICATE_EMAIL",
                    message=f"Email {user.email} ya está registrado para esta universidad"
                )

    try:
        q = Queue("companies", connection=get_redis_connection())
        company_dict = asdict(company)
        job = q.enqueue(upsert_company_job, university_id, company_dict)

        # Register in cache after successful enqueue
        company_email = ""
        if company.users_companies and company.users_companies[0].email:
            company_email = company.users_companies[0].email
        RedisCache.register_company(company.ruc, company_email, university_id)

        return ok(
            status=202,
            result="queued",
            message="Empresa encolada para procesamiento",
            data={"job_id": job.id, "ruc": company.ruc}
        )
    except Exception as e:
        return fail(
            status=500,
            code="QUEUE_ERROR",
            message=f"Error al encolar la empresa: {str(e)}"
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
