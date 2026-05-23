"""Tests for git_standup.stats."""
from datetime import datetime

from git_standup.collector import Commit
from git_standup.grouper import group_by_date_and_repo
from git_standup.stats import DigestStats, compute_stats, format_stats


def _commit(repo="repo-a", hash="abc", dt=datetime(2024, 5, 1, 10, 0)):
    return Commit(repo=repo, hash=hash, message="msg", author="dev", date=dt)


def test_empty_grouped_returns_zero_stats():
    stats = compute_stats({})
    assert stats.total_commits == 0
    assert stats.unique_repos == 0
    assert stats.unique_dates == 0
    assert stats.busiest_date is None
    assert stats.busiest_repo is None


def test_single_commit_stats():
    grouped = group_by_date_and_repo([_commit()])
    stats = compute_stats(grouped)
    assert stats.total_commits == 1
    assert stats.unique_repos == 1
    assert stats.unique_dates == 1
    assert stats.busiest_date == "2024-05-01"
    assert stats.busiest_repo == "repo-a"


def test_commits_per_repo_counted_across_dates():
    commits = [
        _commit(repo="repo-a", hash="a1", dt=datetime(2024, 5, 1, 9, 0)),
        _commit(repo="repo-a", hash="a2", dt=datetime(2024, 5, 2, 9, 0)),
        _commit(repo="repo-b", hash="b1", dt=datetime(2024, 5, 1, 10, 0)),
    ]
    grouped = group_by_date_and_repo(commits)
    stats = compute_stats(grouped)
    assert stats.commits_per_repo["repo-a"] == 2
    assert stats.commits_per_repo["repo-b"] == 1
    assert stats.total_commits == 3


def test_busiest_date_chosen_correctly():
    commits = [
        _commit(hash="a1", dt=datetime(2024, 5, 1, 9, 0)),
        _commit(hash="a2", dt=datetime(2024, 5, 2, 9, 0)),
        _commit(hash="a3", dt=datetime(2024, 5, 2, 10, 0)),
    ]
    grouped = group_by_date_and_repo(commits)
    stats = compute_stats(grouped)
    assert stats.busiest_date == "2024-05-02"


def test_format_stats_contains_key_info():
    commits = [
        _commit(repo="repo-a", hash="x1"),
        _commit(repo="repo-b", hash="x2"),
    ]
    grouped = group_by_date_and_repo(commits)
    stats = compute_stats(grouped)
    output = format_stats(stats)
    assert "Total commits" in output
    assert "2" in output
    assert "repo-" in output


def test_format_stats_no_busiest_when_empty():
    output = format_stats(compute_stats({}))
    assert "Busiest" not in output
