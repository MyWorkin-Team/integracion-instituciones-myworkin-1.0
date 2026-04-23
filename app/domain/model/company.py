from dataclasses import dataclass, asdict
from typing import Optional, List
from datetime import datetime


@dataclass
class Company:
    """
    Modelo de dominio para empresas (companies en Firebase).
    """

    # === IDENTIDAD ===
    displayName: Optional[str] = None
    logotype: Optional[str] = None
    ruc: Optional[str] = None
    importedId: Optional[str] = None

    # === INFORMACION ===
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    representative: Optional[str] = None
    phone: Optional[str] = None

    # === CLASIFICACION ===
    sector: Optional[str] = None
    companySize: Optional[str] = None
    roles: Optional[dict] = None
    status: Optional[str] = None
    users_companies: Optional[List[dict]] = None
    forcePasswordChangeOnNextLogin: bool = True

    # === RESPONSE (solo lectura) ===
    id: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    def to_firestore_dict(self) -> dict:
        """Convierte a diccionario para Firestore, excluyendo valores None."""
        data = asdict(self)
        # Excluimos users_companies porque se guardan en una colección aparte
        if "users_companies" in data:
            del data["users_companies"]
        return {k: v for k, v in data.items() if v is not None}
