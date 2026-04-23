from pydantic import BaseModel, HttpUrl, ConfigDict, EmailStr, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime


class UserCompanyDTO(BaseModel):
    """
    Representa a un usuario vinculado a la empresa con su rol y estado dentro de la organización.
    """
    email: EmailStr = Field(
        ...,
        description="Correo electrónico del usuario. Debe ser único en todo el sistema.",
        examples=["reclutador@empresa.com"],
    )
    role: Literal["ceo", "admin", "recruiter"] = Field(
        ...,
        description="Rol del usuario dentro de la empresa. Valores válidos: 'ceo' (propietario/CEO), 'admin' (gestor de cuenta), 'recruiter' (publicador de ofertas)",
        examples=["ceo"],
    )
    status: Literal["active", "inactive"] = Field(
        ...,
        description="Estado del usuario en la empresa. 'active' para habilitado, 'inactive' para deshabilitado.",
        examples=["active"],
    )
    model_config = ConfigDict(extra="allow")


class CompanyDTO(BaseModel):
    """
    DTO para registrar o actualizar una empresa en el sistema.
    Incluye los datos de la organización y los usuarios vinculados a ella.
    """
    university_id: str = Field(
        ...,
        description="Identificador único de la universidad que registra la empresa. Debe estar en la lista de universidades permitidas.",
        examples=["UCSUR", "UPC", "PUCP"],
    )
    company_id: str = Field(
        ...,
        pattern="^[a-z0-9_-]+$",
        description="Identificador único de la empresa en formato slug (solo minúsculas, números, guiones). Se usa como clave en la base de datos.",
        examples=["mi-empresa-sac"],
    )
    displayName: str = Field(
        ...,
        min_length=2,
        description="Nombre comercial de la empresa tal como se mostrará en la plataforma.",
        examples=["Mi Empresa S.A.C."],
    )
    ruc: str = Field(
        ...,
        description=(
            "Número de identificación tributaria de la empresa. Conocido como RUC en Perú, "
            "NIT en Colombia, CUIT/CUIL en Argentina, RUT en Chile, RFC en México."
        ),
        examples=["20123456789"],
    )
    contactEmail: EmailStr = Field(
        ...,
        description="Correo electrónico de contacto principal de la empresa.",
        examples=["contacto@miempresa.com"],
    )
    status: Literal["active", "inactive"] = Field(
        ...,
        description="Estado de la empresa en la plataforma. 'active' para visible y operativa, 'inactive' para deshabilitada.",
    )
    logo: Optional[str] = Field(
        None,
        description="URL pública del logo de la empresa.",
        examples=["https://storage.empresa.com/logo.png"],
    )
    description: Optional[str] = Field(
        None,
        description="Descripción breve de la empresa: actividad, misión o presentación institucional.",
        examples=["Empresa tecnológica especializada en soluciones de software empresarial."],
    )
    sitio_web: Optional[HttpUrl] = Field(
        None,
        description="URL del sitio web oficial de la empresa.",
        examples=["https://www.miempresa.com"],
    )
    representative: Optional[str] = Field(
        None,
        description="Nombre completo del representante legal o contacto principal de la empresa.",
        examples=["Carlos López Ríos"],
    )
    sector: Optional[str] = Field(
        None,
        description="Sector o industria al que pertenece la empresa.",
        examples=["Tecnología", "Educación", "Salud"],
    )
    phone: Optional[str] = Field(
        None,
        description="Número de teléfono de la empresa incluyendo código de país, solo dígitos sin el signo +.",
        examples=["5112345678"],
    )
    users_companies: Optional[List[UserCompanyDTO]] = Field(
        None,
        description="Lista de usuarios vinculados a la empresa con su rol y estado. OBLIGATORIO: Al crear una empresa, debe incluir al menos un usuario con role='ceo'. Cada usuario debe tener un email único en el sistema.",
    )
    model_config = ConfigDict(extra="allow")

    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v: str):
        import re
        if not re.match(r'^[A-Za-z0-9\-]+$', v):
            raise ValueError('El RUC solo puede contener letras, números y guiones')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        if v:
            if not v.isdigit():
                raise ValueError('El teléfono debe contener solo números')
        return v
