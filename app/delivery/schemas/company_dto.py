from pydantic import BaseModel, HttpUrl, ConfigDict, EmailStr, Field, field_validator, model_validator
from typing import Optional, Literal


class CompanyDTO(BaseModel):
    """
    Data Transfer Object for registering or updating a company in the system.
    Includes organization data and associated users.
    """
    university_id: str = Field(
        ...,
        description="Unique identifier of the university registering the company. Must be in the list of allowed universities.",
        examples=["UCSUR", "UPC", "PUCP"],
    )
    displayName: str = Field(
        ...,
        min_length=2,
        description="Company name as it will be displayed on the platform.",
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
        description="Primary contact email address of the company.",
        examples=["contacto@miempresa.com"],
    )
    status: Literal["active", "inactive"] = Field(
        default="active",
        description="Status of the company on the platform. 'active' for visible and operational, 'inactive' for disabled.",
    )
    logotype: Optional[str] = Field(
        None,
        description="Public URL of the company logo.",
        examples=["https://storage.empresa.com/logo.png"],
    )
    description: Optional[str] = Field(
        None,
        description="Brief company description: business activity, mission, or institutional presentation.",
        examples=["Technology company specializing in enterprise software solutions."],
    )
    website: Optional[HttpUrl] = Field(
        None,
        description="URL of the company's official website.",
        examples=["https://www.miempresa.com"],
    )
    representative: Optional[str] = Field(
        None,
        description="Full name of the legal representative or primary contact of the company.",
        examples=["Carlos López Ríos"],
    )
    sector: Optional[str] = Field(
        None,
        description="Sector or industry to which the company belongs.",
        examples=["Technology", "Education", "Healthcare"],
    )
    phone: Optional[str] = Field(
        None,
        description="Company phone number including country code, digits only without the + sign.",
        examples=["5112345678"],
    )
    model_config = ConfigDict(extra="allow")

    @model_validator(mode='before')
    @classmethod
    def map_cuit_to_ruc(cls, data):
        """If 'cuit' is sent instead of 'ruc', it is automatically mapped to 'ruc'"""
        if isinstance(data, dict):
            if 'cuit' in data and 'ruc' not in data:
                data['ruc'] = data.pop('cuit')
        return data

    @field_validator('ruc')
    @classmethod
    def validate_ruc(cls, v: str):
        import re
        if not re.match(r'^[A-Za-z0-9\-]+$', v):
            raise ValueError('Tax ID can only contain letters, numbers, and hyphens')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]):
        if v:
            if not v.isdigit():
                raise ValueError('Phone number must contain only digits')
        return v
