from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class StudentDTO(BaseModel):
    """
    DTO para registrar o actualizar un estudiante en el sistema.
    Envía los campos requeridos y opcionalmente los adicionales para enriquecer el perfil.
    """
    university_id: str = Field(
        ...,
        description="Identificador único de la universidad emisora del registro. Debe estar en la lista de universidades permitidas.",
        examples=["UCSUR", "UPC", "PUCP"],
    )
    displayName: str = Field(
        ...,
        description="Nombre completo del estudiante tal como aparece en su documento de identidad.",
        examples=["Juan Pérez García"],
    )
    email: EmailStr = Field(
        ...,
        description="Correo electrónico del estudiante. Debe ser único en todo el sistema — no puede estar registrado como estudiante ni como empresa.",
        examples=["juan.perez@universidad.edu.pe"],
    )
    university: str = Field(
        ...,
        description="Nombre completo de la universidad a la que pertenece el estudiante.",
        examples=["Universidad Científica del Sur"],
    )
    career: str = Field(
        ...,
        description="Nombre de la carrera o programa académico que cursa o cursó el estudiante.",
        examples=["Ingeniería de Software"],
    )
    studentStatus: Literal["Estudiante", "Egresado"] = Field(
        ...,
        description="Estado académico actual del estudiante. 'Estudiante' si aún cursa la carrera, 'Egresado' si ya terminó.",
    )
    phone: Optional[str] = Field(
        None,
        description="Número de teléfono incluyendo el código de país sin el signo +. Ejemplo: 51 para Perú seguido del número.",
        examples=["51987654321"],
    )
    dni: Optional[str] = Field(
        None,
        description="Documento de identidad del estudiante. El formato varía según el país de origen. DNI, CI, CC, NIE, etc.",
        examples=["12345678", "V-12345678", "1234567890", "12345678A"],
    )
    cycle: Optional[int] = Field(
        None,
        ge=1,
        le=12,
        description="Ciclo académico actual del estudiante, expresado como número entero entre 1 y 12.",
        examples=[5],
    )
    model_config = ConfigDict(extra="allow")
