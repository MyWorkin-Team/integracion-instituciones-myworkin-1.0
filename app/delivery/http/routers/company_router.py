
import logging
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
from app.infrastructure.validation.firebase_validator import FirebaseValidator

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/push",
    dependencies=[Depends(require_api_key), Depends(validate_university_id)],
    response_model=ApiResponse[dict],
    summary="Create or update company",
    description="""
Creates or updates a company in the system.

**Behavior:**
- **Create**: If the tax ID (RUC) does not exist, a new company is created
- **Update**: If the tax ID (RUC) already exists, the existing company is updated

**Required fields:**
- `university_id`: University identifier (e.g., UCC-TEST, UCSUR)
- `displayName`: Company name (min. 2 characters)
- `ruc`: Tax identification number (also accepts 'cuit' which is mapped to 'ruc')
- `email`: Contact email address

**Optional fields:**
- `logotype`: Logo URL
- `description`: Company description
- `website`: Official website
- `representative`: Legal representative name
- `sector`: Industry/sector
- `phone`: Phone number (digits only)
- `status`: "active" (default) or "inactive"

**Automatic on creation:**
- An 'owner' role user is automatically created using the company email
- The user password is the company's tax ID (RUC)
- `forcePasswordChangeOnNextLogin` is set to true

**Validations:**
- Email must be unique in the system (cannot be used by students or other companies)
- Tax ID (RUC) can only contain letters, numbers, and hyphens
- Phone can only contain digits
    """,
)
@limiter.limit("3000/minute")
async def upsert_company(
    request: Request,
    body: CompanyDTO,
):
    university_id = body.university_id
    company = company_to_domain(body)

    if company.ruc is None or company.ruc == "":
        return fail(
            status=400,
            code="INVALID_DATA",
            message="ruc is required for upsert"
        )

    ruc_already_registered = RedisCache.is_ruc_registered(company.ruc, university_id)

    # Validate company emails globally (Cascading: Redis → Firebase)
    if company.users_companies:
        for user in company.users_companies:
            user_email = user.email if hasattr(user, 'email') else user.get("email") if isinstance(user, dict) else None
            if user_email:
                # Check Redis first
                exists_in_redis, redis_type = RedisCache.is_email_registered_globally(user_email)
                if exists_in_redis:
                    return fail(
                        status=409,
                        code="DUPLICATE_EMAIL",
                        message=f"Email {user_email} is already registered as {redis_type} in the system"
                    )

                # Check Firebase (authority)
                exists_in_firebase, firebase_type = FirebaseValidator.email_exists_globally(user_email)
                if exists_in_firebase:
                    return fail(
                        status=409,
                        code="DUPLICATE_EMAIL",
                        message=f"Email {user_email} already exists as {firebase_type} in the system"
                    )

    try:
        q = Queue("companies", connection=get_redis_connection())
        company_dict = asdict(company)
        job = q.enqueue(upsert_company_job, university_id, company_dict)

        if ruc_already_registered:
            return ok(status=200, result="updated", message="Company updated successfully", data={"ruc": company.ruc})
        else:
            return ok(status=201, result="created", message="Company created successfully", data={"ruc": company.ruc})
    except Exception as e:
        return fail(
            status=500,
            code="QUEUE_ERROR",
            message=f"Error queuing company: {str(e)}"
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
            message="Company not found with the specified tax ID",
            status=404
        )

    return ok(
        company,
        message="Company retrieved successfully"
    )
