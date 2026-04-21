"""
Playwright E2E tests for ApiKeyMiddleware authentication on push endpoints.
"""

from playwright.sync_api import APIRequestContext
from tests import factories


def test_push_student_missing_api_key(api_context: APIRequestContext) -> None:
    """
    Test that pushing a student without an x-api-key header returns 401.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_student_payload()
    response = api_context.post("/api/students/push", data=payload)
    
    assert response.status == 401
    data = response.json()
    assert data["status"] == 401
    assert data["label"] == "Unauthorized"
    assert data["description"] == "Acceso denegado"
    assert data["body"]["error"] == "Unauthorized"


def test_push_company_missing_api_key(api_context: APIRequestContext) -> None:
    """
    Test that pushing a company without an x-api-key header returns 401.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_company_payload()
    response = api_context.post("/api/companies/push", data=payload)
    
    assert response.status == 401
    data = response.json()
    assert data["status"] == 401
    assert data["label"] == "Unauthorized"
    assert data["description"] == "Acceso denegado"
    assert data["body"]["error"] == "Unauthorized"


def test_push_student_invalid_api_key(api_context: APIRequestContext) -> None:
    """
    Test that pushing a student with an invalid x-api-key header returns 401.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_student_payload()
    headers = factories.valid_auth_headers(api_key="wrong-key")
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    
    assert response.status == 401
    data = response.json()
    assert data["status"] == 401
    assert data["label"] == "Unauthorized"
    assert data["description"] == "Acceso denegado"
    assert data["body"]["error"] == "Unauthorized"


def test_push_company_invalid_api_key(api_context: APIRequestContext) -> None:
    """
    Test that pushing a company with an invalid x-api-key header returns 401.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_company_payload()
    headers = factories.valid_auth_headers(api_key="wrong-key")
    response = api_context.post("/api/companies/push", data=payload, headers=headers)
    
    assert response.status == 401
    data = response.json()
    assert data["status"] == 401
    assert data["label"] == "Unauthorized"
    assert data["description"] == "Acceso denegado"
    assert data["body"]["error"] == "Unauthorized"


def test_push_student_missing_university_id(api_context: APIRequestContext) -> None:
    """
    Test that pushing a student with a valid key but missing university_id returns 400.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_student_payload()
    payload.pop("university_id", None)
    headers = factories.valid_auth_headers()
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    
    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"
    assert data["description"] == "university_id missing"
    assert data["body"]["error"] == "Bad Request"
    assert data["body"]["message"] == "university_id es requerido en el body."


def test_push_company_missing_university_id(api_context: APIRequestContext) -> None:
    """
    Test that pushing a company with a valid key but missing university_id returns 400.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_company_payload()
    payload.pop("university_id", None)
    headers = factories.valid_auth_headers()
    response = api_context.post("/api/companies/push", data=payload, headers=headers)
    
    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"
    assert data["description"] == "university_id missing"
    assert data["body"]["error"] == "Bad Request"
    assert data["body"]["message"] == "university_id es requerido en el body."


def test_push_student_disallowed_university(api_context: APIRequestContext) -> None:
    """
    Test that pushing a student with a valid key but disallowed university_id returns 401.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_student_payload(university_id="HACKU")
    headers = factories.valid_auth_headers()
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    
    assert response.status == 401
    data = response.json()
    assert data["status"] == 401
    assert data["label"] == "Unauthorized"
    assert data["description"] == "Acceso denegado"
    assert data["body"]["error"] == "Unauthorized"


def test_push_company_disallowed_university(api_context: APIRequestContext) -> None:
    """
    Test that pushing a company with a valid key but disallowed university_id returns 401.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = factories.valid_company_payload(university_id="HACKU")
    headers = factories.valid_auth_headers()
    response = api_context.post("/api/companies/push", data=payload, headers=headers)
    
    assert response.status == 401
    data = response.json()
    assert data["status"] == 401
    assert data["label"] == "Unauthorized"
    assert data["description"] == "Acceso denegado"
    assert data["body"]["error"] == "Unauthorized"


def test_push_student_empty_body(api_context: APIRequestContext) -> None:
    """
    Test that pushing a student with a valid key but empty body returns 400.

    @param api_context - Playwright APIRequestContext fixture.
    """
    headers = factories.valid_auth_headers()
    response = api_context.post("/api/students/push", data={}, headers=headers)
    
    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"
    assert data["description"] == "university_id missing"
    assert data["body"]["error"] == "Bad Request"
    assert data["body"]["message"] == "university_id es requerido en el body."


def test_push_company_empty_body(api_context: APIRequestContext) -> None:
    """
    Test that pushing a company with a valid key but empty body returns 400.

    @param api_context - Playwright APIRequestContext fixture.
    """
    headers = factories.valid_auth_headers()
    response = api_context.post("/api/companies/push", data={}, headers=headers)
    
    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"
    assert data["description"] == "university_id missing"
    assert data["body"]["error"] == "Bad Request"
    assert data["body"]["message"] == "university_id es requerido en el body."
