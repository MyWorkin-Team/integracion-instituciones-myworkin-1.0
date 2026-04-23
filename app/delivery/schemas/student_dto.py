from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field


class StudentDTO(BaseModel):
    """
    Data Transfer Object for registering or updating a student in the system.
    Send required fields and optionally additional fields to enrich the profile.
    """
    university_id: str = Field(
        ...,
        description="Unique identifier of the university issuing the registration. Must be in the list of allowed universities.",
        examples=["UCSUR", "UPC", "PUCP"],
    )
    cod_student: str = Field(
        ...,
        description="Unique student code assigned by the university.",
        examples=["EST2024001", "ALU-2024-001"],
    )
    displayName: str = Field(
        ...,
        description="Full name of the student as it appears in their identity document.",
        examples=["Juan Pérez García"],
    )
    email: EmailStr = Field(
        ...,
        description="Student email address. Must be unique in the entire system — cannot be registered as both student and company.",
        examples=["juan.perez@universidad.edu.pe"],
    )
    university: str = Field(
        ...,
        description="Full name of the university to which the student belongs.",
        examples=["Universidad Científica del Sur"],
    )
    career: str = Field(
        ...,
        description="Name of the career or academic program that the student is or was pursuing.",
        examples=["Software Engineering"],
    )
    studentStatus: Literal["Estudiante", "Egresado"] = Field(
        ...,
        description="Current academic status of the student. 'Estudiante' if still studying, 'Egresado' if graduated.",
    )
    phone: Optional[str] = Field(
        None,
        description="Phone number including country code without the + sign. Example: 51 for Peru followed by the number.",
        examples=["51987654321"],
    )
    dni: Optional[str] = Field(
        None,
        description="Student identity document. Format varies depending on country of origin. DNI, CI, CC, NIE, etc.",
        examples=["12345678", "V-12345678", "1234567890", "12345678A"],
    )
    cycle: Optional[int] = Field(
        None,
        ge=1,
        le=12,
        description="Current academic cycle of the student, expressed as an integer between 1 and 12.",
        examples=[5],
    )
    model_config = ConfigDict(extra="allow")
