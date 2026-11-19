"""The natives command."""

from __future__ import annotations

from . import helpers
from .helpers import REPO_ROOT

SYNOPSIS = "Downloads and regenerates natives for all Cfx projects."
DESCRIPTION = "Runs prebuild_natives.cmd from the repository root."


def add_arguments(parser):
    pass


def run(args, extra):
    script = REPO_ROOT / "prebuild_natives.cmd"

    if not script.exists():
        raise helpers.MgrError(f"{script} was not found")

    helpers.run(["cmd.exe", "/c", script], cwd=REPO_ROOT)

    return 0
