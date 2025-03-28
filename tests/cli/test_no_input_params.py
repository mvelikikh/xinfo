from unittest.mock import patch

import xinfo.cli as cli


@patch("sys.argv", ["program"])
def test_no_input_params(capsys):
    """Test without input parameters should show usage."""
    assert cli.main() == 1
    err = capsys.readouterr().err
    assert "usage:" in err
