from unittest.mock import patch

import pytest
import xinfo.commands.list as list_


@pytest.fixture
def mock_command():
    """Mock a sample command called by the CLI module."""
    with patch.object(list_, "list_tables") as mock:
        yield mock


@pytest.fixture
def mock_exists():
    """Mock os.path.exists to return True."""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        yield
