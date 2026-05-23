"""Lifecycle hooks for the pipeline — lets callers inject callbacks at key stages."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from git_standup.collector import Commit


OnCommitsCollected = Callable[[List[Commit]], None]
OnCommitsFiltered = Callable[[List[Commit]], None]
OnDigestReady = Callable[[str], None]
OnError = Callable[[Exception], None]


@dataclass
class HookConfig:
    """Optional callbacks invoked at pipeline lifecycle points."""

    on_commits_collected: Optional[OnCommitsCollected] = None
    on_commits_filtered: Optional[OnCommitsFiltered] = None
    on_digest_ready: Optional[OnDigestReady] = None
    on_error: Optional[OnError] = None


def fire(hook: Optional[Callable], *args) -> None:
    """Safely invoke a hook if it is set; swallow exceptions so hooks never crash the pipeline."""
    if hook is None:
        return
    try:
        hook(*args)
    except Exception:  # noqa: BLE001
        pass


def logging_hook_config(logger) -> HookConfig:
    """Return a HookConfig that logs each lifecycle event via *logger*."""

    def _collected(commits: List[Commit]) -> None:
        logger.debug("collected %d commits", len(commits))

    def _filtered(commits: List[Commit]) -> None:
        logger.debug("after filtering: %d commits", len(commits))

    def _ready(digest: str) -> None:
        logger.debug("digest ready (%d chars)", len(digest))

    def _error(exc: Exception) -> None:
        logger.error("pipeline error: %s", exc)

    return HookConfig(
        on_commits_collected=_collected,
        on_commits_filtered=_filtered,
        on_digest_ready=_ready,
        on_error=_error,
    )
