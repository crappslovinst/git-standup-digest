"""Natural-language summary generator for standup digests."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from git_standup.grouper import GroupedCommits
from git_standup.stats import DigestStats


@dataclass
class SummaryConfig:
    max_highlights: int = 3
    include_repo_breakdown: bool = True
    greeting: str = "Here's what got done:"


def _pluralise(count: int, singular: str, plural: str = "") -> str:
    if not plural:
        plural = singular + "s"
    return f"{count} {singular if count == 1 else plural}"


def _top_repos(stats: DigestStats, n: int) -> List[Tuple[str, int]]:
    """Return the top-n repos by commit count, sorted descending."""
    sorted_repos = sorted(stats.commits_per_repo.items(), key=lambda x: x[1], reverse=True)
    return sorted_repos[:n]


def build_summary(grouped: GroupedCommits, stats: DigestStats, cfg: SummaryConfig | None = None) -> str:
    """Return a short human-readable summary string."""
    if cfg is None:
        cfg = SummaryConfig()

    if stats.total_commits == 0:
        return "Nothing committed yet — go ship something!"

    lines: List[str] = [cfg.greeting, ""]

    commit_str = _pluralise(stats.total_commits, "commit")
    repo_str = _pluralise(stats.total_repos, "repo")
    date_str = _pluralise(stats.total_days, "day")
    lines.append(f"  • {commit_str} across {repo_str} over {date_str}")

    if cfg.include_repo_breakdown:
        highlights = _top_repos(stats, cfg.max_highlights)
        if highlights:
            lines.append("")
            lines.append("  Top repos:")
            for repo, count in highlights:
                lines.append(f"    - {repo}: {_pluralise(count, 'commit')}")

    if stats.busiest_date:
        lines.append("")
        lines.append(f"  Busiest day: {stats.busiest_date}")

    return "\n".join(lines)
