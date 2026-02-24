from pydantic import BaseModel, HttpUrl, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List, Any
from datetime import datetime
import re


class UserCompanyDTO(BaseModel):
    """
    DTO para la relación entre usuario y empresa (users_companies).
    """
    companyId: Optional[str] = None
    createdAt: Optional[Any] = None
    createdFromAdmin: Optional[bool] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, min_length=2)
    status: Optional[str] = Field("active", pattern="^(active|inactive|pending)$")
    uid: Optional[str] = None
    updatedAt: Optional[Any] = None


class CompanyDTO(BaseModel):
    """
    DTO para empresas (companies en Firebase).
    """

    # === IDENTIDAD ===
    company_id: Optional[str] = None
    displayName: Optional[str] = Field(None, min_length=2)
    logo: Optional[str] = None
    ruc: Optional[str] = Field(None, min_length=11, max_length=11)
    importedId: Optional[str] = None

    # === INFORMACION ===
    description: Optional[str] = None
    sitio_web: Optional[HttpUrl] = None
    contactEmail: Optional[EmailStr] = None
    representative: Optional[str] = None
    phone: Optional[str] = None

    # === CLASIFICACION ===
    sector: Optional[str] = None
    companySize: Optional[str] = None
    roles: Optional[dict] = None
    status: Optional[str] = Field("active", pattern="^(active|inactive|pending)$")
    users_companies: Optional[List[UserCompanyDTO]] = None

    # === RESPONSE (solo lectura) ===
    id: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    # Permite campos extra para backward compatibility
    model_config = ConfigDict(extra="allow")

    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v: Optional[str]):
        if v is not None:
            if not v.isdigit():
                raise ValueError('El RUC debe contener solo números')
            if len(v) != 11:
                raise ValueError('El RUC debe tener exactamente 11 dígitos')
        return v
