"""Control plane entrypoint for SAST Guard CLI."""

import sys

from src.cli.dispatcher import main


def run() -> int:
    """Run control plane dispatcher."""
    return main()


if __name__ == "__main__":
    sys.exit(run())
