"""Tests for git_standup.filters."""

from datetime import date

import pytest

from git_standup.collector import Commit
from git_standup.filters import (
    FilterConfig,
    _is_merge_commit,
    _matches_any,
    filter_commits,
    last_n_days,
)


def _commit(message="fix bug", author="Alice", repo="my-repo", days_ago=0):
    return Commit(
        hash="abc1234",
        author=author,
        date=date.today()
        if days_ago == 0
        else date.fromordinal(date.today().toordinal() - days_ago),
        message=message,
        repo=repo,
    )


def test_no_filters_returns_all():
    commits = [_commit(), _commit(message="add feature")]
    assert filter_commits(commits, FilterConfig()) == commits


def test_exclude_merges_default():
    commits = [_commit("Merge branch 'main'"), _commit("fix bug")]
    result = filter_commits(commits, FilterConfig())
    assert len(result) == 1
    assert result[0].message == "fix bug"


def test_exclude_merges_disabled():
    commits = [_commit("Merge branch 'main'"), _commit("fix bug")]
    result = filter_commits(commits, FilterConfig(exclude_merges=False))
    assert len(result) == 2


def test_filter_by_author():
    commits = [_commit(author="Alice"), _commit(author="Bob")]
    result = filter_commits(commits, FilterConfig(authors=["alice"]))
    assert all(c.author == "Alice" for c in result)


def test_filter_by_repo():
    commits = [_commit(repo="api"), _commit(repo="frontend")]
    result = filter_commits(commits, FilterConfig(repos=["api"]))
    assert all(c.repo == "api" for c in result)


def test_filter_since():
    old = _commit(days_ago=5)
    new = _commit(days_ago=0)
    cfg = FilterConfig(since=date.today())
    assert filter_commits([old, new], cfg) == [new]


def test_filter_until():
    old = _commit(days_ago=3)
    new = _commit(days_ago=0)
    cfg = FilterConfig(until=date.fromordinal(date.today().toordinal() - 1))
    assert filter_commits([old, new], cfg) == [old]


def test_min_message_length():
    commits = [_commit(message="ok"), _commit(message="detailed fix for issue")]
    result = filter_commits(commits, FilterConfig(min_message_length=5))
    assert len(result) == 1
    assert "detailed" in result[0].message


def test_matches_any_case_insensitive():
    assert _matches_any("Alice Smith", ["alice"]) is True
    assert _matches_any("Bob", ["alice"]) is False


def test_is_merge_commit():
    assert _is_merge_commit("Merge branch 'dev' into main") is True
    assert _is_merge_commit("fix: correct typo") is False


def test_last_n_days_range():
    cfg = last_n_days(7)
    assert cfg.until == date.today()
    assert (cfg.until - cfg.since).days == 6
