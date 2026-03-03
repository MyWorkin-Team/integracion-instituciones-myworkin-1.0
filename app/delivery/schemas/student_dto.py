from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class StudentDTO(BaseModel):
    """
    DTO para estudiantes.
    Validaciones según el esquema de campos requeridos y opcionales.
    """
    # Campos requeridos
    university_id: str = Field(..., description="Identificador de la universidad")
    displayName: str = Field(..., description="Nombre completo del estudiante")
    email: EmailStr = Field(..., description="Correo electrónico institucional o personal")
    university: str = Field(..., description="Nombre completo de la universidad")
    career: str = Field(..., description="Carrera del estudiante")
    studentStatus: Literal["Estudiante", "Egresado"] = Field(..., description="Estado académico actual")

    # Campos opcionales
    phone: Optional[str] = Field(None, description="Número de teléfono con código de país (ej: 51...)")
    dni: Optional[str] = Field(None, description="Documento de identidad nacional")
    cycle: Optional[int] = Field(None, ge=1, le=12, description="Ciclo académico actual (1 – 12)")

    # Identificadores (solo lectura en respuesta)
    id: Optional[str] = None
    uid: Optional[str] = None

    # Permite campos extra para backward compatibility con formato antiguo
    model_config = ConfigDict(extra="allow")
