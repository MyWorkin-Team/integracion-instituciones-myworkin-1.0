from pydantic import BaseModel
from typing import Optional

class StudentULimaDTO(BaseModel):
    id: str
    firstName: str
    lastName: str
    surname: Optional[str] = None
    email: str
    careerCode: str
    phone: Optional[str] = None

    class Config:
        extra = "ignore"
