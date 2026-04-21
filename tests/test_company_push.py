"""
Playwright E2E tests for the POST /api/companies/push endpoint.
"""

import pytest
from playwright.sync_api import APIRequestContext
from tests.factories import (
    valid_company_payload,
    valid_company_full_payload,
    valid_auth_headers,
    user_company_payload,
)
from tests.assertions import assert_success, assert_error


def test_create_company_happy_path(api_context: APIRequestContext) -> None:
    """
    Test creating a new company with a valid payload.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(ruc="10000000001")
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 201
    data = response.json()
    assert_success(data, 201, "created")
    assert data["data"]["ruc"] == "10000000001"


def test_update_company_happy_path(api_context: APIRequestContext) -> None:
    """
    Test updating an existing company by sending the same RUC.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(ruc="10000000002")

    api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 200
    data = response.json()
    assert_success(data, 200, "updated")
    assert data["data"]["ruc"] == "10000000002"


def test_missing_ruc_returns_validation_error(
    api_context: APIRequestContext,
) -> None:
    """
    Test payload with empty RUC triggers Pydantic validation (400).

    Pydantic min_length=11 catches empty string before router-level check.
    App returns 400 via validation_exception_handler.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(ruc="")
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"


def test_duplicate_user_email_redis(api_context: APIRequestContext) -> None:
    """
    Test creating a company with a user email already registered returns 409.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload1 = valid_company_payload(
        ruc="10000000003",
        users_companies=[user_company_payload(email="dup-user@test.com")],
    )
    api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload1,
    )

    payload2 = valid_company_payload(
        ruc="10000000004",
        users_companies=[user_company_payload(email="dup-user@test.com")],
    )
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload2,
    )

    assert response.status == 409
    data = response.json()
    assert_error(data, 409, "DUPLICATE_EMAIL")


@pytest.mark.xfail(
    reason="App bug: router checks email globally without skipping for same-RUC update",
    strict=True,
)
def test_update_allows_same_email(api_context: APIRequestContext) -> None:
    """
    Test updating a company with the same user email should succeed.

    Known app bug: router does not skip email validation when the RUC is
    already registered (unlike student router which checks dni_already_registered).

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(
        ruc="10000000005",
        users_companies=[user_company_payload(email="same-co@test.com")],
    )

    api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 200
    data = response.json()
    assert_success(data, 200, "updated")


@pytest.mark.xfail(
    reason="App bug: @field_validator raises ValueError whose ctx is not JSON serializable, returns 500",
    strict=True,
)
def test_validation_error_invalid_ruc_non_numeric(
    api_context: APIRequestContext,
) -> None:
    """
    Test payload with non-numeric RUC returns validation error.

    Known app bug: the @field_validator('ruc') raises ValueError, which
    Pydantic puts into exc.errors() ctx field. The validation_exception_handler
    tries to serialize this via JSONResponse, causing a 500.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(ruc="1234567890a")
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 400


def test_validation_error_ruc_too_short(
    api_context: APIRequestContext,
) -> None:
    """
    Test payload with RUC shorter than 11 digits returns 400 validation error.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(ruc="123")
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"


def test_validation_error_invalid_company_id(
    api_context: APIRequestContext,
) -> None:
    """
    Test payload with invalid company_id format returns 400 validation error.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(company_id="INVALID!")
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"


def test_validation_error_display_name_too_short(
    api_context: APIRequestContext,
) -> None:
    """
    Test payload with displayName shorter than 2 characters returns 400 validation error.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(displayName="A")
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 400
    data = response.json()
    assert data["status"] == 400
    assert data["label"] == "Bad Request"


def test_company_without_users_companies(
    api_context: APIRequestContext,
) -> None:
    """
    Test creating a company without users_companies returns 201.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(ruc="10000000006")
    payload.pop("users_companies", None)
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 201
    data = response.json()
    assert_success(data, 201, "created")


def test_company_with_multiple_users(api_context: APIRequestContext) -> None:
    """
    Test creating a company with multiple users in users_companies returns 201.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_payload(
        ruc="10000000007",
        users_companies=[
            user_company_payload(email="user1-co@test.com"),
            user_company_payload(email="user2-co@test.com"),
            user_company_payload(email="user3-co@test.com"),
        ],
    )
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 201
    data = response.json()
    assert_success(data, 201, "created")


def test_redis_cache_populated_after_create(
    api_context: APIRequestContext,
    fake_redis_server,
) -> None:
    """
    Test that Redis cache is populated after creating a company.

    @param api_context - Playwright APIRequestContext fixture.
    @param fake_redis_server - Session-scoped fakeredis instance.
    """
    ruc = "10000000008"
    payload = valid_company_payload(ruc=ruc)
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 201

    keys = fake_redis_server.keys(f"company:TESTUNI:{ruc}:*")
    assert len(keys) > 0


def test_full_payload_with_all_optional_fields(
    api_context: APIRequestContext,
) -> None:
    """
    Test creating a company with all optional fields populated returns 201.

    @param api_context - Playwright APIRequestContext fixture.
    """
    payload = valid_company_full_payload(ruc="10000000009")
    response = api_context.post(
        "/api/companies/push",
        headers=valid_auth_headers(),
        data=payload,
    )

    assert response.status == 201
    data = response.json()
    assert_success(data, 201, "created")
