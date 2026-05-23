"""Tests for git_standup.hooks."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List
from unittest.mock import MagicMock

import pytest

from git_standup.collector import Commit
from git_standup.hooks import HookConfig, fire, logging_hook_config


def _commit(msg: str = "fix: thing") -> Commit:
    return Commit(
        hash="abc1234",
        author="Alice",
        date=datetime(2024, 1, 15, 9, 0),
        message=msg,
        repo="my-repo",
    )


# ---------------------------------------------------------------------------
# fire()
# ---------------------------------------------------------------------------

def test_fire_calls_hook():
    called_with = []
    fire(lambda x: called_with.append(x), 42)
    assert called_with == [42]


def test_fire_none_hook_is_noop():
    fire(None, "anything")  # should not raise


def test_fire_swallows_hook_exceptions():
    def bad_hook(x):
        raise RuntimeError("boom")

    fire(bad_hook, "value")  # should not raise


def test_fire_passes_multiple_args():
    received = []
    fire(lambda a, b: received.extend([a, b]), "x", "y")
    assert received == ["x", "y"]


# ---------------------------------------------------------------------------
# HookConfig defaults
# ---------------------------------------------------------------------------

def test_hook_config_defaults_are_none():
    cfg = HookConfig()
    assert cfg.on_commits_collected is None
    assert cfg.on_commits_filtered is None
    assert cfg.on_digest_ready is None
    assert cfg.on_error is None


def test_hook_config_accepts_callables():
    cb = MagicMock()
    cfg = HookConfig(on_commits_collected=cb)
    commits = [_commit()]
    fire(cfg.on_commits_collected, commits)
    cb.assert_called_once_with(commits)


# ---------------------------------------------------------------------------
# logging_hook_config()
# ---------------------------------------------------------------------------

def test_logging_hook_config_returns_hook_config():
    logger = logging.getLogger("test")
    cfg = logging_hook_config(logger)
    assert isinstance(cfg, HookConfig)


def test_logging_hooks_do_not_raise(caplog):
    logger = logging.getLogger("test.hooks")
    cfg = logging_hook_config(logger)
    commits = [_commit()]
    with caplog.at_level(logging.DEBUG, logger="test.hooks"):
        fire(cfg.on_commits_collected, commits)
        fire(cfg.on_commits_filtered, commits)
        fire(cfg.on_digest_ready, "some digest text")
        fire(cfg.on_error, ValueError("oops"))
    # just ensure nothing raised; log output is a bonus


def test_logging_collected_logs_count(caplog):
    logger = logging.getLogger("test.hooks.count")
    cfg = logging_hook_config(logger)
    commits = [_commit(), _commit("feat: other")]
    with caplog.at_level(logging.DEBUG, logger="test.hooks.count"):
        fire(cfg.on_commits_collected, commits)
    assert any("2" in r.message for r in caplog.records)
