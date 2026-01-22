from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Student:
    """
    Modelo de dominio simplificado para estudiantes.
    Reducido de 59+ campos a 28 campos core.
    """

    # === CORE (15 campos) ===
    # Identidad basica
    email: Optional[str] = None
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
    coIdPs: Optional[str] = None
    numeroDocumento: Optional[str] = None

    # === ULIMA INTEGRATION (8 campos) ===
    coPers: Optional[str] = None
    tipoDocumento: Optional[str] = None
    paisEmisionDocumento: Optional[str] = None
    degreeLevel: Optional[str] = None
    ppa: Optional[str] = None
    cicloUltimaMatricula: Optional[str] = None
    fechaEgreso: Optional[str] = None
    alumni: Optional[bool] = None

    # === RESPONSE (5 campos) ===
    id: Optional[str] = None
    uid: Optional[str] = None
    displayName: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    def to_firestore_dict(self) -> dict:
        """Convierte a diccionario para Firestore, excluyendo valores None."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}
