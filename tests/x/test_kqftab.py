import sys
from collections import OrderedDict
from unittest.mock import ANY

import pytest
import xinfo.x.kqftab as kqftab

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Does not work on Windows"
)


KQFTAB = OrderedDict(
    {
        1: OrderedDict(
            [
                ("obj", 1),
                ("ver", 1),
                ("nam_ptr", ANY),
                ("nam", "X$TABLEA1"),
                ("xstruct_nam_ptr", ANY),
                ("xstruct", "tablea1"),
                ("typ", 4),
                ("flg", 5),
                ("rsz", 2),
                ("coc", 1),
            ]
        ),
        2: OrderedDict(
            [
                ("obj", 1),
                ("ver", 1),
                ("nam_ptr", ANY),
                ("nam", "X$TABLEB1"),
                ("xstruct_nam_ptr", ANY),
                ("xstruct", "tableb1"),
                ("typ", 4),
                ("flg", 5),
                ("rsz", 2),
                ("coc", 1),
            ]
        ),
        3: OrderedDict(
            [
                ("obj", 1),
                ("ver", 1),
                ("nam_ptr", ANY),
                ("nam", "X$TABLEA2"),
                ("xstruct_nam_ptr", ANY),
                ("xstruct", "tablea2"),
                ("typ", 4),
                ("flg", 5),
                ("rsz", 2),
                ("coc", 1),
            ]
        ),
    }
)


@pytest.mark.parametrize("table, expected", [("X$TABLEA1", 1), ("X$TABLEA2", 3)])
def test_get_index(test_executable, force, table, expected):
    """get_index should return the correct index for a given table name."""
    index = kqftab.get_index(table)
    assert index == expected


def test_get_kqftab(test_executable, force):
    """The expected kqftab structure should be returned."""
    kqftab_map = kqftab.get_kqftab()
    assert kqftab_map == KQFTAB
