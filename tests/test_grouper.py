"""Tests for git_standup.grouper."""
from datetime import date, datetime

import pytest

from git_standup.collector import Commit
from git_standup.grouper import GroupConfig, group_by_date_and_repo


def _commit(
    repo: str = "my-repo",
    message: str = "fix thing",
    hash: str = "abc1234",
    dt: datetime = datetime(2024, 5, 1, 10, 0, 0),
) -> Commit:
    return Commit(repo=repo, hash=hash, message=message, author="dev", date=dt)


def test_empty_returns_empty():
    assert group_by_date_and_repo([]) == {}


def test_single_commit_grouped_correctly():
    c = _commit()
    result = group_by_date_and_repo([c])
    assert "2024-05-01" in result
    assert "my-repo" in result["2024-05-01"]
    assert result["2024-05-01"]["my-repo"] == [c]


def test_multiple_dates_sorted_descending():
    c1 = _commit(dt=datetime(2024, 5, 1, 9, 0))
    c2 = _commit(dt=datetime(2024, 5, 2, 9, 0))
    result = group_by_date_and_repo([c1, c2])
    keys = list(result.keys())
    assert keys == ["2024-05-02", "2024-05-01"]


def test_repos_sorted_alphabetically():
    c1 = _commit(repo="zebra")
    c2 = _commit(repo="alpha")
    result = group_by_date_and_repo([c1, c2])
    repos = list(result["2024-05-01"].keys())
    assert repos == ["alpha", "zebra"]


def test_repos_not_sorted_when_disabled():
    c1 = _commit(repo="zebra")
    c2 = _commit(repo="alpha")
    cfg = GroupConfig(sort_repos_alpha=False)
    result = group_by_date_and_repo([c1, c2], config=cfg)
    # insertion order preserved
    repos = list(result["2024-05-01"].keys())
    assert set(repos) == {"zebra", "alpha"}


def test_commits_sorted_by_date_descending_default():
    c1 = _commit(hash="aaa", dt=datetime(2024, 5, 1, 8, 0))
    c2 = _commit(hash="bbb", dt=datetime(2024, 5, 1, 12, 0))
    result = group_by_date_and_repo([c1, c2])
    commits = result["2024-05-01"]["my-repo"]
    assert commits[0].hash == "bbb"


def test_sort_by_message():
    c1 = _commit(hash="aaa", message="zebra fix")
    c2 = _commit(hash="bbb", message="alpha fix")
    cfg = GroupConfig(sort_commits_by="message", reverse_commits=False)
    result = group_by_date_and_repo([c1, c2], config=cfg)
    commits = result["2024-05-01"]["my-repo"]
    assert commits[0].hash == "bbb"  # alpha comes first


def test_sort_by_hash():
    c1 = _commit(hash="ccc")
    c2 = _commit(hash="aaa")
    cfg = GroupConfig(sort_commits_by="hash", reverse_commits=False)
    result = group_by_date_and_repo([c1, c2], config=cfg)
    commits = result["2024-05-01"]["my-repo"]
    assert commits[0].hash == "aaa"
