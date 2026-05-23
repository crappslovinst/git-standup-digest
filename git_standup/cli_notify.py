"""CLI entry-point for sending a one-off standup notification.

Usage::

    python -m git_standup.cli_notify --message "3 commits today" \\
        --backend notify-send --title "Daily Standup"
"""
from __future__ import annotations

import argparse
import sys

from git_standup.notifier import NotifierConfig, notify


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="git-standup-notify",
        description="Send a standup digest notification.",
    )
    p.add_argument(
        "--message", "-m",
        default="Your git standup digest is ready.",
        help="Notification body text (default: %(default)s).",
    )
    p.add_argument(
        "--title", "-t",
        default="git-standup-digest",
        help="Notification title (default: %(default)s).",
    )
    p.add_argument(
        "--backend",
        choices=["notify-send", "osascript", "terminal"],
        default=None,
        help="Notification backend to use (auto-detected by default).",
    )
    p.add_argument(
        "--disable",
        action="store_true",
        default=False,
        help="Suppress the notification (useful for dry-run).",
    )
    return p


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    cfg = NotifierConfig(
        title=args.title,
        enabled=not args.disable,
        backend=args.backend,
    )
    notify(args.message, cfg)


if __name__ == "__main__":  # pragma: no cover
    main()
