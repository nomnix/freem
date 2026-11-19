"""The vs command."""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from types import SimpleNamespace

from . import gen, helpers
from .build import build_path
from .helpers import REPO_ROOT

SYNOPSIS = "Opens Visual Studio for the native project."
DESCRIPTION = (
    "Restores the NuGet packages of the CitizenMP solution and opens it in Visual Studio.\n"
    "The solution is copied to a branch-specific name so branches do not clash."
)
EPILOG = """examples:
  python mgr.py vs
  python mgr.py vs -game server
"""


def add_arguments(parser):
    parser.add_argument(
        "-game",
        "-Game",
        "--game",
        default="five",
        metavar="GAME",
        help="game to open the solution for (default: five)",
    )


def find_devenv():
    for name in ("devenv.exe", "devenv"):
        found = shutil.which(name)

        if found:
            return found

    install_path = os.environ.get("VSINSTALLDIR", "")

    if install_path:
        candidate = Path(install_path) / "Common7" / "IDE" / "devenv.exe"

        if candidate.exists():
            return str(candidate)

    return None


def run(args, extra):
    helpers.vs_init()

    path = build_path(args.game)
    solution = path / "CitizenMP.sln"

    if not solution.exists():
        print(f"{solution} does not exist, generating the project files first", flush=True)
        gen.run(SimpleNamespace(game=args.game, args=""), [])

        if not helpers.DRY_RUN and not solution.exists():
            raise helpers.MgrError(f"project generation did not create {solution}")

    helpers.run([helpers.CI_DIR / "nuget.exe", "restore", solution])

    branch = helpers.git_output("branch", "--show-current") or "detached"
    branch = re.sub(r"[-/\\]", "_", branch)

    branch_solution = path / f"CitizenMP_{args.game}_{branch}.sln"

    if not helpers.DRY_RUN:
        shutil.copyfile(solution, branch_solution)

    devenv = find_devenv()

    if devenv:
        helpers.run([devenv, branch_solution], cwd=REPO_ROOT)
    elif helpers.DRY_RUN:
        helpers.run(["devenv.exe", branch_solution], cwd=REPO_ROOT)
    else:
        raise helpers.MgrError("devenv.exe was not found - is Visual Studio installed?")

    return 0
