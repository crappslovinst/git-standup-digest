"""CLI entry-point for the background scheduler.

Usage
-----
    python -m git_standup.cli_scheduler --hour 9 --minute 0 /path/to/repo1 /path/to/repo2
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from git_standup.pipeline import PipelineConfig, run_pipeline
from git_standup.scheduler import SchedulerConfig, run_scheduler

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="git-standup-scheduler",
        description="Run git-standup-digest automatically every day at a fixed time.",
    )
    p.add_argument(
        "repos",
        nargs="+",
        metavar="REPO",
        help="Paths to local git repositories to include in the digest.",
    )
    p.add_argument(
        "--hour",
        type=int,
        default=9,
        metavar="H",
        help="Hour of day to run (24-hour clock, default: 9).",
    )
    p.add_argument(
        "--minute",
        type=int,
        default=0,
        metavar="M",
        help="Minute of hour to run (default: 0).",
    )
    p.add_argument(
        "--author",
        default=None,
        help="Only include commits by this author (substring match).",
    )
    p.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of past days to include in each digest (default: 1).",
    )
    p.add_argument(
        "--output",
        default=None,
        help="Write digest to this file instead of stdout.",
    )
    p.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable debug logging.",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    repo_paths = [Path(r) for r in args.repos]
    for rp in repo_paths:
        if not rp.is_dir():
            parser.error(f"Repository path does not exist: {rp}")

    sched_cfg = SchedulerConfig(run_at_hour=args.hour, run_at_minute=args.minute)

    def task() -> None:
        pipeline_cfg = PipelineConfig(
            repos=repo_paths,
            author=args.author,
            days=args.days,
            output=Path(args.output) if args.output else None,
        )
        run_pipeline(pipeline_cfg)

    logger.info(
        "Scheduler configured: daily at %02d:%02d, repos=%s",
        args.hour,
        args.minute,
        [str(r) for r in repo_paths],
    )
    run_scheduler(sched_cfg, task)


if __name__ == "__main__":  # pragma: no cover
    main()
