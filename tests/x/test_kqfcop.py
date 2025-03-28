import sys

import pytest
import xinfo.x.kqfcop as kqfcop


@pytest.mark.parametrize(
    "indx, typ, expected",
    [pytest.param(*(1, 7, "f1"), id="test get_func with known type")],
)
@pytest.mark.skipif(sys.platform == "win32", reason="Does not work on Windows")
def test_get_func_known_type(test_executable, force, indx, typ, expected):
    """get_func should return an expected function."""
    func = kqfcop.get_func(indx, typ)
    assert func == expected


@pytest.mark.parametrize("typ", [10, 30])
def test_get_func_unhandled_type(typ):
    """get_func should throw an error for an unhandled type."""
    with pytest.raises(ValueError) as exc_info:
        kqfcop.get_func(0, typ)
    assert "Unhandled kqfcop typ" in str(exc_info)
