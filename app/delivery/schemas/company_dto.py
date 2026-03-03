from pydantic import BaseModel, HttpUrl, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime


class UserCompanyDTO(BaseModel):
    """
    DTO para la relación entre usuario y empresa (users_companies).
    """

    email: EmailStr
    role: Literal["ceo", "admin", "recruiter"]
    status: Literal["active", "inactive"]

    # Opcionales internos
    companyId: Optional[str] = None
    createdAt: Optional[datetime] = None
    createdFromAdmin: Optional[bool] = None
    uid: Optional[str] = None
    updatedAt: Optional[datetime] = None


class CompanyDTO(BaseModel):
    """
    DTO para empresas (companies en Firebase).
    """

    # === CAMPOS OBLIGATORIOS (según tu employerFields) ===
    university_id: str
    company_id: str = Field(..., pattern="^[a-z0-9-]+$")
    displayName: str = Field(..., min_length=2)
    ruc: str = Field(..., min_length=11, max_length=11)
    contactEmail: EmailStr
    status: Literal["active", "inactive"]

    # === OPCIONALES ===
    logo: Optional[str] = None
    description: Optional[str] = None
    sitio_web: Optional[HttpUrl] = None
    representative: Optional[str] = None
    sector: Optional[str] = None
    phone: Optional[str] = None

    users_companies: Optional[List[UserCompanyDTO]] = None

    # === SOLO RESPONSE ===
    id: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    model_config = ConfigDict(extra="allow")

    # === VALIDADORES ===

    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v: str):
        if not v.isdigit():
            raise ValueError('El RUC debe contener solo números')
        if len(v) != 11:
            raise ValueError('El RUC debe tener exactamente 11 dígitos')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        if v:
            if not v.isdigit():
                raise ValueError('El teléfono debe contener solo números')
        return v