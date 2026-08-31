import sys

from .cli import main

if __name__ == "__main__":
    if len(sys.argv) == 1:
        from .gui import launch_gui

        raise SystemExit(launch_gui())
    raise SystemExit(main())
