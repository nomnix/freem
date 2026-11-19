"""The build command."""

from __future__ import annotations

import os
from types import SimpleNamespace

from . import gen, helpers
from .helpers import REPO_ROOT

SYNOPSIS = "Runs MSBuild on the core native project."
DESCRIPTION = (
    "Builds the CitizenMP solution of the selected game with MSBuild.\n"
    "The Visual Studio developer environment is initialised automatically."
)
EPILOG = """examples:
  python mgr.py build
  python mgr.py build -configuration Release
  python mgr.py build -game server
"""
PASSTHROUGH = True


def add_arguments(parser):
    parser.add_argument(
        "-configuration",
        "-Configuration",
        "--configuration",
        default="Debug",
        metavar="CONFIGURATION",
        help="build configuration (default: Debug)",
    )
    parser.add_argument(
        "-game",
        "-Game",
        "--game",
        default="five",
        metavar="GAME",
        help="game to build: five, server, rdr3 or ny (default: five)",
    )


def build_path(game: str):
    path = REPO_ROOT / "code" / "build" / game

    if game == "server":
        path = path / "windows"

    return path


def run(args, extra):
    helpers.vs_init()

    path = build_path(args.game)
    solution = path / "CitizenMP.sln"

    if not solution.exists():
        print(f"{solution} does not exist, generating the project files first", flush=True)
        gen.run(SimpleNamespace(game=args.game, args=""), [])

        if not helpers.DRY_RUN and not solution.exists():
            raise helpers.MgrError(f"project generation did not create {solution}")

    os.environ.pop("platform", None)

    helpers.run([helpers.CI_DIR / "nuget.exe", "restore", solution])

    os.environ["UseMultiToolTask"] = "true"
    os.environ["EnforceProcessCountAcrossBuilds"] = "true"

    helpers.run(["msbuild", f"/p:configuration={args.configuration}", "/m", *extra, solution])

    return 0
