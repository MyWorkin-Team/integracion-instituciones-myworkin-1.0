from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class StudentDTO(BaseModel):
    """
    DTO para estudiantes.
    Actualizado según el esquema solicitado.
    """
    career: Optional[str] = None
    cycle: Optional[int] = None
    displayName: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[int] = None
    studentStatus: Optional[str] = None  # "Estudiante" | "Egresado"
    university: Optional[str] = None

    # Identificadores (solo lectura en respuesta)
    id: Optional[str] = None
    uid: Optional[str] = None

    # Permite campos extra para backward compatibility con formato antiguo
    model_config = ConfigDict(extra="allow")
