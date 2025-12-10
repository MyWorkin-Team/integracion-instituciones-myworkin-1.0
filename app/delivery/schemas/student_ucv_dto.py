from pydantic import BaseModel

class StudentUCVDTO(BaseModel):
    codigo: str
    nombres: str
    apellidos: str
    correo: str
    facultad: str
    telefono: str | None = None

    class Config:
        extra = "ignore"
