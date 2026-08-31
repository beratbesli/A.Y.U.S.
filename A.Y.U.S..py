"""Backward-compatible launcher for the A.Y.U.S. CLI."""

from ayus.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
