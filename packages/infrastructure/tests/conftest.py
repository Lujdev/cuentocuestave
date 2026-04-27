"""Shared pytest fixtures for infrastructure tests."""
import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register custom pytest marks."""
    config.addinivalue_line("markers", "integration: mark test as requiring live DB/Redis")


@pytest.fixture(scope="session")
def vcr_config() -> dict:
    """VCR.py configuration for HTTP cassette recording/replay.

    In CI (CI=true) cassettes are never re-recorded — tests must use existing
    cassettes or be replayed from disk. Locally, new HTTP interactions are
    recorded on first run and replayed on subsequent runs.
    """
    return {
        "cassette_library_dir": "tests/cassettes",
        "record_mode": "none" if os.environ.get("CI") == "true" else "new_episodes",
        "filter_headers": ["authorization", "cookie", "set-cookie", "user-agent"],
        "decode_compressed_response": True,
    }
