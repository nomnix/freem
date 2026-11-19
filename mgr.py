#!/usr/bin/env python3
"""mgr - the cfx.re developer utility.

Run `python mgr.py help` for the list of commands, or
`python mgr.py <command> -?` for help with a specific command.
"""

import sys
from pathlib import Path

if sys.version_info < (3, 8):
    sys.exit("mgr: Python 3.8 or higher is required")

sys.path.insert(0, str(Path(__file__).resolve().parent / "code" / "tools"))

from mgr.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
