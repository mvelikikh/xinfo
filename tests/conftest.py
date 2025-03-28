"""Shared fixtures."""

from unittest.mock import patch

import pytest


def pytest_addoption(parser):
    """Pass test executable through command line."""
    parser.addoption("--test-executable", action="store", help="test executable")


@pytest.fixture
def test_executable(request):
    """Overwrite ora_binary using the value from the command line."""
    with patch(
        "xinfo.config.settings.ora_binary",
        request.config.getoption("--test-executable"),
    ):
        yield
