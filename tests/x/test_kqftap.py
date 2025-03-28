import sys
from collections import OrderedDict
from unittest.mock import ANY, patch

import pytest
import xinfo.binutils as binutils
import xinfo.x.kqftap as kqftap

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Does not work on Windows"
)

KQFTAP = OrderedDict(
    [
        (
            1,
            OrderedDict(
                [
                    ("xstruct_ptr", ANY),
                    ("cb1_ptr", ANY),
                    ("cb2_ptr", ANY),
                    ("xstruct", "tablea1_c"),
                    ("cb1", "f1"),
                    ("cb2", "f2"),
                ]
            ),
        )
    ]
)


def set_ora_version(version):
    with patch("xinfo.config.settings.ora_version", version):
        yield version


@pytest.fixture(params=[19, 21, 23, 25])
def valid_ora_version(request):
    """Valid Oracle Database versions.."""
    yield from set_ora_version(request.param)


@pytest.fixture(params=[10, 12])
def invalid_ora_version(request):
    """Unhandled Oracle Database versions resulting in an error."""
    yield from set_ora_version(request.param)


@pytest.fixture
def kqftap_map(valid_ora_version):
    """Intercept the call to kqftap to return a versioned kqftap structure."""
    kqftaps = {19: "kqftap19", 23: "kqftap23"}
    kqftap_version = max(v for v in kqftaps if v <= valid_ora_version)
    symbol = kqftaps[kqftap_version]
    original_objdump = binutils.objdump_symbol
    with patch("xinfo.config.settings.ora_version", valid_ora_version):
        with patch.object(binutils, "objdump_symbol") as mock_objdump:
            mock_objdump.return_value = original_objdump(symbol)
            yield


def test_get_kqftap_valid_version(test_executable, kqftap_map, force):
    """Expected kqftap is returned for a valid Oracle version."""
    kqftap_map = kqftap.get_kqftap()
    assert kqftap_map == KQFTAP


def test_get_kqftap_invalid_version(test_executable, invalid_ora_version, force):
    """Should throw ValueError for an invalid Oracle version."""
    with pytest.raises(ValueError):
        _ = kqftap.get_kqftap()
