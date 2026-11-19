"""Helpers shared by the mgr commands."""

from __future__ import annotations

import locale
import os
import shlex
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
CODE_DIR = REPO_ROOT / "code"
TOOLS_DIR = CODE_DIR / "tools"
CI_DIR = TOOLS_DIR / "ci"

WINDIR = Path(os.environ.get("WINDIR") or os.environ.get("SystemRoot") or r"C:\Windows")

DRY_RUN = False

VS_REQUIRES = "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"


class MgrError(Exception):
    """An error that should be reported to the user without a traceback."""


def set_dry_run(enabled: bool) -> None:
    global DRY_RUN
    DRY_RUN = enabled


def _decode(data: bytes) -> str:
    if not data:
        return ""

    # `wsl -l -q` and some other Windows tools emit UTF-16LE regardless of the console codepage.
    if data.count(b"\x00") > len(data) // 4:
        try:
            return data.decode("utf-16-le")
        except UnicodeDecodeError:
            pass

    for encoding in ("utf-8", locale.getpreferredencoding(False), "cp866", "mbcs"):
        if not encoding:
            continue

        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue

    return data.decode("utf-8", errors="replace")


def run(cmd, cwd=None, check=True, capture=False, echo=True):
    """Runs an external command, echoing it first. Raises MgrError on failure."""

    argv = [str(part) for part in cmd]
    line = subprocess.list2cmdline(argv)

    if echo:
        suffix = f"   [cwd: {cwd}]" if cwd else ""
        print(f"+ {line}{suffix}", flush=True)

    if DRY_RUN and not capture:
        return subprocess.CompletedProcess(argv, 0, stdout="", stderr="")

    try:
        if capture:
            proc = subprocess.run(
                argv,
                cwd=str(cwd) if cwd else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            proc.stdout = _decode(proc.stdout)
            proc.stderr = _decode(proc.stderr)
        else:
            proc = subprocess.run(argv, cwd=str(cwd) if cwd else None)
    except FileNotFoundError:
        raise MgrError(f"'{argv[0]}' was not found - make sure it is installed and available in PATH")
    except OSError as exc:
        raise MgrError(f"could not run '{line}': {exc}")

    if check and proc.returncode != 0:
        detail = ""
        if capture and proc.stderr.strip():
            detail = f": {proc.stderr.strip()}"

        raise MgrError(f"'{line}' failed with exit code {proc.returncode}{detail}")

    return proc


def vswhere(*args) -> str:
    """Queries vswhere.exe, returning trimmed stdout."""

    exe = CI_DIR / "vswhere.exe"

    if not exe.exists():
        raise MgrError(f"vswhere.exe was not found at {exe}")

    return run([exe, *args], capture=True, echo=False).stdout.strip()


def vs_catalog_version() -> tuple:
    """Returns the (major, minor) version of the newest Visual Studio with the C++ toolset."""

    version = vswhere(
        "-prerelease",
        "-latest",
        "-property",
        "catalog_buildVersion",
        "-products",
        "*",
        "-requires",
        VS_REQUIRES,
    )

    if not version:
        raise MgrError("Visual Studio with the C++ toolset was not found")

    parts = version.split(".")

    try:
        return (int(parts[0]), int(parts[1]))
    except (IndexError, ValueError):
        raise MgrError(f"could not parse the Visual Studio version '{version}'")


def _import_batch_env(batch_file: Path) -> None:
    """Runs a batch file and copies the resulting environment into this process."""

    handle, path = tempfile.mkstemp(suffix=".cmd", prefix="mgr-vs-")
    os.close(handle)

    with open(path, "w", encoding="utf-8", newline="\r\n") as temp:
        temp.write("@echo off\n")
        temp.write("chcp 65001 >nul\n")
        temp.write(f'call "{batch_file}" >nul\n')
        temp.write("set\n")

    try:
        proc = subprocess.run(["cmd.exe", "/c", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass

    for line in _decode(proc.stdout).splitlines():
        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key or key.startswith("="):
            continue

        os.environ[key] = value


def vs_init() -> None:
    """Sets up the Visual Studio developer environment."""

    if DRY_RUN:
        print("+ (dry run) initialising the Visual Studio environment", flush=True)
        return

    if os.environ.get("DevEnvDir"):
        return

    install_path = os.environ.get("VSINSTALLDIR", "")

    if not install_path:
        install_path = vswhere(
            "-prerelease",
            "-latest",
            "-property",
            "installationPath",
            "-products",
            "*",
            "-requires",
            VS_REQUIRES,
        )

    if not install_path:
        raise MgrError("Visual Studio with the C++ toolset was not found")

    vcvars = Path(install_path) / "VC" / "Auxiliary" / "Build" / "vcvars64.bat"

    if not vcvars.exists():
        raise MgrError(f"vcvars64.bat was not found at {vcvars}")

    _import_batch_env(vcvars)

    if not os.environ.get("DevEnvDir"):
        raise MgrError("No VC path!")


def split_args(value: str) -> list:
    """Splits an argument string, keeping quoted values intact."""

    if not value:
        return []

    parts = shlex.split(value, posix=False)

    return [part[1:-1] if len(part) >= 2 and part[0] == part[-1] == '"' else part for part in parts]


def git_output(*args, cwd=None) -> str:
    """Runs git and returns trimmed stdout."""

    argv = ["git", *args]
    proc = subprocess.run(argv, cwd=str(cwd or REPO_ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if proc.returncode != 0:
        raise MgrError(f"'{subprocess.list2cmdline(argv)}' failed with exit code {proc.returncode}")

    return _decode(proc.stdout).strip()


def remove_tree(path: Path) -> None:
    import shutil

    if DRY_RUN:
        print(f"+ rmdir /s /q {path}", flush=True)
        return

    shutil.rmtree(path, ignore_errors=True)


def copy_tree(src: Path, dst: Path) -> None:
    import shutil

    if DRY_RUN:
        print(f"+ copy {src}\\* {dst}", flush=True)
        return

    for item in src.iterdir():
        target = dst / item.name

        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True, symlinks=True)
        else:
            shutil.copy2(item, target)
