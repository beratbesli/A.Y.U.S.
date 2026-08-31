"""Backward-compatible launcher for the A.Y.U.S. application."""

import sys

from ayus.cli import main

if __name__ == "__main__":
    if len(sys.argv) == 1:
        from ayus.gui import launch_gui

        raise SystemExit(launch_gui())
    raise SystemExit(main())
