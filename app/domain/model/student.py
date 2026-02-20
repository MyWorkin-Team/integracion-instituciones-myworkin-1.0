from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Student:
    """
    Modelo de dominio para estudiantes.
    Actualizado según el esquema solicitado.
    """
    career: Optional[str] = None
    createdAt: Optional[datetime] = None
    createdFrom: Optional[str] = None
    cycle: Optional[int] = None
    displayName: Optional[str] = None
    dni: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[int] = None
    searchTokens: Optional[list[str]] = None
    studentStatus: Optional[str] = None  # "Estudiante" | "Egresado"
    university: Optional[str] = None
    updatedAt: Optional[datetime] = None
    userType: str = "student"

    # Identificadores técnicos necesarios para persistencia/API
    id: Optional[str] = None
    uid: Optional[str] = None

    def to_firestore_dict(self) -> dict:
        """Convierte a diccionario para Firestore, excluyendo valores None."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}
