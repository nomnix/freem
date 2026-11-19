"""The gen command."""

from __future__ import annotations

from . import helpers

SYNOPSIS = "Generates Visual Studio project files for the specified Cfx project."
DESCRIPTION = (
    "Regenerates the Visual Studio project files for a game specified on the command line.\n"
    "Use -game to select the game: five (default), server, rdr3 or ny."
)
EPILOG = """examples:
  python mgr.py gen
  python mgr.py gen -game server
"""
PASSTHROUGH = True


def add_arguments(parser):
    parser.add_argument(
        "-game",
        "-Game",
        "--game",
        default="five",
        metavar="GAME",
        help="game to generate the project files for (default: five)",
    )
    parser.add_argument(
        "-args",
        "-Args",
        "--args",
        default="",
        metavar="ARGS",
        help="extra arguments passed to premake5",
    )


def run(args, extra):
    version = helpers.vs_catalog_version()

    if version >= (17, 0):
        vs_line = "vs2022"
    elif version >= (16, 0):
        vs_line = "vs2019"
    else:
        raise helpers.MgrError("Unknown or invalid VS version.")

    command = [helpers.CI_DIR / "premake5.exe", vs_line, f"--game={args.game}"]
    command += helpers.split_args(args.args)
    command += extra

    helpers.run(command, cwd=helpers.CODE_DIR)

    return 0
