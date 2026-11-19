"""The wsl-run command."""

from __future__ import annotations

from pathlib import Path

from . import helpers
from .wsl_build import DISTRO

SYNOPSIS = "Runs the built WSL server install in the specified data directory."
DESCRIPTION = (
    "Starts the FXServer built by 'python mgr.py wsl-build' inside the FXServer-Alpine\n"
    "WSL distribution, using the given directory as its data directory."
)


def add_arguments(parser):
    parser.add_argument("path", metavar="PATH", help="data directory to run the server in")
    parser.add_argument(
        "-withdebugger",
        "-WithDebugger",
        "--withdebugger",
        action="store_true",
        help="run the server under gdb",
    )


def run(args, extra):
    directory = Path(args.path).expanduser()

    if not helpers.DRY_RUN and not directory.is_dir():
        raise helpers.MgrError(f"{directory} is not a directory")

    server = "/opt/cfx-server/FXServer"
    server_args = ["+set", "citizen_dir", "/opt/cfx-server/citizen/", "+exec", "server.cfg", *extra]

    helpers.run(
        ["wsl", "-d", DISTRO, "cp", "-a", "/lib/ld-musl-x86_64.so.1", "/opt/cfx-server/"],
        cwd=directory,
    )

    if args.withdebugger:
        helpers.run(["wsl", "-d", DISTRO, "apk", "add", "gdb"], cwd=directory)
        helpers.run(["wsl", "-d", DISTRO, "gdb", "--args", server, *server_args], cwd=directory)
    else:
        helpers.run(
            ["wsl", "-d", DISTRO, "/opt/cfx-server/ld-musl-x86_64.so.1", server, *server_args],
            cwd=directory,
        )

    return 0
