"""Tests for the CLI argument parsing and main() entry point."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from git_standup.cli import _build_parser, main


@pytest.fixture()
def parser():
    return _build_parser()


def test_defaults(parser):
    args = parser.parse_args([])
    assert args.repos == [Path(".")]
    assert args.author is None
    assert args.days == 1
    assert args.since is None
    assert args.show_hash is True
    assert args.output is None
    assert args.clipboard is False


def test_repos_positional(parser):
    args = parser.parse_args(["repo1", "repo2"])
    assert args.repos == [Path("repo1"), Path("repo2")]


def test_author_flag(parser):
    args = parser.parse_args(["--author", "Alice"])
    assert args.author == "Alice"


def test_days_flag(parser):
    args = parser.parse_args(["--days", "7"])
    assert args.days == 7


def test_since_flag(parser):
    args = parser.parse_args(["--since", "2024-01-01"])
    assert args.since == "2024-01-01"


def test_no_hash_flag(parser):
    args = parser.parse_args(["--no-hash"])
    assert args.show_hash is False


def test_output_flag(parser):
    args = parser.parse_args(["--output", "out.md"])
    assert args.output == Path("out.md")


def test_clipboard_flag(parser):
    args = parser.parse_args(["--clipboard"])
    assert args.clipboard is True


@patch("git_standup.cli.run_pipeline")
def test_main_calls_run_pipeline(mock_run: MagicMock):
    result = main(["--days", "3", "--no-hash"])
    assert result == 0
    mock_run.assert_called_once()
    config = mock_run.call_args[0][0]
    assert config.show_hash is False


@patch("git_standup.cli.run_pipeline")
def test_main_since_overrides_days(mock_run: MagicMock):
    main(["--since", "2024-06-01", "--days", "99"])
    config = mock_run.call_args[0][0]
    assert config.since == "2024-06-01"


@patch("git_standup.cli.run_pipeline")
def test_main_days_computes_since(mock_run: MagicMock):
    from datetime import date, timedelta

    main(["--days", "2"])
    config = mock_run.call_args[0][0]
    expected = (date.today() - timedelta(days=2)).isoformat()
    assert config.since == expected
