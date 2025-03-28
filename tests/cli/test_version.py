from unittest.mock import patch

import pytest
import xinfo
import xinfo.cli as cli


@patch("sys.argv", ["program", "--version"])
def test_version(capsys):
    """Correct version should be returned."""
    with pytest.raises(SystemExit):
        cli.main()
    out = capsys.readouterr().out.rstrip()
    assert out == xinfo.__version__
