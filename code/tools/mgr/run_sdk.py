"""The run-sdk command."""

from __future__ import annotations

import os

from . import helpers
from .helpers import REPO_ROOT

SYNOPSIS = "Starts Five, listening to the FxDK dev server."
DESCRIPTION = (
    "Launches the built client with -fxdk, pointing it at the dev server started\n"
    "by 'python mgr.py dev-sdk' (http://<computer name>:3000/)."
)


def add_arguments(parser):
    pass


def run(args, extra):
    exe = REPO_ROOT / "code" / "bin" / "five" / "debug" / "FiveM.exe"
    sdk_root = REPO_ROOT / "ext" / "sdk" / "resources" / "sdk-root"

    if not helpers.DRY_RUN:
        if not exe.exists():
            raise helpers.MgrError(f"{exe} was not found - build the client first with 'python mgr.py build'")

        if not sdk_root.exists():
            raise helpers.MgrError(f"{sdk_root} was not found - did you initialise the submodules?")

    host = os.environ.get("COMPUTERNAME", "localhost").lower()

    helpers.run(
        [
            exe,
            "-fxdk",
            "+set",
            "sdk_url",
            f"http://{host}:3000/",
            "+set",
            "sdk_root_path",
            sdk_root.resolve().as_posix(),
        ],
        cwd=exe.parent,
    )

    return 0
