"""Export digest output to different file formats (markdown, plain text, JSON)."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional

ExportFormat = Literal["markdown", "text", "json"]


@dataclass
class ExportConfig:
    format: ExportFormat = "markdown"
    output_path: Optional[Path] = None
    include_stats: bool = True


def export_as_markdown(grouped: Dict, stats_text: str, config: ExportConfig) -> str:
    """Render grouped commits as a Markdown document."""
    lines: List[str] = ["# Git Standup Digest\n"]
    for date, repos in grouped.items():
        lines.append(f"## {date}\n")
        for repo, commits in repos.items():
            lines.append(f"### {repo}\n")
            for commit in commits:
                lines.append(f"- `{commit.hash[:7]}` {commit.message}")
            lines.append("")
    if config.include_stats and stats_text:
        lines.append("---\n")
        lines.append("## Stats\n")
        lines.append(stats_text)
    return "\n".join(lines)


def export_as_text(grouped: Dict, stats_text: str, config: ExportConfig) -> str:
    """Render grouped commits as plain text."""
    lines: List[str] = []
    for date, repos in grouped.items():
        lines.append(f"=== {date} ===")
        for repo, commits in repos.items():
            lines.append(f"  [{repo}]")
            for commit in commits:
                lines.append(f"    {commit.hash[:7]} {commit.message}")
        lines.append("")
    if config.include_stats and stats_text:
        lines.append("--- Stats ---")
        lines.append(stats_text)
    return "\n".join(lines)


def export_as_json(grouped: Dict, stats_text: str, config: ExportConfig) -> str:
    """Render grouped commits as JSON."""
    data: Dict = {}
    for date, repos in grouped.items():
        data[date] = {}
        for repo, commits in repos.items():
            data[date][repo] = [
                {"hash": c.hash, "message": c.message, "author": c.author}
                for c in commits
            ]
    payload = {"digest": data}
    if config.include_stats and stats_text:
        payload["stats"] = stats_text
    return json.dumps(payload, indent=2)


_EXPORTERS = {
    "markdown": export_as_markdown,
    "text": export_as_text,
    "json": export_as_json,
}


def export_digest(grouped: Dict, stats_text: str, config: ExportConfig) -> str:
    """Dispatch to the correct exporter and optionally write to a file."""
    exporter = _EXPORTERS.get(config.format)
    if exporter is None:
        raise ValueError(f"Unknown export format: {config.format!r}")
    result = exporter(grouped, stats_text, config)
    if config.output_path is not None:
        config.output_path.parent.mkdir(parents=True, exist_ok=True)
        config.output_path.write_text(result, encoding="utf-8")
    return result
