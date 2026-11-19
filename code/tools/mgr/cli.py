"""The mgr command dispatcher."""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

from . import helpers
from .helpers import MgrError

PACKAGE_DIR = Path(__file__).resolve().parent

HELP_FLAGS = {"-?", "/?", "-help", "--help", "-h"}

IGNORED_MODULES = {"cli", "helpers"}


def command_modules() -> dict:
    """Maps command names (as typed on the command line) to module names."""

    modules = {}

    for path in sorted(PACKAGE_DIR.glob("*.py")):
        if path.stem in IGNORED_MODULES or path.stem.startswith("_"):
            continue

        modules[path.stem.replace("_", "-")] = path.stem

    return modules


def find_command(name: str):
    modules = command_modules()

    for candidate in (name, name.replace("_", "-")):
        if candidate in modules:
            return candidate, modules[candidate]

    return None, None


def load_module(module_name: str):
    return importlib.import_module(f"{__package__}.{module_name}")


def make_parser(name: str, module) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=f"python mgr.py {name}",
        description=getattr(module, "DESCRIPTION", None) or None,
        epilog=getattr(module, "EPILOG", None),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    module.add_arguments(parser)

    return parser


def print_command_help(name: str, module) -> None:
    print(f"mgr {name} - {module.SYNOPSIS}")
    print()
    make_parser(name, module).print_help()


def run_command(name: str, module, argv) -> int:
    argv = ["--help" if token in HELP_FLAGS else token for token in argv]

    parser = make_parser(name, module)
    args, extra = parser.parse_known_args(argv)

    if extra and not getattr(module, "PASSTHROUGH", False):
        parser.error(f"unrecognized arguments: {' '.join(extra)}")

    return module.run(args, extra)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--dry-run" in argv:
        argv.remove("--dry-run")
        helpers.set_dry_run(True)
        print("mgr: dry run - commands will be printed but not executed", flush=True)

    if not argv:
        argv = ["help"]

    name, module_name = find_command(argv[0])

    if not name:
        print(f"mgr: invalid command '{argv[0]}' - run 'python mgr.py help' for help", file=sys.stderr)
        return 1

    module = load_module(module_name)

    try:
        return run_command(name, module, argv[1:])
    except MgrError as exc:
        print(f"mgr: error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nmgr: interrupted", file=sys.stderr)
        return 130
    except BrokenPipeError:
        return 1
