from fastapi import APIRouter, HTTPException, Request

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
@limiter.limit("5/minute")
async def register_ulima_student(
    request: Request,
    body: StudentULimaDTO
):
    try:
        uc = register_student_use_case()
        result = uc.execute(ulima_to_domain(body))
        return {"status": result}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "type": type(e).__name__
        }
from app.config.di_student import update_by_co_id_ps_use_case

@router.patch("/students/ulima/by-co-id-ps/{co_id_ps}")
async def update_ulima_student(co_id_ps: str, body: StudentULimaDTO):
    uc = update_by_co_id_ps_use_case()
    data = body.model_dump(exclude_unset=True)

    updated = uc.execute(co_id_ps, data)

    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"status": "updated"}

# -------------------------------------------------
# UCV
# -------------------------------------------------
# @router.post("/students/ucv")
# @limiter.limit("10/minute")
# def register_ucv_student(
#     request: Request,
#     body: StudentUCVDTO
# ):
#     uc = register_student_use_case()
#     return {"status": uc.execute(ucv_to_domain(body))}
