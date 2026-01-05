from app.domain.model.student import Student
from app.delivery.schemas.student_ulima_dto import StudentULimaDTO
from app.config.helpers import date_to_datetime

def ulima_to_domain(dto: StudentULimaDTO) -> Student:
    data = dto.model_dump()

    full_name_parts = [
        data.get("firstName"),
        data.get("middleName"),
        data.get("lastName"),
        data.get("secondLastName"),
    ]
    fullName = " ".join([p for p in full_name_parts if p])

    rights = data.get("rights") or {}


    return Student(
        # Identidad
        id=data.get("id"),
        displayName=data.get("displayName"),
        email=data.get("email"),
        phone=data.get("phone"),
        firstName=data.get("firstName"),
        middleName=data.get("middleName"),
        lastName=data.get("lastName"),
        secondLastName=data.get("secondLastName"),
        fullName=fullName,
        image=data.get("image"),
        # birthdate=data.get("birthdate"),
        gender=data.get("gender"),
        discapacidad=data.get("discapacidad"),
        alumni=data.get("alumni"),

        # Estado
        role=data.get("role") or "student",
        status=data.get("status") or "active",
        university=data.get("university"),
        verified=data.get("verified", False),
        hasCV=data.get("hasCV", False),
        usoPrimerHerramienta=data.get("usoPrimerHerramienta", False),

        # Fechas
        birthdate=date_to_datetime(data.get("birthdate")),
        createdAt=date_to_datetime(data.get("createdAt")),
        updatedAt=date_to_datetime(data.get("updatedAt")),

        # Identificadores
        schoolStudentId=data.get("schoolStudentId"),
        coPers=data.get("coPers"),
        coIdPs=data.get("coIdPs"),

        # Documentos
        tipoDocumento=data.get("document", {}).get("tipoDocumento"),
        numeroDocumento=data.get("document", {}).get("numeroDocumento"),
        paisEmisionDocumento=data.get("document", {}).get("paisEmisionDocumento"),

        # Dirección
        street=data.get("address", {}).get("street"),
        city=data.get("address", {}).get("city"),
        dependentLocality=data.get("address", {}).get("dependentLocality"),
        state=data.get("address", {}).get("state"),
        zip=data.get("address", {}).get("zip"),
        country=data.get("address", {}).get("country"),

        # Académico
        applicantType=data.get("academic", {}).get("applicantType"),
        degreeLevel=data.get("academic", {}).get("degreeLevel"),
        degreeMode=data.get("academic", {}).get("degreeMode"),
        degreeAward=data.get("academic", {}).get("degreeAward"),
        degreeYear=data.get("academic", {}).get("degreeYear"),
        degreePrimary=data.get("academic", {}).get("degreePrimary"),
        degree=data.get("academic", {}).get("degree"),
        subjectArea=data.get("academic", {}).get("subjectArea"),
        institucionEducacionSuperior=data.get("academic", {}).get("institucionEducacionSuperior"),
        rankingUlima=data.get("academic", {}).get("rankingUlima"),
        ppa=data.get("academic", {}).get("ppa"),
        cicloUltimaMatricula=data.get("academic", {}).get("cicloUltimaMatricula"),
        creditosAprobados=data.get("academic", {}).get("creditosAprobados"),
        creditosMatriculados=data.get("academic", {}).get("creditosMatriculados"),
        fechaEgreso=data.get("academic", {}).get("fechaEgreso"),

        # Estudios
        tienesColegiatura=data.get("studies", {}).get("tienesColegiatura"),
        tienesMaestria=data.get("studies", {}).get("tienesMaestria"),
        tienesMaestriaExternaUl=data.get("studies", {}).get("tienesMaestriaExternaUl"),

        # Preferencias
        languages=data.get("preferences", {}).get("languages"),
        receiveJobBlastEmail=data.get("preferences", {}).get("receiveJobBlastEmail"),
        experientialLearning=data.get("preferences", {}).get("experientialLearning"),

        # Derechos
        canApplyJobs = rights.get("canApplyJobs"),
        canDownloadCertificates = rights.get("canDownloadCertificates"),
        canEditProfile = rights.get("canEditProfile"),


        # Laboral
        situacionLaboral=data.get("situacionLaboral"),
        interesesLaborales=data.get("interesesLaborales") or []
    )
