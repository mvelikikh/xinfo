from unittest.mock import patch

import pytest
from xinfo.formatter import Formatter


@pytest.fixture
def mock_formatter():
    """Mock Formatter."""
    with patch.object(Formatter, "__call__") as mock:
        yield mock
