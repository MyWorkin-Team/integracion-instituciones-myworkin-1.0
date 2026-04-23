"""
Reusable test data builders for StudentDTO and CompanyDTO payloads.

Provides factory functions that return valid request bodies with sensible
defaults. Override any field via keyword arguments.
"""

from typing import Optional


def valid_student_payload(**overrides) -> dict:
    """
    Build a valid student push payload.

    @param overrides - Fields to override in the default payload.
    @returns Dict matching StudentDTO schema.
    """
    base = {
        "university_id": "TESTUNI",
        "cod_student": "EST2024001",
        "displayName": "Juan Perez",
        "email": "juan@test.edu",
        "university": "Test University",
        "career": "Computer Science",
        "studentStatus": "Estudiante",
        "dni": "12345678",
    }
    base.update(overrides)
    return base


def valid_student_full_payload(**overrides) -> dict:
    """
    Build a student payload with all optional fields populated.

    @param overrides - Fields to override in the default payload.
    @returns Dict matching StudentDTO schema with optional fields.
    """
    base = valid_student_payload(
        phone="51987654321",
        cycle=6,
    )
    base.update(overrides)
    return base


def valid_company_payload(**overrides) -> dict:
    """
    Build a valid company push payload.

    @param overrides - Fields to override in the default payload.
    @returns Dict matching CompanyDTO schema.
    """
    base = {
        "university_id": "TESTUNI",
        "displayName": "Test Corp",
        "ruc": "12345678901",
        "email": "contact@test.com",
    }
    base.update(overrides)
    return base


def valid_company_full_payload(**overrides) -> dict:
    """
    Build a company payload with all optional fields.

    @param overrides - Fields to override in the default payload.
    @returns Dict matching CompanyDTO schema with optional fields.
    """
    base = valid_company_payload(
        logotype="https://example.com/logo.png",
        description="A test company",
        website="https://example.com",
        representative="Maria Lopez",
        sector="Technology",
        phone="51912345678",
    )
    base.update(overrides)
    return base


def valid_auth_headers(api_key: str = "test-key-12345") -> dict:
    """
    Build valid authentication headers.

    @param api_key - API key for x-api-key header.
    @returns Dict with x-api-key header.
    """
    return {"x-api-key": api_key}
