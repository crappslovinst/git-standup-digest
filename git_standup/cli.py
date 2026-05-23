"""Command-line interface for git-standup-digest."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

from git_standup.pipeline import PipelineConfig, run_pipeline


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="git-standup",
        description="Generate a readable daily standup summary from git commit history.",
    )
    parser.add_argument(
        "repos",
        nargs="*",
        type=Path,
        default=[Path(".")],
        metavar="REPO",
        help="Paths to local git repositories (default: current directory).",
    )
    parser.add_argument(
        "--author",
        default=None,
        metavar="NAME",
        help="Filter commits by author name or email.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        metavar="N",
        help="Number of past days to include (default: 1).",
    )
    parser.add_argument(
        "--since",
        default=None,
        metavar="DATE",
        help="Start date in YYYY-MM-DD format (overrides --days).",
    )
    parser.add_argument(
        "--no-hash",
        dest="show_hash",
        action="store_false",
        help="Hide commit hashes in output.",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        type=Path,
        metavar="FILE",
        help="Write output to a file instead of stdout.",
    )
    parser.add_argument(
        "--clipboard",
        action="store_true",
        help="Copy output to clipboard.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.since:
        since = args.since
    else:
        since_date = date.today() - timedelta(days=args.days)
        since = since_date.isoformat()

    config = PipelineConfig(
        repo_paths=args.repos,
        author=args.author,
        since=since,
        show_hash=args.show_hash,
        output_file=args.output,
        copy_to_clipboard=args.clipboard,
    )

    run_pipeline(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
