"""Tests for git_standup.summarizer."""
from __future__ import annotations

import pytest
from datetime import date
from collections import defaultdict

from git_standup.collector import Commit
from git_standup.stats import DigestStats
from git_standup.summarizer import SummaryConfig, build_summary, _pluralise, _top_repos


def _stats(
    total_commits=0,
    total_repos=0,
    total_days=0,
    commits_per_repo=None,
    busiest_date=None,
) -> DigestStats:
    return DigestStats(
        total_commits=total_commits,
        total_repos=total_repos,
        total_days=total_days,
        commits_per_repo=commits_per_repo or {},
        busiest_date=busiest_date,
    )


def test_empty_stats_returns_nudge():
    result = build_summary({}, _stats())
    assert "Nothing committed" in result


def test_summary_includes_greeting():
    cfg = SummaryConfig(greeting="Yo, listen up:")
    stats = _stats(total_commits=1, total_repos=1, total_days=1, commits_per_repo={"repo": 1})
    result = build_summary({}, stats, cfg)
    assert "Yo, listen up:" in result


def test_summary_shows_commit_count():
    stats = _stats(total_commits=5, total_repos=2, total_days=3, commits_per_repo={"a": 3, "b": 2})
    result = build_summary({}, stats)
    assert "5 commits" in result


def test_summary_singular_commit():
    stats = _stats(total_commits=1, total_repos=1, total_days=1, commits_per_repo={"a": 1})
    result = build_summary({}, stats)
    assert "1 commit" in result
    assert "1 commits" not in result


def test_summary_includes_top_repos():
    stats = _stats(
        total_commits=6, total_repos=2, total_days=1,
        commits_per_repo={"alpha": 4, "beta": 2},
    )
    result = build_summary({}, stats)
    assert "alpha" in result
    assert "beta" in result


def test_summary_limits_highlights():
    cfg = SummaryConfig(max_highlights=1)
    stats = _stats(
        total_commits=9, total_repos=3, total_days=1,
        commits_per_repo={"a": 5, "b": 3, "c": 1},
    )
    result = build_summary({}, stats, cfg)
    assert "a" in result
    assert "b" not in result


def test_busiest_date_shown():
    stats = _stats(
        total_commits=3, total_repos=1, total_days=2,
        commits_per_repo={"x": 3},
        busiest_date="2024-06-10",
    )
    result = build_summary({}, stats)
    assert "2024-06-10" in result


def test_no_repo_breakdown_when_disabled():
    cfg = SummaryConfig(include_repo_breakdown=False)
    stats = _stats(
        total_commits=2, total_repos=1, total_days=1,
        commits_per_repo={"myrepo": 2},
    )
    result = build_summary({}, stats, cfg)
    assert "myrepo" not in result


def test_pluralise_singular():
    assert _pluralise(1, "cat") == "1 cat"


def test_pluralise_plural():
    assert _pluralise(3, "cat") == "3 cats"


def test_pluralise_custom_plural():
    assert _pluralise(2, "ox", "oxen") == "2 oxen"
