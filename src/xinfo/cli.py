"""Command line entry point."""

import argparse
import importlib
import logging
import logging.config
import os
import subprocess
import sys
import traceback

import yaml

import xinfo.config.settings as settings
from xinfo._version import __version__

LOGGER = None


def _setup_logging():
    global LOGGER
    log_file_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "config/logging.yaml"
    )
    with open(log_file_path, "r") as stream:
        config = yaml.load(stream, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
    LOGGER = logging.getLogger(__name__)


def _load_actions():
    """Load argparse actions."""
    this_module_dir = os.path.dirname(os.path.realpath(__file__))
    module_dir_name = "commands"
    module_dir = os.path.join(this_module_dir, module_dir_name)
    package = ".".join([__package__, module_dir_name])
    actions = []
    for filename in os.listdir(module_dir):
        filename = os.path.join(module_dir, filename)
        if os.path.isfile(filename):
            basename = os.path.basename(filename)
            base, extension = os.path.splitext(basename)
            if extension == ".py" and not basename.startswith("_"):
                module = importlib.import_module("." + base, package=package)
                actions.append(module.get_cmd_args())
    return actions


def _ora_bin_default():
    """Oracle binary default value."""
    oh = os.environ.get("ORACLE_HOME")

    if not oh:
        raise argparse.ArgumentTypeError(
            ("Oracle binary path is not specified, and ORACLE_HOME is not set")
        )

    ora_bin = os.path.join(oh, "bin", "oracle")

    if not os.path.exists(ora_bin):
        raise argparse.ArgumentTypeError(
            ("Wrong ORACLE_HOME = %s. %s does not exist" % (oh, ora_bin))
        )

    return ora_bin


def _ora_binary(path):
    """Oracle binary validation."""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError("%s does not exist" % (path))
    return path


def _ora_version_default():
    """Oracle version default value."""
    oh = os.environ.get("ORACLE_HOME")

    if not oh:
        raise argparse.ArgumentTypeError(
            ("Oracle version is not specified, and ORACLE_HOME is not set")
        )

    ora_version_bin = os.path.join(oh, "bin", "oraversion")

    if not os.path.exists(ora_version_bin):
        raise argparse.ArgumentTypeError(
            ("Wrong ORACLE_HOME = %s. %s does not exist" % (oh, ora_version_bin))
        )

    cmd = f"{ora_version_bin} -majorVersion"
    LOGGER.debug(cmd)
    exitcode, output = subprocess.getstatusoutput(cmd)
    LOGGER.debug("exitcode=%r output=%r", exitcode, output)
    if exitcode != 0:
        raise RuntimeError(
            "Unexpected exitcode = %r output = %r command = %r"
            % (exitcode, output, cmd)
        )

    ora_version = None
    try:
        ora_version = int(output)
    except ValueError:
        raise RuntimeError("Cannot convert Oracle version to number: %r" % output)
    return ora_version


def _get_common_parsers():
    """Load common argparse parsers."""
    oracle_parser = argparse.ArgumentParser(add_help=False)
    oracle_parser.add_argument(
        "-b",
        "--ora-binary",
        type=_ora_binary,
        required=False,
        default=_ora_bin_default,
        help=(
            "Specify the path to Oracle binary. "
            "The program will look for $ORACLE_HOME/bin/oracle "
            "if no binary is specified"
        ),
    )
    oracle_parser.add_argument(
        "--ora-version",
        type=int,
        required=False,
        default=_ora_version_default,
        help=(
            "Specify the major Oracle version, such as 19, 23 etc. "
            "The program will execute $ORACLE_HOME/bin/oraversion "
            "if no version is specified"
        ),
    )

    force_parser = argparse.ArgumentParser(add_help=False)
    force_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Set to true to refresh the local cache",
    )

    logging_parser = argparse.ArgumentParser(add_help=False)
    logging_group = logging_parser.add_mutually_exclusive_group()
    logging_group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        help="Enable verbose output",
    )
    logging_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        required=False,
        help="Enable silent mode (only show warnings and errors)",
    )

    fmt_parser = argparse.ArgumentParser(add_help=False)
    fmt_parser.add_argument(
        "-o",
        "--output",
        default="table",
        choices=["table", "json", "html"],
        help="The formatting style for command output",
    )

    return [oracle_parser, force_parser, logging_parser, fmt_parser]


def _handle_common_args(args):
    if args.verbose or args.quiet:
        log_level = logging.DEBUG if args.verbose else logging.WARNING
        loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            logger.setLevel(log_level)

    if args.ora_binary:
        ora_binary = args.ora_binary
        if callable(ora_binary):
            settings.ora_binary = ora_binary()
        else:
            settings.ora_binary = ora_binary

    if args.ora_version:
        ora_version = args.ora_version
        if callable(ora_version):
            settings.ora_version = ora_version()
        else:
            settings.ora_version = ora_version

    if args.force:
        settings.force = args.force

    if args.output:
        settings.format_type = args.output


def main():
    """Command line entry point."""
    try:
        _setup_logging()

        parser = argparse.ArgumentParser(
            prog="xinfo",
            description="Command line utility to display X$ table meta-information",
        )
        parser.add_argument("--version", action="version", version=__version__)

        subparsers = parser.add_subparsers(
            metavar="[command]", description="Available commands"
        )

        actions = _load_actions()
        spd = {}
        for cmd, (action, args_cb, help_) in actions:
            spd[cmd] = sp = subparsers.add_parser(
                cmd, help=help_, parents=_get_common_parsers(), description=help_
            )
            sp.set_defaults(command=cmd)
            if args_cb is not None:
                args_cb(sp)

        if len(sys.argv) == 1:
            parser.print_help(sys.stderr)
            return 1

        args = parser.parse_args()

        _handle_common_args(args)
        LOGGER.debug(args)
        action = dict(actions)[args.command][0]
        action(args)
        sys.stdout.flush()
        return 0
    except argparse.ArgumentTypeError:
        raise
    except BrokenPipeError:  # pragma: no cover
        # Python flushes standard streams on exit; redirect remaining output
        # to devnull to avoid another BrokenPipeError at shutdown
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        return 1  # Python exits with error code 1 on EPIPE
    except Exception:
        sys.stderr.write(traceback.format_exc())
        return 255
