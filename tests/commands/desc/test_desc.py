import sys
from argparse import Namespace
from collections import OrderedDict
from unittest.mock import ANY

import pytest
from xinfo.commands.desc import describe_table
from xinfo.formatter import Formatter

pytestmark = pytest.mark.skipif(
    sys.platform == "win32", reason="Does not work on Windows"
)


@pytest.fixture
def desc_args(request):
    """Create input arguments for the desc command."""
    args = Namespace(
        command="desc",
        table=None,
        output="table",
        ora_version=19,
    )
    for k, v in request.param.items():
        setattr(args, k, v)
    yield args


TABLEA1 = [
    (
        1,
        OrderedDict(
            [
                ("cno", 1),
                ("nam_ptr", ANY),
                ("nam", "COL1"),
                ("siz", 128),
                ("dty", 1),
                ("typ", 28),
                ("max", 3),
                ("lsz", 2),
                ("lof", 10),
                ("off", 8),
                ("idx", 1),
                ("ipo", 2),
                ("kqfcop_indx", 0),
            ]
        ),
    ),
    (
        2,
        OrderedDict(
            [
                ("cno", 2),
                ("nam_ptr", ANY),
                ("nam", "COL2"),
                ("siz", 1),
                ("dty", 2),
                ("typ", 11),
                ("max", 3),
                ("lsz", 2),
                ("lof", 10),
                ("off", 32),
                ("idx", 1),
                ("ipo", 2),
                ("kqfcop_indx", 1),
                ("func", "f1"),
            ]
        ),
    ),
]


@pytest.mark.parametrize(
    "desc_args, expected",
    [
        pytest.param(*({"table": "X$TABLEA1"}, TABLEA1), id="desc with table name"),
    ],
    indirect=["desc_args"],
)
def test_desc_with_table_name(test_executable, desc_args, mock_formatter, expected):
    """The desc command should return expected output."""
    describe_table(desc_args)
    mock_formatter.assert_called_once_with("desc", OrderedDict(expected))


@pytest.mark.parametrize(
    "desc_args",
    [pytest.param({"table": "X$NO_SUCH_TABLE"}, id="desc with an unknown table")],
    indirect=["desc_args"],
)
def test_desc_no_such_table(test_executable, desc_args):
    """The desc command should throw an error in case the table is not found."""
    with pytest.raises(ValueError) as exc_info:
        describe_table(desc_args)
    assert "Table X$NO_SUCH_TABLE not found" in str(exc_info)
