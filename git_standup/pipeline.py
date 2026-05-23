"""High-level pipeline that wires collector → filter → group → format → render."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from git_standup.cache import CacheConfig, load_cached, save_cached
from git_standup.collector import CollectorConfig, collect_commits
from git_standup.filters import FilterConfig, filter_commits
from git_standup.formatter import FormatConfig, format_digest
from git_standup.grouper import GroupConfig, group_by_date_and_repo
from git_standup.hooks import HookConfig, fire
from git_standup.renderer import render


@dataclass
class PipelineConfig:
    repos: List[Path]
    collector: CollectorConfig = field(default_factory=CollectorConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    group: GroupConfig = field(default_factory=GroupConfig)
    format: FormatConfig = field(default_factory=FormatConfig)
    cache: Optional[CacheConfig] = None
    hooks: HookConfig = field(default_factory=HookConfig)
    output: Optional[Path] = None
    append: bool = False
    to_clipboard: bool = False


def run_pipeline(cfg: PipelineConfig) -> str:
    """Execute the full standup pipeline and return the rendered digest string."""
    try:
        # --- collect ---
        commits = collect_commits(cfg.repos, cfg.collector)
        fire(cfg.hooks.on_commits_collected, commits)

        # --- cache round-trip (optional) ---
        if cfg.cache is not None:
            cached = load_cached(cfg.cache, commits)
            if cached is not None:
                fire(cfg.hooks.on_digest_ready, cached)
                return cached

        # --- filter ---
        commits = filter_commits(commits, cfg.filters)
        fire(cfg.hooks.on_commits_filtered, commits)

        # --- group → format ---
        grouped = group_by_date_and_repo(commits, cfg.group)
        digest = format_digest(grouped, cfg.format)

        # --- cache save ---
        if cfg.cache is not None:
            save_cached(cfg.cache, commits, digest)

        # --- render ---
        render(
            digest,
            output=cfg.output,
            append=cfg.append,
            to_clipboard=cfg.to_clipboard,
        )

        fire(cfg.hooks.on_digest_ready, digest)
        return digest

    except Exception as exc:  # noqa: BLE001
        fire(cfg.hooks.on_error, exc)
        raise
