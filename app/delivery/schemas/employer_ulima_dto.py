from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class EmployerULimaDTO(BaseModel):
    # Identidad
    id: Optional[str] = None
    label: Optional[str] = None
    name: Optional[str] = None
    alias: Optional[str] = None

    # Identificadores externos / legales
    importedId: Optional[str] = None
    taxId: Optional[str] = Field(
        default=None,
        description="RUC de la empresa (11 dígitos)"
    )

    # Información general
    description: Optional[str] = None
    overview: Optional[str] = None
    website: Optional[HttpUrl] = None

    # Relaciones (estructura flexible, sin sub-modelos)
    industries: Optional[List[Dict]] = None
    primaryContact: Optional[Dict] = None
    accountManager: Optional[Dict] = None
    parent: Optional[Dict] = None

    # Dirección
    address: Optional[Dict] = None

    # Metadatos
    lastModified: Optional[datetime] = None

    # class Config:
    #     extra = "ignore"
    #     json_schema_extra = {
    #         "example": {
    #             "label": "ALICORP SAA",
    #             "name": "ALICORP SAA",
    #             "alias": "ALICORP SAA",
    #             "taxId": "20100055237",
    #             "website": "http://www.alicorp.com.pe/alicorp/index.html",
    #             "industries": [
    #                 {"id": "298", "label": "INDUSTRIAS MANUFACTURERAS"}
    #             ],
    #             "primaryContact": {
    #                 "id": "91528f6a479cdded8b25ec7670b28b04",
    #                 "label": "GABRIELA MATTO MUNDACA",
    #                 "link": "/api/public/v1/contacts/91528f6a479cdded8b25ec7670b28b04"
    #             }
    #         }
    #     }
