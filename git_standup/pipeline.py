"""High-level pipeline: collect → format → render."""

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from git_standup.collector import CollectorConfig, collect_commits
from git_standup.formatter import FormatConfig, format_digest
from git_standup.renderer import render


@dataclass
class PipelineConfig:
    """Top-level configuration combining all stages."""

    # Collection
    repo_paths: list[Path] = field(default_factory=list)
    author: Optional[str] = None
    since: str = "yesterday"
    until: str = "now"

    # Formatting
    show_repo: bool = True
    show_hash: bool = True
    show_time: bool = False
    group_by_repo: bool = True
    date_header: bool = True

    # Rendering
    stdout: bool = True
    output_file: Optional[Path] = None
    append_to_file: bool = False
    clipboard: bool = False


def run_pipeline(config: PipelineConfig) -> str:
    """Execute the full collect → format → render pipeline.

    Returns the formatted digest string regardless of render targets.
    """
    collector_cfg = CollectorConfig(
        author=config.author,
        since=config.since,
        until=config.until,
    )

    commits = collect_commits(config.repo_paths, collector_cfg)

    format_cfg = FormatConfig(
        show_repo=config.show_repo,
        show_hash=config.show_hash,
        show_time=config.show_time,
        group_by_repo=config.group_by_repo,
        date_header=config.date_header,
    )

    for_date: Optional[date] = None
    if config.since == "yesterday":
        for_date = date.today() - timedelta(days=1)
    elif config.since == "today" or config.since == "midnight":
        for_date = date.today()

    digest = format_digest(commits, config=format_cfg, for_date=for_date)

    render(
        digest,
        stdout=config.stdout,
        file_path=config.output_file,
        append=config.append_to_file,
        clipboard=config.clipboard,
    )

    return digest
