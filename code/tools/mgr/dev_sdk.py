"""The dev-sdk command."""

from __future__ import annotations

from . import helpers
from .helpers import REPO_ROOT

SYNOPSIS = "Runs the FxDK dev server for Five."
DESCRIPTION = "Installs the ext/sdk dependencies with yarn and starts the FxDK development server."


def add_arguments(parser):
    pass


def run(args, extra):
    sdk = REPO_ROOT / "ext" / "sdk"

    if not sdk.exists():
        raise helpers.MgrError(f"{sdk} was not found - did you initialise the submodules?")

    helpers.run(["cmd.exe", "/c", "yarn", "install"], cwd=sdk)
    helpers.run(["cmd.exe", "/c", "yarn", "start"], cwd=sdk)

    return 0
