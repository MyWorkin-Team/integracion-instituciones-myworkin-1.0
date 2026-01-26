from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class Employer:
    """
    Modelo de dominio simplificado para empresas.
    Reducido de 15 a 12 campos core.
    """

    # === IDENTIDAD (5 campos) ===
    name: Optional[str] = None
    displayName: Optional[str] = None
    logo: Optional[str] = None
    taxId: Optional[str] = None  # RUC
    importedId: Optional[str] = None

    # === INFORMACION (4 campos) ===
    description: Optional[str] = None
    website: Optional[str] = None
    contactEmail: Optional[str] = None
    phone: Optional[str] = None

    # === CLASIFICACION (3 campos) ===
    sector: Optional[str] = None
    companySize: Optional[str] = None
    status: Optional[str] = None

    # === RESPONSE (solo lectura) ===
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_firestore_dict(self) -> dict:
        """Convierte a diccionario para Firestore, excluyendo valores None."""
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}
