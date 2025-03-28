from unittest.mock import patch

import pytest


@pytest.fixture
def force():
    """Set the force flag to ignore existing data files."""
    with patch("xinfo.config.settings.force", True):
        yield
