"""Orchestrates collect → filter → group → export pipeline."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from git_standup.collector import CollectorConfig, collect_commits
from git_standup.filters import FilterConfig, filter_commits
from git_standup.grouper import GroupConfig, group_by_date_and_repo
from git_standup.exporter import ExportConfig, export_digest
from git_standup.renderer import render
from git_standup.hooks import HookConfig, fire
from git_standup.summarizer import SummaryConfig, build_summary
from git_standup.stats import compute_stats


@dataclass
class PipelineConfig:
    repos: List[Path]
    author: Optional[str] = None
    days: int = 1
    show_hash: bool = True
    no_merges: bool = True
    output_file: Optional[Path] = None
    output_format: str = "text"
    append: bool = False
    to_clipboard: bool = False
    show_summary: bool = False
    summary_cfg: SummaryConfig = field(default_factory=SummaryConfig)
    hook_cfg: HookConfig = field(default_factory=HookConfig)


def run_pipeline(cfg: PipelineConfig) -> str:
    collector_cfg = CollectorConfig(
        repos=cfg.repos,
        author=cfg.author,
        days=cfg.days,
    )
    commits = collect_commits(collector_cfg)
    fire(cfg.hook_cfg.on_commits_collected, commits)

    filter_cfg = FilterConfig(
        exclude_merges=cfg.no_merges,
        author=cfg.author,
        days=cfg.days,
    )
    commits = filter_commits(commits, filter_cfg)
    fire(cfg.hook_cfg.on_commits_filtered, commits)

    group_cfg = GroupConfig()
    grouped = group_by_date_and_repo(commits, group_cfg)
    fire(cfg.hook_cfg.on_commits_grouped, grouped)

    export_cfg = ExportConfig(
        fmt=cfg.output_format,
        show_hash=cfg.show_hash,
    )
    digest = export_digest(grouped, export_cfg)

    if cfg.show_summary:
        stats = compute_stats(grouped)
        summary = build_summary(grouped, stats, cfg.summary_cfg)
        digest = summary + "\n\n" + digest

    render(
        digest,
        output_file=cfg.output_file,
        append=cfg.append,
        to_clipboard=cfg.to_clipboard,
    )
    return digest
