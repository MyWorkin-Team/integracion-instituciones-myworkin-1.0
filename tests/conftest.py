"""
Pytest fixtures for Playwright E2E API tests.

Manages FastAPI server lifecycle, environment configuration, and mock
dependencies (fakeredis, Firebase, RQ Queue) for isolated testing.

Environment variables are set at module level to ensure they are available
before any application modules are imported during test collection.
"""

import os
import threading
import time
import logging
from unittest.mock import patch, MagicMock

import fakeredis
import pytest
from playwright.sync_api import sync_playwright, APIRequestContext

# ---------------------------------------------------------------------------
# Environment configuration — must be set BEFORE any app module imports
# ---------------------------------------------------------------------------
os.environ.setdefault("UNIVERSITY_API_KEYS", '{"TESTUNI": "test-key-12345"}')
os.environ.setdefault("ALLOWED_UNIVERSITIES", "TESTUNI")
os.environ.setdefault("PROTECTED_PATHS", "/api/students,/api/companies")
os.environ.setdefault("REDIS_URL", "redis://fake:6379")

logger = logging.getLogger("e2e")

_TEST_PORT = 8999
_BASE_URL = f"http://127.0.0.1:{_TEST_PORT}"


@pytest.fixture(scope="session")
def fake_redis_server():
    """
    Session-scoped fakeredis instance.

    Patches get_redis_connection to return a fakeredis instance before the
    FastAPI server starts, ensuring all RedisCache and Queue operations use
    the in-memory store.

    @returns fakeredis.FakeRedis instance.
    """
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture(scope="session")
def _mocked_server(fake_redis_server):
    """
    Start FastAPI server in a background thread with all external deps mocked.

    Applies patches for:
    - get_redis_connection → fakeredis
    - FirebaseValidator.email_exists_globally → (False, None)
    - FirebaseValidator.student_dni_exists → False
    - FirebaseValidator.company_ruc_exists → False
    - firebase_admin.initialize_app → MagicMock (prevents real Firebase init)

    @returns fakeredis.FakeRedis instance (for per-test flush).
    """
    firebase_validator_path = (
        "app.infrastructure.validation.firebase_validator.FirebaseValidator"
    )

    with (
        patch(
            "app.infrastructure.queue.redis_client.get_redis_connection",
            return_value=fake_redis_server,
        ),
        patch(
            "app.infrastructure.cache.redis_cache.get_redis_connection",
            return_value=fake_redis_server,
        ),
        patch(
            f"{firebase_validator_path}.email_exists_globally",
            return_value=(False, None),
        ),
        patch(
            f"{firebase_validator_path}.student_dni_exists",
            return_value=False,
        ),
        patch(
            f"{firebase_validator_path}.company_ruc_exists",
            return_value=False,
        ),
        patch("firebase_admin.initialize_app", return_value=MagicMock()),
        patch("firebase_admin._apps", {}),
    ):
        import uvicorn

        thread = threading.Thread(
            target=uvicorn.run,
            args=("app.main:app",),
            kwargs={
                "host": "127.0.0.1",
                "port": _TEST_PORT,
                "log_level": "error",
            },
            daemon=True,
        )
        thread.start()
        _wait_for_server(_BASE_URL, timeout=10)
        yield fake_redis_server


def _wait_for_server(url: str, timeout: int = 10) -> None:
    """
    Poll the server until it responds or timeout is reached.

    @param url - Base URL to poll.
    @param timeout - Maximum seconds to wait.
    """
    import httpx

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = httpx.get(f"{url}/docs", timeout=1)
            if resp.status_code in (200, 404):
                return
        except (httpx.ConnectError, httpx.TimeoutException):
            pass
        time.sleep(0.3)
    raise RuntimeError(f"Server at {url} did not start within {timeout}s")


@pytest.fixture(scope="session")
def _playwright_instance():
    """
    Session-scoped Playwright instance for API testing.

    @returns playwright.sync_api.Playwright context manager.
    """
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def api_context(_playwright_instance, _mocked_server):
    """
    Session-scoped Playwright APIRequestContext.

    Pre-configured with base_url pointing to the test FastAPI server.
    Use this fixture in all E2E tests to make HTTP requests.

    @returns playwright.sync_api.APIRequestContext.
    """
    ctx = _playwright_instance.request.new_context(base_url=_BASE_URL)
    yield ctx
    ctx.dispose()


@pytest.fixture(autouse=True)
def _clean_redis(_mocked_server):
    """
    Flush fakeredis before each test for clean state isolation.
    """
    _mocked_server.flushall()
    yield
