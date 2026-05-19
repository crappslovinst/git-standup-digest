"""Formats collected commits into a readable standup digest."""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

from git_standup.collector import Commit


@dataclass
class FormatConfig:
    show_repo: bool = True
    show_hash: bool = True
    show_time: bool = False
    group_by_repo: bool = True
    date_header: bool = True
    indent: str = "  "


def _format_commit_line(commit: Commit, config: FormatConfig) -> str:
    parts = []
    if config.show_hash:
        parts.append(f"[{commit.short_hash}]")
    if config.show_time:
        parts.append(f"({commit.timestamp.strftime('%H:%M')})")
    parts.append(commit.message)
    return config.indent + " ".join(parts)


def format_digest(
    commits: list[Commit],
    config: Optional[FormatConfig] = None,
    for_date: Optional[date] = None,
) -> str:
    if config is None:
        config = FormatConfig()

    if not commits:
        return "No commits found."

    lines: list[str] = []

    if config.date_header:
        label = for_date.strftime("%A, %B %d %Y") if for_date else "Today"
        lines.append(f"=== Standup Digest: {label} ===")
        lines.append("")

    if config.group_by_repo:
        repos: dict[str, list[Commit]] = {}
        for commit in commits:
            repos.setdefault(commit.repo, []).append(commit)

        for repo, repo_commits in repos.items():
            if config.show_repo:
                lines.append(f"{repo}/")
            for commit in repo_commits:
                lines.append(_format_commit_line(commit, config))
            lines.append("")
    else:
        for commit in commits:
            prefix = f"{commit.repo}: " if config.show_repo else ""
            lines.append(prefix + _format_commit_line(commit, config).lstrip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
