from app.domain.model.student import Student
from app.delivery.schemas.student_dto import StudentDTO
from app.config.helpers import date_to_datetime


def student_to_domain(dto: StudentDTO) -> Student:
    """
    Mapea DTO de estudiante a modelo de dominio.
    Soporta tanto formato nuevo (simplificado) como formato antiguo (backward compatibility).
    """
    data = dto.model_dump()

    # === BACKWARD COMPATIBILITY: Mapeo de campos antiguos ===

    # image -> photoURL
    photo_url = data.get("photoURL") or data.get("image")

    # degree -> carrera
    carrera = data.get("carrera") or data.get("degree")

    # verified -> emailVerified
    email_verified = data.get("emailVerified")
    if email_verified is None:
        email_verified = data.get("verified", False)

    # alumni -> studentStatus
    student_status = data.get("studentStatus")
    if student_status is None:
        alumni = data.get("alumni")
        if alumni is True:
            student_status = "Egresado"
        elif alumni is False:
            student_status = "Estudiante"

    # Calcular displayName automaticamente si no viene
    display_name = data.get("displayName")
    if not display_name:
        name_parts = [data.get("firstName"), data.get("lastName")]
        display_name = " ".join([p for p in name_parts if p]) or None

    # location: construir desde campos antiguos si no viene
    location = data.get("location")
    if not location:
        city = data.get("city")
        country = data.get("country")
        if city and country:
            location = f"{city}, {country}"
        elif city:
            location = city
        elif country:
            location = country

    # degreeLevel: buscar en academic si no viene directamente
    degree_level = data.get("degreeLevel")
    if not degree_level and isinstance(data.get("academic"), dict):
        degree_level = data["academic"].get("degreeLevel")

    # ppa: buscar en academic si no viene directamente
    ppa = data.get("ppa")
    if not ppa and isinstance(data.get("academic"), dict):
        ppa = data["academic"].get("ppa")

    # cicloUltimaMatricula: buscar en academic si no viene directamente
    ciclo = data.get("cicloUltimaMatricula")
    if not ciclo and isinstance(data.get("academic"), dict):
        ciclo = data["academic"].get("cicloUltimaMatricula")

    # fechaEgreso: buscar en academic si no viene directamente
    fecha_egreso = data.get("fechaEgreso")
    if not fecha_egreso and isinstance(data.get("academic"), dict):
        fecha_egreso = data["academic"].get("fechaEgreso")

    # tipoDocumento: buscar en document si no viene directamente
    tipo_doc = data.get("tipoDocumento")
    if not tipo_doc and isinstance(data.get("document"), dict):
        tipo_doc = data["document"].get("tipoDocumento")

    # numeroDocumento: buscar en document si no viene directamente
    numero_doc = data.get("numeroDocumento")
    if not numero_doc and isinstance(data.get("document"), dict):
        numero_doc = data["document"].get("numeroDocumento")

    # paisEmisionDocumento: buscar en document si no viene directamente
    pais_doc = data.get("paisEmisionDocumento")
    if not pais_doc and isinstance(data.get("document"), dict):
        pais_doc = data["document"].get("paisEmisionDocumento")

    return Student(
        # === CORE ===
        email=data.get("email"),
        firstName=data.get("firstName"),
        lastName=data.get("lastName"),
        phone=data.get("phone"),
        photoURL=photo_url,
        location=location,

        university=data.get("university"),
        carrera=carrera,
        studentStatus=student_status,

        role=data.get("role") or "student",
        status=data.get("status") or "active",
        emailVerified=email_verified,

        schoolStudentId=data.get("schoolStudentId"),
        coIdPs=data.get("coIdPs"),
        numeroDocumento=numero_doc,

        # === ULIMA INTEGRATION ===
        coPers=data.get("coPers"),
        tipoDocumento=tipo_doc,
        paisEmisionDocumento=pais_doc,
        degreeLevel=degree_level,
        ppa=ppa,
        cicloUltimaMatricula=ciclo,
        fechaEgreso=date_to_datetime(fecha_egreso),
        alumni=data.get("alumni"),

        # === RESPONSE ===
        id=data.get("id"),
        displayName=display_name,
        createdAt=date_to_datetime(data.get("createdAt")),
        updatedAt=date_to_datetime(data.get("updatedAt")),
    )
