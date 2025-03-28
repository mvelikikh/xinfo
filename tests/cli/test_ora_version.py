import argparse
import subprocess
from unittest.mock import patch

import pytest
import xinfo.cli as cli
from xinfo.config import settings


@pytest.fixture
def mock_exists_except_oraversion():
    """Mock os.path.exists to return True for all paths except oraversion."""

    def _exists_except_oraversion(*args, **kwargs):
        if args[0].endswith("oraversion"):
            return False
        return True

    with patch("os.path.exists") as mock_exists:
        mock_exists.side_effect = _exists_except_oraversion
        yield mock_exists


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
            "X$TABLE",
        ],
    ) as mock_argv:
        if request.param:
            mock_argv.extend(request.param)
        yield mock_argv


@pytest.mark.parametrize("cmd_args", [("--ora-version", "19")], indirect=["cmd_args"])
def test_version_provided_by_user_used(mock_command, cmd_args, mock_exists):
    """User provided version is used."""
    cli.main()
    assert settings.ora_version == 19


@pytest.mark.parametrize("cmd_args", [None], indirect=["cmd_args"])
@patch.dict("os.environ", {}, clear=True)
def test_default_no_ora_home(cmd_args, mock_exists):
    """The program tries to identify the Oracle version if no version is provided.
    Error is thrown because ORACLE_HOME is not set."""
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        cli.main()
    assert "ORACLE_HOME is not set" in str(exc_info.value)


@pytest.mark.parametrize("cmd_args", [None], indirect=["cmd_args"])
@patch.dict("os.environ", {"ORACLE_HOME": "some_path"}, clear=True)
def test_default_uses_ora_home_that_exists_valid_output(cmd_args, mock_exists):
    """The program tries to determine Oracle version using the supplied ORACLE_HOME.
    oraversion produces valid version."""
    with patch.object(subprocess, "getstatusoutput", autospec=True) as mock_subprocess:
        mock_subprocess.return_value = (0, "19")
        cli.main()
    assert settings.ora_version == 19


@pytest.mark.parametrize("cmd_args", [None], indirect=["cmd_args"])
@patch.dict("os.environ", {"ORACLE_HOME": "some_path"}, clear=True)
@pytest.mark.parametrize("output", ["", "not a number"])
def test_default_uses_ora_home_that_exists_invalid_output(
    cmd_args, mock_exists, output, capsys
):
    """The program tries to determine Oracle version using the supplied ORACLE_HOME.
    oraversion returns non-zero exit code."""
    with patch.object(subprocess, "getstatusoutput", autospec=True) as mock_subprocess:
        mock_subprocess.return_value = (0, output)
        assert cli.main() == 255
        err = capsys.readouterr().err
        assert "Cannot convert Oracle version to number" in err


@pytest.mark.parametrize("cmd_args", [None], indirect=["cmd_args"])
@patch.dict("os.environ", {"ORACLE_HOME": "some_path"}, clear=True)
@pytest.mark.parametrize("return_code", [1, 2, 10])
def test_default_uses_ora_home_that_exists_non_zero_return_code(
    cmd_args, mock_exists, return_code, capsys
):
    """The program tries to determine Oracle version using the supplied ORACLE_HOME.
    oraversion returns non-zero exit code."""
    with patch.object(subprocess, "getstatusoutput", autospec=True) as mock_subprocess:
        mock_subprocess.return_value = (return_code, "some output")
        assert cli.main() == 255
        err = capsys.readouterr().err
        assert "Unexpected exitcode" in err


@pytest.mark.parametrize("cmd_args", [None], indirect=["cmd_args"])
@patch.dict("os.environ", {"ORACLE_HOME": "some_path"}, clear=True)
def test_default_uses_ora_home_without_oraversion(
    cmd_args, mock_exists_except_oraversion
):
    """The program tries to determine Oracle version using the supplied ORACLE_HOME.
    oraversion does not exist."""
    with pytest.raises(argparse.ArgumentTypeError) as exc_info:
        cli.main()
    assert "oraversion does not exist" in str(exc_info)
