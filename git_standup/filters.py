"""Filtering utilities for commit collections."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

from git_standup.collector import Commit


@dataclass
class FilterConfig:
    """Configuration for filtering commits."""

    since: Optional[date] = None
    until: Optional[date] = None
    authors: List[str] = field(default_factory=list)
    repos: List[str] = field(default_factory=list)
    exclude_merges: bool = True
    min_message_length: int = 0


def filter_commits(commits: List[Commit], config: FilterConfig) -> List[Commit]:
    """Return only commits that pass all active filters."""
    result = []
    for commit in commits:
        if config.since and commit.date < config.since:
            continue
        if config.until and commit.date > config.until:
            continue
        if config.authors and not _matches_any(commit.author, config.authors):
            continue
        if config.repos and commit.repo not in config.repos:
            continue
        if config.exclude_merges and _is_merge_commit(commit.message):
            continue
        if len(commit.message.strip()) < config.min_message_length:
            continue
        result.append(commit)
    return result


def _matches_any(value: str, patterns: List[str]) -> bool:
    """Case-insensitive substring match against any pattern."""
    lower = value.lower()
    return any(p.lower() in lower for p in patterns)


def _is_merge_commit(message: str) -> bool:
    """Heuristic: treat messages starting with 'Merge' as merge commits."""
    return message.strip().lower().startswith("merge")


def last_n_days(n: int) -> FilterConfig:
    """Convenience factory: filter to the last *n* days (inclusive)."""
    today = date.today()
    return FilterConfig(since=today - timedelta(days=n - 1), until=today)
