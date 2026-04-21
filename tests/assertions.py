"""
Shared assertion helpers for ApiResponse format validation.

All API responses conform to the ApiResponse schema:
  { status, success, message, result, data, error }
"""


def assert_success(response_json: dict, status: int, result: str) -> None:
    """
    Assert a successful ApiResponse.

    @param response_json - Parsed JSON response body.
    @param status - Expected HTTP status code.
    @param result - Expected result string ("created" or "updated").
    """
    assert response_json["status"] == status, (
        f"Expected status {status}, got {response_json['status']}"
    )
    assert response_json["success"] is True, (
        f"Expected success=True, got {response_json['success']}"
    )
    assert response_json["result"] == result, (
        f"Expected result='{result}', got '{response_json.get('result')}'"
    )
    assert response_json.get("error") is None, (
        f"Expected error=None, got {response_json.get('error')}"
    )


def assert_error(response_json: dict, status: int, code: str) -> None:
    """
    Assert an error ApiResponse.

    @param response_json - Parsed JSON response body.
    @param status - Expected HTTP status code.
    @param code - Expected error code (e.g. "INVALID_DATA").
    """
    assert response_json["status"] == status, (
        f"Expected status {status}, got {response_json['status']}"
    )
    assert response_json["success"] is False, (
        f"Expected success=False, got {response_json['success']}"
    )
    assert response_json["error"]["code"] == code, (
        f"Expected error.code='{code}', got '{response_json['error']['code']}'"
    )


def assert_validation_error(response_json: dict) -> None:
    """
    Assert a Pydantic validation error response (422).

    @param response_json - Parsed JSON response body from validation_exception_handler.
    """
    assert response_json["status"] == 422, (
        f"Expected status 422, got {response_json.get('status')}"
    )
