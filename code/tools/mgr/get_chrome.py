"""The get-chrome command."""

from __future__ import annotations

from . import helpers
from .helpers import REPO_ROOT

SYNOPSIS = "Downloads the 64-bit CEF dependency to vendor/cef/."
DESCRIPTION = (
    "Downloads the CEF build named in vendor/cef/cef_build_name.txt (the archive is\n"
    "cached in code/build) and replaces the contents of vendor/cef with it."
)


def add_arguments(parser):
    pass


def run(args, extra):
    vendor = REPO_ROOT / "vendor" / "cef"
    save_dir = REPO_ROOT / "code" / "build"
    name_file = vendor / "cef_build_name.txt"

    if not name_file.exists():
        raise helpers.MgrError(f"{name_file} was not found")

    cef_name = name_file.read_text(encoding="ascii", errors="replace").strip()

    if not cef_name:
        raise helpers.MgrError(f"{name_file} does not contain a CEF build name")

    archive = save_dir / f"{cef_name}.zip"

    if archive.exists():
        print(f"using the already downloaded {archive}", flush=True)
    else:
        save_dir.mkdir(parents=True, exist_ok=True)
        helpers.run(
            [
                "curl.exe",
                "--create-dirs",
                "-Lo",
                archive,
                f"https://content.cfx.re/mirrors/vendor/cef/v144/{cef_name}.zip",
            ]
        )

    if not helpers.DRY_RUN and (not archive.exists() or archive.stat().st_size == 0):
        raise helpers.MgrError(f"{archive} was not downloaded")

    if vendor.exists():
        for item in vendor.iterdir():
            if item.is_dir():
                helpers.remove_tree(item)

    vendor.mkdir(parents=True, exist_ok=True)

    extracted = vendor / cef_name

    helpers.run([helpers.WINDIR / "system32" / "tar.exe", "-C", vendor, "-xf", archive])
    helpers.copy_tree(extracted, vendor)
    helpers.remove_tree(extracted)

    return 0
