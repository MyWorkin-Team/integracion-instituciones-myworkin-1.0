from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime


@dataclass
class Company:
    """
    Modelo de dominio para empresas (companies en Firebase).
    """

    # === IDENTIDAD ===
    company_id: Optional[str] = None
    displayName: Optional[str] = None
    logo: Optional[str] = None
    ruc: Optional[str] = None
    importedId: Optional[str] = None

    # === INFORMACION ===
    description: Optional[str] = None
    sitio_web: Optional[str] = None
    contactEmail: Optional[str] = None
    representative: Optional[str] = None
    phone: Optional[str] = None

    # === CLASIFICACION ===
    sector: Optional[str] = None
    companySize: Optional[str] = None
    roles: Optional[dict] = None
    status: Optional[str] = None
    users_companies: Optional[List[dict]] = None

    # === RESPONSE (solo lectura) ===
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_firestore_dict(self) -> dict:
        """Convierte a diccionario para Firestore, excluyendo valores None."""
        data = asdict(self)
        # Excluimos users_companies porque se guardan en una colección aparte
        if "users_companies" in data:
            del data["users_companies"]
        return {k: v for k, v in data.items() if v is not None}
