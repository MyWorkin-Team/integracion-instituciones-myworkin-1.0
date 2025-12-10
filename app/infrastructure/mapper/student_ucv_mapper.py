from app.domain.model.student import Student
from app.delivery.schemas.student_ucv_dto import StudentUCVDTO

def ucv_to_domain(dto: StudentUCVDTO) -> Student:
    return Student(
        id=dto.codigo,
        full_name=f"{dto.nombres} {dto.apellidos}".strip(),
        first_name=dto.nombres,
        last_name=dto.apellidos,
        email=dto.correo.lower(),
        phone=dto.telefono,
        birthdate=None,
        gender=None,
        school_code=dto.facultad
    )
