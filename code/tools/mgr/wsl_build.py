"""The wsl-build command."""

from __future__ import annotations

import tempfile
from pathlib import Path

from . import helpers
from .helpers import REPO_ROOT

SYNOPSIS = "Prepares and runs an incremental FXServer build for WSL."
DESCRIPTION = (
    "Creates the FXServer-Alpine WSL distribution on first use (or with -rebuild)\n"
    "and runs tools/ci/wsl-build.sh inside it."
)

DISTRO = "FXServer-Alpine"

ALPINE_URL = "http://dl-cdn.alpinelinux.org/alpine/v3.16/releases/x86_64/alpine-minirootfs-3.16.5-x86_64.tar.gz"

SETUP_COMMANDS = (
    "/bin/chmod 755 /",
    "/sbin/apk --no-cache add shadow",
    "/bin/sed -i 's/^export PATH/#export PATH/' /etc/profile",
)


def add_arguments(parser):
    parser.add_argument(
        "-rebuild",
        "-Rebuild",
        "--rebuild",
        action="store_true",
        help="recreate the FXServer-Alpine WSL distribution from scratch",
    )


def distro_exists() -> bool:
    output = helpers.run(["wsl", "-l", "-q"], capture=True, echo=False, check=False).stdout

    return any(DISTRO.lower() in line.strip().lower() for line in output.splitlines())


def run(args, extra):
    build_dir = REPO_ROOT / "code" / "build"

    if args.rebuild:
        helpers.run(["wsl", "--unregister", DISTRO], check=False)

    if not distro_exists():
        build_dir.mkdir(parents=True, exist_ok=True)

        archive = Path(tempfile.gettempdir()) / "alpine.tar.gz"

        helpers.run(["curl.exe", "-Lo", archive, ALPINE_URL])
        helpers.run(["wsl", "--import", DISTRO, build_dir / "alpine-root", archive, "--version", "2"])

        for command in SETUP_COMMANDS:
            helpers.run(["wsl.exe", "-d", DISTRO, "sh", "-c", command])

    revision = helpers.git_output("rev-list", "-1", "HEAD", "tools/ci/", cwd=helpers.CODE_DIR)

    helpers.run(["wsl", "-d", DISTRO, "./tools/ci/wsl-build.sh", revision], cwd=helpers.CODE_DIR)

    return 0
