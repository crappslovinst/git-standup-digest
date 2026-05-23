"""Groups and sorts commits for digest presentation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

from git_standup.collector import Commit


@dataclass
class GroupConfig:
    sort_repos_alpha: bool = True
    sort_commits_by: str = "date"  # "date" | "hash" | "message"
    reverse_commits: bool = True


RepoName = str
DateStr = str
GroupedCommits = Dict[DateStr, Dict[RepoName, List[Commit]]]


def group_by_date_and_repo(
    commits: List[Commit],
    config: GroupConfig | None = None,
) -> GroupedCommits:
    """Return commits nested as {date_str: {repo_name: [commits]}}."""
    if config is None:
        config = GroupConfig()

    grouped: GroupedCommits = {}

    for commit in commits:
        date_str = _date_key(commit.date)
        grouped.setdefault(date_str, {})
        grouped[date_str].setdefault(commit.repo, [])
        grouped[date_str][commit.repo].append(commit)

    # Sort commits within each repo bucket
    key_fn = _sort_key(config.sort_commits_by)
    for date_str, repos in grouped.items():
        repo_keys = sorted(repos.keys()) if config.sort_repos_alpha else list(repos.keys())
        sorted_repos: Dict[RepoName, List[Commit]] = {}
        for repo in repo_keys:
            sorted_repos[repo] = sorted(
                repos[repo], key=key_fn, reverse=config.reverse_commits
            )
        grouped[date_str] = sorted_repos

    return dict(sorted(grouped.items(), reverse=True))


def _date_key(dt: date) -> str:
    return dt.isoformat()


def _sort_key(sort_by: str):
    if sort_by == "hash":
        return lambda c: c.hash
    if sort_by == "message":
        return lambda c: c.message.lower()
    # default: date (datetime)
    return lambda c: c.date
