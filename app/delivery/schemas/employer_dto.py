from pydantic import BaseModel, HttpUrl, ConfigDict
from typing import Optional
from datetime import datetime


class EmployerDTO(BaseModel):
    """
    DTO simplificado para empresas ULima.
    Reducido de 15 a 12 campos core.
    """

    # === IDENTIDAD (5 campos) ===
    name: Optional[str] = None
    displayName: Optional[str] = None
    logo: Optional[str] = None
    taxId: Optional[str] = None  # RUC (11 digitos)
    importedId: Optional[str] = None

    # === INFORMACION (4 campos) ===
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
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

    # Permite campos extra para backward compatibility
    model_config = ConfigDict(extra="allow")
