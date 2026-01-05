
from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends

from app.config.di_student import get_student_by_id_use_case
from app.core.limiter import limiter
from app.core.config import require_api_key

from app.delivery.schemas.employer_ulima_dto import EmployerULimaDTO
from app.config.di_employer import get_employer_by_tax_id_use_case, update_by_tax_id_use_case, register_employer_use_case
from app.infrastructure.mapper.employer_ulima_mapper import ulima_employer_to_domain

router = APIRouter()

@router.post("/push/ulima", dependencies=[Depends(require_api_key)])
@limiter.limit("3000/minute")
async def upsert_ulima_employer(
    request: Request,
    body: EmployerULimaDTO
):
    employer = ulima_employer_to_domain(body)

    if not employer.taxId:
        raise HTTPException(
            status_code=400,
            detail="taxId is required for upsert"
        )

    # 1️⃣ UPDATE
    uc_update = update_by_tax_id_use_case()
    updated = uc_update.execute(
        employer.taxId,
        employer.to_firestore_dict()
    )

    if updated:
        return {
            "status": "updated",
            "taxId": employer.taxId
        }

    # 2️⃣ CREATE
    uc_create = register_employer_use_case()
    uc_create.execute(employer)

    return {
        "status": "created",
        "taxId": employer.taxId
    }

@router.get("/pull/ulima/{employer_id}")
async def pull_ulima_employer(employer_id: str):
    uc = get_employer_by_tax_id_use_case()
    employer = uc.execute(employer_id)

    if not employer:
        raise HTTPException(status_code=404, detail="Employer not found")       
    return {
        "status": "ok",
        "mode": "pull",
        "employer": employer
    }
