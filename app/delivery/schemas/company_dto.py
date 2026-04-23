from pydantic import BaseModel, HttpUrl, ConfigDict, EmailStr, Field, field_validator, model_validator
from typing import Optional, Literal


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
    email: EmailStr = Field(
        ...,
        description="Correo electrónico de contacto principal de la empresa.",
        examples=["contacto@miempresa.com"],
    )
    status: Literal["active", "inactive"] = Field(
        default="active",
        description="Estado de la empresa en la plataforma. 'active' para visible y operativa, 'inactive' para deshabilitada.",
    )
    logotype: Optional[str] = Field(
        None,
        description="URL pública del logo de la empresa.",
        examples=["https://storage.empresa.com/logo.png"],
    )
    description: Optional[str] = Field(
        None,
        description="Descripción breve de la empresa: actividad, misión o presentación institucional.",
        examples=["Empresa tecnológica especializada en soluciones de software empresarial."],
    )
    website: Optional[HttpUrl] = Field(
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
    model_config = ConfigDict(extra="allow")

    @model_validator(mode='before')
    @classmethod
    def map_cuit_to_ruc(cls, data):
        """Si se envía 'cuit' en lugar de 'ruc', lo mapea automáticamente a 'ruc'"""
        if isinstance(data, dict):
            if 'cuit' in data and 'ruc' not in data:
                data['ruc'] = data.pop('cuit')
        return data

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
