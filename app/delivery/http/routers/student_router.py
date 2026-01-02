from fastapi import APIRouter, HTTPException, Request

from app.core.limiter import limiter
from app.config.di_student import get_student_by_id_use_case, register_student_use_case
from app.delivery.schemas.student_ulima_dto import StudentULimaDTO
from app.infrastructure.mapper.student_ulima_mapper import ulima_to_domain
from app.config.di_student import update_by_co_id_ps_use_case


router = APIRouter()

# -------------------------------------------------
# ULIMA
# -------------------------------------------------
@router.post("/push/ulima")
@limiter.limit("1000/minute")
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

@router.patch("/push/ulima/updated/{co_id_ps}")
async def update_ulima_student(co_id_ps: str, body: StudentULimaDTO):
    uc = update_by_co_id_ps_use_case()
    data = body.model_dump(exclude_unset=True)

    updated = uc.execute(co_id_ps, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "status": "success",
        "message": "Student updated successfully",
        "co_id_ps": co_id_ps
    }

@router.get("/ulima")
async def test_route():
    return {
        "status": "ok",
        "message": "Te listo estudiantes de ulima"
    }

@router.get("/pull/ulima/{student_id}")
async def pull_ulima_student(student_id: str):
    uc = get_student_by_id_use_case()
    student = uc.execute(student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "status": "ok",
        "mode": "pull",
        "student": student
    }
