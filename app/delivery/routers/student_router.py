from fastapi import APIRouter
from app.config.di_student import register_student_use_case
from app.delivery.schemas.student_ulima_dto import StudentULimaDTO
from app.delivery.schemas.student_ucv_dto import StudentUCVDTO
from app.infrastructure.mapper.student_ulima_mapper import ulima_to_domain
from app.infrastructure.mapper.student_ucv_mapper import ucv_to_domain

router = APIRouter()

@router.post("/students/ulima")
def register_ulima_student(request: StudentULimaDTO):
    uc = register_student_use_case()
    return {"status": uc.execute(ulima_to_domain(request))}

@router.post("/students/ucv")
def register_ucv_student(request: StudentUCVDTO):
    uc = register_student_use_case()
    return {"status": uc.execute(ucv_to_domain(request))}
