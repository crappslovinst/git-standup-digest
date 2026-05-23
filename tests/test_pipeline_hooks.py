"""Integration-style tests verifying hooks fire correctly inside run_pipeline."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from git_standup.collector import Commit
from git_standup.hooks import HookConfig
from git_standup.pipeline import PipelineConfig, run_pipeline


def _fake_commit(repo: str = "repo-a") -> Commit:
    return Commit(
        hash="deadbeef",
        author="Bob",
        date=datetime(2024, 3, 1, 10, 0),
        message="chore: update deps",
        repo=repo,
    )


@pytest.fixture()
def patched_pipeline(tmp_path):
    """Patch heavy I/O so pipeline runs without real git repos."""
    commits = [_fake_commit()]
    with (
        patch("git_standup.pipeline.collect_commits", return_value=commits) as mock_collect,
        patch("git_standup.pipeline.render") as mock_render,
    ):
        yield mock_collect, mock_render, commits, tmp_path


def _cfg(hooks: HookConfig, tmp_path: Path) -> PipelineConfig:
    return PipelineConfig(repos=[tmp_path], hooks=hooks)


def test_on_commits_collected_fires(patched_pipeline):
    _, _, commits, tmp_path = patched_pipeline
    cb = MagicMock()
    run_pipeline(_cfg(HookConfig(on_commits_collected=cb), tmp_path))
    cb.assert_called_once_with(commits)


def test_on_commits_filtered_fires(patched_pipeline):
    _, _, _, tmp_path = patched_pipeline
    cb = MagicMock()
    run_pipeline(_cfg(HookConfig(on_commits_filtered=cb), tmp_path))
    cb.assert_called_once()


def test_on_digest_ready_fires(patched_pipeline):
    _, _, _, tmp_path = patched_pipeline
    cb = MagicMock()
    run_pipeline(_cfg(HookConfig(on_digest_ready=cb), tmp_path))
    cb.assert_called_once()
    digest_arg = cb.call_args[0][0]
    assert isinstance(digest_arg, str)


def test_on_error_fires_and_exception_reraised(tmp_path):
    cb = MagicMock()
    cfg = PipelineConfig(repos=[tmp_path], hooks=HookConfig(on_error=cb))
    with (
        patch("git_standup.pipeline.collect_commits", side_effect=RuntimeError("git gone")),
        pytest.raises(RuntimeError, match="git gone"),
    ):
        run_pipeline(cfg)
    cb.assert_called_once()
    assert isinstance(cb.call_args[0][0], RuntimeError)


def test_pipeline_returns_digest_string(patched_pipeline):
    _, _, _, tmp_path = patched_pipeline
    result = run_pipeline(_cfg(HookConfig(), tmp_path))
    assert isinstance(result, str)


def test_no_hooks_pipeline_still_works(patched_pipeline):
    """Ensure pipeline works fine when no hooks are provided."""
    _, _, _, tmp_path = patched_pipeline
    cfg = PipelineConfig(repos=[tmp_path])
    result = run_pipeline(cfg)
    assert isinstance(result, str)
