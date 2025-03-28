import sys

import pytest
import xinfo.x.columns as xcolumns

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Does not work on Windows"
)


@pytest.mark.parametrize(
    "xstruct",
    ["kqfcop", "kqftap23"],
    ids=["not greater than 64 bytes", "not multiple of 64 bytes"],
)
def test_invalid_xstruct_length(test_executable, xstruct):
    """get_xstruct should throw ValueError for an invalid xstruct length."""
    with pytest.raises(ValueError):
        xcolumns.get_xstruct(xstruct)
