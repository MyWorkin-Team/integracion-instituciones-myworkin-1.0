from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    id: str
    full_name: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    birthdate: Optional[str]
    gender: Optional[str]
    school_code: Optional[str]
    created_at: Optional[str] = None
