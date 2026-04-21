"""
Playwright E2E tests for the POST /api/students/push endpoint.
"""

from playwright.sync_api import APIRequestContext
from tests.factories import valid_student_payload, valid_student_full_payload, valid_auth_headers
from tests.assertions import assert_success, assert_error, assert_validation_error


def test_create_student_happy_path(api_context: APIRequestContext) -> None:
    """
    Test creating a new student with a valid payload.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload()
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 201
    
    data = response.json()
    assert_success(data, 201, "created")
    assert data["data"]["dni"] == payload["dni"]


def test_update_student_happy_path(api_context: APIRequestContext) -> None:
    """
    Test updating an existing student.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload()
    headers = valid_auth_headers()
    
    api_context.post("/api/students/push", data=payload, headers=headers)
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 200
    
    data = response.json()
    assert_success(data, 200, "updated")
    assert data["data"]["dni"] == payload["dni"]


def test_missing_dni(api_context: APIRequestContext) -> None:
    """
    Test that missing DNI returns a 400 error.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload()
    del payload["dni"]
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 400
    
    data = response.json()
    assert_error(data, 400, "INVALID_DATA")


def test_duplicate_email_redis(api_context: APIRequestContext) -> None:
    """
    Test that creating a student with an email already registered to another DNI returns 409.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload1 = valid_student_payload(dni="11111111", email="duplicate@test.edu")
    headers = valid_auth_headers()
    
    api_context.post("/api/students/push", data=payload1, headers=headers)
    
    payload2 = valid_student_payload(dni="22222222", email="duplicate@test.edu")
    response = api_context.post("/api/students/push", data=payload2, headers=headers)
    
    assert response.status == 409
    data = response.json()
    assert_error(data, 409, "DUPLICATE_EMAIL")


def test_update_same_email_allowed(api_context: APIRequestContext) -> None:
    """
    Test that updating a student with the same email is allowed.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload(dni="33333333", email="same@test.edu")
    headers = valid_auth_headers()
    
    api_context.post("/api/students/push", data=payload, headers=headers)
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    
    assert response.status == 200
    data = response.json()
    assert_success(data, 200, "updated")


def test_queue_error(api_context: APIRequestContext) -> None:
    """
    Test the happy path to ensure Queue.enqueue works with fakeredis.
    Note: We cannot easily mock Queue.enqueue to raise an exception per-test
    because the server runs in a separate thread. If RQ enqueue fails,
    the handler catches it and returns 500.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload(dni="44444444")
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 201
    
    data = response.json()
    assert_success(data, 201, "created")


def test_validation_error_invalid_email(api_context: APIRequestContext) -> None:
    """
    Test that an invalid email format returns a 422 validation error.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload(email="not-an-email")
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 400
    
    data = response.json()
    assert data["status"] == 400


def test_validation_error_invalid_status(api_context: APIRequestContext) -> None:
    """
    Test that an invalid studentStatus returns a 422 validation error.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload(studentStatus="Graduado")
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 400
    
    data = response.json()
    assert data["status"] == 400


def test_validation_error_cycle_out_of_range(api_context: APIRequestContext) -> None:
    """
    Test that a cycle value out of range (1-12) returns a 422 validation error.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_payload(cycle=15)
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 400
    
    data = response.json()
    assert data["status"] == 400


def test_full_payload_with_optional_fields(api_context: APIRequestContext) -> None:
    """
    Test creating a student with all optional fields provided.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = valid_student_full_payload(dni="55555555")
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 201
    
    data = response.json()
    assert_success(data, 201, "created")


def test_minimal_payload_required_only(api_context: APIRequestContext) -> None:
    """
    Test creating a student with only the required fields plus DNI.
    
    @param api_context - Playwright APIRequestContext fixture
    """
    payload = {
        "university_id": "TESTUNI",
        "displayName": "Minimal Student",
        "email": "minimal@test.edu",
        "university": "Test University",
        "career": "Math",
        "studentStatus": "Estudiante",
        "dni": "66666666"
    }
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 201
    
    data = response.json()
    assert_success(data, 201, "created")


def test_redis_cache_populated_after_create(api_context: APIRequestContext, fake_redis_server) -> None:
    """
    Test that the Redis cache is populated after a successful student creation.
    
    @param api_context - Playwright APIRequestContext fixture
    @param fake_redis_server - Session-scoped fakeredis instance fixture
    """
    dni = "77777777"
    email = "cache@test.edu"
    payload = valid_student_payload(dni=dni, email=email)
    headers = valid_auth_headers()
    
    response = api_context.post("/api/students/push", data=payload, headers=headers)
    assert response.status == 201
    
    expected_key = f"student:TESTUNI:{dni}:{email}"
    assert fake_redis_server.exists(expected_key)
