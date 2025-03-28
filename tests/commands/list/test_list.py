import sys
from argparse import Namespace
from collections import OrderedDict
from unittest.mock import ANY

import pytest
from xinfo.commands.list import LOGGER, list_tables
from xinfo.formatter import Formatter

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Does not work on Windows"
)


@pytest.fixture
def list_args(request):
    """Create input arguments for the list command."""
    args = Namespace(
        command="list",
        expr=None,
        output="table",
        with_kqftap=False,
    )
    for k, v in request.param.items():
        setattr(args, k, v)
    yield args


TABLEA1 = (
    1,
    OrderedDict(
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
)
TABLEA1_KQFTAP = OrderedDict(
    [
        ("xstruct_ptr", ANY),
        ("cb1_ptr", ANY),
        ("cb2_ptr", ANY),
        ("xstruct", "tablea1_c"),
        ("cb1", "f1"),
        ("cb2", "f2"),
    ]
)
TABLEB1 = (
    2,
    OrderedDict(
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
)
TABLEA2 = (
    3,
    OrderedDict(
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
)


@pytest.mark.parametrize(
    "list_args, expected",
    [
        pytest.param(
            *(
                {"expr": ""},
                [
                    TABLEA1,
                    TABLEB1,
                    TABLEA2,
                ],
            ),
            id="list without params",
        ),
        pytest.param(
            *(
                {"expr": "X$TABLEA*"},
                [
                    TABLEA1,
                    TABLEA2,
                ],
            ),
            id="list with wildcard",
        ),
        pytest.param(
            *(
                {"expr": "X$TABLEB1"},
                [
                    TABLEB1,
                ],
            ),
            id="list with table name",
        ),
        pytest.param(
            *(
                {"expr": "X$NO_SUCH_TABLE"},
                [],
            ),
            id="list without match",
        ),
        pytest.param(
            *(
                {"expr": "X$TABLEA1", "with_kqftap": True},
                [(TABLEA1[0], OrderedDict(**TABLEA1[1], **{"kqftap": TABLEA1_KQFTAP}))],
            ),
            id="list with kqftap",
        ),
    ],
    indirect=["list_args"],
)
def test_list(test_executable, list_args, expected, mock_formatter):
    list_tables(list_args)
    mock_formatter.assert_called_once_with("list", OrderedDict(expected))
