"""Tests for the git commit collector module."""

from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from git_standup.collector import Commit, CollectorConfig, collect_commits, _run_git_log


FAKE_GIT_OUTPUT = (
    "abc1234|||fix: correct off-by-one error|||2024-05-20T09:15:00+00:00\n"
    "def5678|||feat: add dark mode support|||2024-05-20T11:30:00+00:00\n"
)


@pytest.fixture()
def fake_repo(tmp_path: Path) -> Path:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    return tmp_path


def _make_completed_process(stdout: str = FAKE_GIT_OUTPUT):
    mock = MagicMock()
    mock.stdout = stdout
    return mock


@patch("git_standup.collector.subprocess.run")
def test_run_git_log_returns_commits(mock_run, fake_repo):
    mock_run.return_value = _make_completed_process()
    commits = _run_git_log(fake_repo, "alice", date(2024, 5, 20), date(2024, 5, 20))
    assert len(commits) == 2
    assert commits[0].hash == "abc1234"
    assert commits[0].message == "fix: correct off-by-one error"
    assert commits[0].repo == fake_repo.name


@patch("git_standup.collector.subprocess.run")
def test_run_git_log_empty_output(mock_run, fake_repo):
    mock_run.return_value = _make_completed_process(stdout="")
    commits = _run_git_log(fake_repo, "alice", date(2024, 5, 20), date(2024, 5, 20))
    assert commits == []


@patch("git_standup.collector.subprocess.run")
def test_run_git_log_whitespace_only_output(mock_run, fake_repo):
    """Lines that are blank or whitespace-only should be ignored."""
    mock_run.return_value = _make_completed_process(stdout="\n   \n\n")
    commits = _run_git_log(fake_repo, "alice", date(2024, 5, 20), date(2024, 5, 20))
    assert commits == []


@patch("git_standup.collector.subprocess.run")
def test_collect_commits_skips_non_git_dirs(mock_run, tmp_path):
    non_git = tmp_path / "not_a_repo"
    non_git.mkdir()
    config = CollectorConfig(
        repos=[non_git], author="alice", since=date(2024, 5, 20)
    )
    commits = collect_commits(config)
    mock_run.assert_not_called()
    assert commits == []


@patch("git_standup.collector.subprocess.run")
def test_collect_commits_sorted_by_timestamp(mock_run, fake_repo):
    mock_run.return_value = _make_completed_process()
    config = CollectorConfig(
        repos=[fake_repo], author="alice", since=date(2024, 5, 20)
    )
    commits = collect_commits(config)
    timestamps = [c.timestamp for c in commits]
    assert timestamps == sorted(timestamps)


def test_commit_dataclass_fields():
    c = Commit(
        repo="myrepo",
        hash="abc1234",
        message="chore: update deps",
        timestamp=datetime(2024, 5, 20, 10, 0, 0),
    )
    assert c.repo == "myrepo"
    assert c.hash == "abc1234"
