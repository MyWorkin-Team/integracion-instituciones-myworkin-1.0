from app.domain.model.student import Student
from app.delivery.schemas.student_ulima_dto import StudentULimaDTO

def ulima_to_domain(dto: StudentULimaDTO) -> Student:
    full_name = f"{dto.firstName} {dto.lastName}"
    if dto.surname:
        full_name += f" {dto.surname}"
    full_name = " ".join(full_name.split())

    return Student(
        id=dto.id,
        full_name=full_name,
        first_name=dto.firstName,
        last_name=f"{dto.lastName} {dto.surname}".strip() if dto.surname else dto.lastName,
        email=dto.email.lower(),
        phone=dto.phone,
        birthdate=None,
        gender=None,
        school_code=dto.careerCode
    )
