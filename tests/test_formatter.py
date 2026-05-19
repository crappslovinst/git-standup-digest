"""Tests for git_standup.formatter."""

from datetime import date, datetime

import pytest

from git_standup.collector import Commit
from git_standup.formatter import FormatConfig, format_digest


def _make_commit(repo="myrepo", message="fix bug", short_hash="abc1234") -> Commit:
    return Commit(
        repo=repo,
        short_hash=short_hash,
        message=message,
        author="Dev",
        timestamp=datetime(2024, 5, 14, 10, 30),
    )


def test_format_digest_empty_returns_message():
    result = format_digest([])
    assert result == "No commits found."


def test_format_digest_includes_date_header():
    commits = [_make_commit()]
    result = format_digest(commits, for_date=date(2024, 5, 14))
    assert "Tuesday, May 14 2024" in result


def test_format_digest_groups_by_repo():
    commits = [
        _make_commit(repo="api", message="add endpoint"),
        _make_commit(repo="api", message="fix auth"),
        _make_commit(repo="frontend", message="update styles"),
    ]
    result = format_digest(commits)
    assert "api/" in result
    assert "frontend/" in result
    api_idx = result.index("api/")
    frontend_idx = result.index("frontend/")
    assert api_idx < frontend_idx


def test_format_digest_shows_hash_by_default():
    commits = [_make_commit(short_hash="deadbee")]
    result = format_digest(commits)
    assert "[deadbee]" in result


def test_format_digest_hides_hash_when_configured():
    config = FormatConfig(show_hash=False)
    commits = [_make_commit(short_hash="deadbee")]
    result = format_digest(commits, config=config)
    assert "[deadbee]" not in result


def test_format_digest_shows_time_when_configured():
    config = FormatConfig(show_time=True)
    commits = [_make_commit()]
    result = format_digest(commits, config=config)
    assert "(10:30)" in result


def test_format_digest_flat_mode_includes_repo_prefix():
    config = FormatConfig(group_by_repo=False, show_repo=True)
    commits = [_make_commit(repo="backend", message="migrate db")]
    result = format_digest(commits, config=config)
    assert "backend:" in result
    assert "migrate db" in result


def test_format_digest_no_date_header():
    config = FormatConfig(date_header=False)
    commits = [_make_commit()]
    result = format_digest(commits, config=config)
    assert "Standup Digest" not in result
