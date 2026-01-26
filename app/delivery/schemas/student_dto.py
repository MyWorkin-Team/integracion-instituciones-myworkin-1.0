from typing import Optional
from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class StudentDTO(BaseModel):
    """
    DTO simplificado para estudiantes ULima.
    Reducido de 59+ campos a 28 campos core.
    """

    # === CORE (15 campos) ===
    # Identidad basica
    email: Optional[EmailStr] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None
    photoURL: Optional[str] = None
    location: Optional[str] = None

    # Academico
    university: Optional[str] = None
    carrera: Optional[str] = None
    studentStatus: Optional[str] = None  # "Estudiante" | "Egresado"

    # Sistema
    role: Optional[str] = None
    status: Optional[str] = None
    emailVerified: Optional[bool] = None

    # Identificadores
    schoolStudentId: Optional[str] = None
    coIdPs: Optional[str] = None  # REQUERIDO para push
    numeroDocumento: Optional[str] = None

    # === ULIMA INTEGRATION (8 campos) ===
    coPers: Optional[str] = None
    tipoDocumento: Optional[str] = None
    paisEmisionDocumento: Optional[str] = None
    degreeLevel: Optional[str] = None
    ppa: Optional[str] = None
    cicloUltimaMatricula: Optional[str] = None
    fechaEgreso: Optional[date] = None
    alumni: Optional[bool] = None

    # === RESPONSE (5 campos - solo lectura) ===
    id: Optional[str] = None
    displayName: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Permite campos extra para backward compatibility con formato antiguo
    model_config = ConfigDict(extra="allow")
