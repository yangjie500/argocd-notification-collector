"""Interface for ``python -m event_collector``."""

from argparse import ArgumentParser
from collections.abc import Sequence

import uvicorn

from . import __version__

__all__ = ["main"]


def main(args: Sequence[str] | None = None) -> None:
    """Argument parser for the CLI."""
    parser = ArgumentParser()
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=__version__,
    )

    subparsers = parser.add_subparsers(dest="command")
    serve = subparsers.add_parser("serve")
    serve.add_argument("--host", default="0.0.0.0")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--reload", action="store_true")

    parsed = parser.parse_args(args)

    if parsed.command == "serve":
        uvicorn.run(
            "event_collector.app:app",
            host=parsed.host,
            port=parsed.port,
            reload=parsed.reload,
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
