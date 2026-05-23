"""Compute simple statistics over a grouped commit structure."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from git_standup.grouper import GroupedCommits


@dataclass
class DigestStats:
    total_commits: int
    unique_repos: int
    unique_dates: int
    commits_per_repo: Dict[str, int]
    commits_per_date: Dict[str, int]
    busiest_date: str | None
    busiest_repo: str | None


def compute_stats(grouped: GroupedCommits) -> DigestStats:
    """Derive summary statistics from a grouped commit mapping."""
    commits_per_date: Dict[str, int] = {}
    commits_per_repo: Dict[str, int] = {}

    for date_str, repos in grouped.items():
        day_total = 0
        for repo, commits in repos.items():
            count = len(commits)
            day_total += count
            commits_per_repo[repo] = commits_per_repo.get(repo, 0) + count
        commits_per_date[date_str] = day_total

    total_commits = sum(commits_per_date.values())
    unique_repos = len(commits_per_repo)
    unique_dates = len(commits_per_date)

    busiest_date = (
        max(commits_per_date, key=lambda d: commits_per_date[d])
        if commits_per_date
        else None
    )
    busiest_repo = (
        max(commits_per_repo, key=lambda r: commits_per_repo[r])
        if commits_per_repo
        else None
    )

    return DigestStats(
        total_commits=total_commits,
        unique_repos=unique_repos,
        unique_dates=unique_dates,
        commits_per_repo=commits_per_repo,
        commits_per_date=commits_per_date,
        busiest_date=busiest_date,
        busiest_repo=busiest_repo,
    )


def format_stats(stats: DigestStats) -> str:
    """Return a human-readable stats summary string."""
    lines = [
        "── Stats ──────────────────────────",
        f"  Total commits : {stats.total_commits}",
        f"  Repos touched : {stats.unique_repos}",
        f"  Days covered  : {stats.unique_dates}",
    ]
    if stats.busiest_date:
        lines.append(f"  Busiest day   : {stats.busiest_date} ({stats.commits_per_date[stats.busiest_date]} commits)")
    if stats.busiest_repo:
        lines.append(f"  Busiest repo  : {stats.busiest_repo} ({stats.commits_per_repo[stats.busiest_repo]} commits)")
    lines.append("────────────────────────────────────")
    return "\n".join(lines)
