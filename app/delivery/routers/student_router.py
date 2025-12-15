from fastapi import APIRouter, Request

from app.core.limiter import limiter
from app.config.di_student import register_student_use_case
from app.delivery.schemas.student_ulima_dto import StudentULimaDTO
from app.delivery.schemas.student_ucv_dto import StudentUCVDTO
from app.infrastructure.mapper.student_ulima_mapper import ulima_to_domain
from app.infrastructure.mapper.student_ucv_mapper import ucv_to_domain

router = APIRouter()

# -------------------------------------------------
# ULIMA
# -------------------------------------------------
@router.post("/students/ulima")
@limiter.limit("10/minute")
def register_ulima_student(
    request: Request,
    body: StudentULimaDTO
):
    uc = register_student_use_case()
    return {"status": uc.execute(ulima_to_domain(body))}

# -------------------------------------------------
# UCV
# -------------------------------------------------
@router.post("/students/ucv")
@limiter.limit("10/minute")
def register_ucv_student(
    request: Request,
    body: StudentUCVDTO
):
    uc = register_student_use_case()
    return {"status": uc.execute(ucv_to_domain(body))}
