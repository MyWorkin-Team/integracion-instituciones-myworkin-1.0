from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel


@dataclass
class Employer:
    # Identidad
    id: Optional[str] = None
    label: Optional[str] = None
    name: Optional[str] = None
    alias: Optional[str] = None

    # Identificadores externos / legales
    importedId: Optional[str] = None
    taxId: Optional[str] = None  # RUC

    # Información general
    description: Optional[str] = None
    overview: Optional[str] = None
    website: Optional[str] = None

    # Relaciones (estructuras simples)
    industries: Optional[List[Dict[str, Any]]] = None
    primaryContact: Optional[Dict[str, Any]] = None
    accountManager: Optional[Dict[str, Any]] = None
    parent: Optional[Dict[str, Any]] = None

    # Dirección
    address: Optional[Dict[str, Any]] = None

    # Metadatos
    lastModified: Optional[datetime] = None

    # 🔥 CLAVE
    def to_firestore_dict(self) -> dict:
        data = asdict(self)
        return {k: v for k, v in data.items() if v is not None}
    
