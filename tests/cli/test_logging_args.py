import logging
from unittest.mock import patch

import pytest
import xinfo.cli as cli


@pytest.fixture
def cmd_args(request):
    """Create input arguments for list."""
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
        mock_argv.append(request.param)
        yield mock_argv


@pytest.mark.parametrize(
    "cmd_args, expected_logging_level",
    [("--verbose", logging.DEBUG), ("--quiet", logging.WARNING)],
    indirect=["cmd_args"],
)
def test_logging_args(mock_command, mock_exists, cmd_args, expected_logging_level):
    """Selected logging level is used."""
    exit_code = cli.main()
    assert exit_code == 0
    assert cli.LOGGER.level == expected_logging_level
