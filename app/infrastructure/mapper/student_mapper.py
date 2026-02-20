from app.domain.model.student import Student
from app.delivery.schemas.student_dto import StudentDTO
from app.config.helpers import date_to_datetime


def student_to_domain(dto: StudentDTO) -> Student:
    data = dto.model_dump()

    # Backward compatibility: Mapeo de campos core si vienen con nombres antiguos
    career = data.get("career") or data.get("carrera") or data.get("degree")
    
    # Manejo de phone (asegurar que sea int si es posible)
    phone = data.get("phone")
    if isinstance(phone, str) and phone.isdigit():
        phone = int(phone)

    # dni: mapear desde numeroDocumento si no viene
    dni = data.get("dni") or data.get("numeroDocumento")

    return Student(
        career=career,
        cycle=data.get("cycle"),
        displayName=data.get("displayName"),
        dni=dni,
        email=data.get("email"),
        phone=phone,
        studentStatus=data.get("studentStatus"),
        university=data.get("university"),
    )
