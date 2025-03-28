"""Collection of binary utilities similar to Linux binutils RPM."""

import logging
import subprocess
import tempfile
from functools import lru_cache

import xinfo.config.settings as settings

LOGGER = logging.getLogger(__name__)


def _get_cmd_output(cmd):
    LOGGER.debug(cmd)
    exitcode, output = subprocess.getstatusoutput(cmd)
    LOGGER.debug("exitcode=%r output=%r", exitcode, output)

    if exitcode != 0:
        raise RuntimeError(
            "Unexpected exitcode = %r output = %r command = %r"
            % (exitcode, output, cmd)
        )

    return output


def get_addr_len(symbol):
    """Return address and length of the given symbol."""
    cmd = "nm -S %(ora_binary)s | grep -w %(symbol)s | awk '{print $1, $2}'"

    cmd = cmd % dict(ora_binary=settings.ora_binary, symbol=symbol)

    output = _get_cmd_output(cmd)

    if not output:
        raise ValueError("%s symbol not found" % (symbol))

    addr, len_ = output.split()

    return (int(addr, 16), int(len_, 16))


def objdump(start_addr, len_):
    """Return a byte-array from the Oracle binary for the given parameters."""
    cmd = (
        "objdump -s --start-address=%(start_addr)d --stop-address=%(stop_addr)d %(ora_binary)s"
        " | awk '/Contents/{m=1;next;} m {print substr($0, length($1)+3, 36)}'"
        " | tr -d ' '"
    )
    cmd = cmd % dict(
        ora_binary=settings.ora_binary,
        start_addr=start_addr,
        stop_addr=start_addr + len_,
    )

    output = _get_cmd_output(cmd)

    dump = bytearray()

    for line in output.split("\n"):
        dump.extend(bytes.fromhex(line))

    return dump


@lru_cache
def get_str_from_addr(addr, max_string_len):
    """Get a NULL terminated string from the address."""
    dump = objdump(addr, max_string_len)
    if b"\x00" not in dump:
        raise ValueError(
            (
                "The NULL character is not found in the dump. "
                "Try to use a larger max_string_length value. "
                "The current string in the dump is %r"
            )
            % (dump.decode("utf-8", errors="replace"))
        )
    nam = dump[: dump.index(b"\x00")].decode("utf-8")
    return nam


def objdump_symbol(symbol):
    """Call objdump for a given symbol."""
    return objdump(*get_addr_len(symbol))


def get_symbols(addr_list):
    """Get symbols for a list of addresses."""
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        LOGGER.debug(fp.name)
        for addr in addr_list:
            print(format(addr, "x"), file=fp)
        fp.flush()

        cmd = "nm %(ora_binary)s | grep -f %(file_name)s" % dict(
            ora_binary=settings.ora_binary, file_name=fp.name
        )
        output = _get_cmd_output(cmd)

        symbols = dict()
        for line in output.split("\n"):
            LOGGER.debug(line)
            addr, _, symbol = line.split()
            func_ptr = int.from_bytes(bytes.fromhex(addr), byteorder="big")
            symbols[func_ptr] = symbol

    return symbols
