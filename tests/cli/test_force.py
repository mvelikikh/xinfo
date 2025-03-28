from unittest.mock import patch

import pytest
import xinfo.cli as cli
import xinfo.config.settings as settings


@pytest.fixture
def cmd_args(request):
    """Create input arguments for the command."""
    with patch(
        "sys.argv",
        [
            "program",
            "list",
            "--ora-binary",
            "some_path",
            "--ora-version",
            "19",
            "X$TABLE",
        ],
    ) as mock_argv:
        if request.param:
            mock_argv.extend(request.param)
        yield mock_argv


@pytest.mark.parametrize("cmd_args", [()], indirect=["cmd_args"])
def test_force_false_by_default(mock_command, mock_exists, cmd_args):
    """force is set to False by default."""
    cli.main()
    assert not settings.force


@pytest.mark.parametrize("cmd_args", [("--force",)], indirect=["cmd_args"])
def test_force_true_when_specified(mock_command, mock_exists, cmd_args):
    """force is set to True when specified."""
    cli.main()
    assert settings.force
