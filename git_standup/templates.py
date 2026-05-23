"""Built-in string templates for the markdown exporter."""

from __future__ import annotations

from string import Template
from typing import Dict

# Top-level document template
DOCUMENT_TMPL = Template(
    """# Git Standup Digest

$body
$stats_section"""
)

DATE_SECTION_TMPL = Template("## $date\n")

REPO_SECTION_TMPL = Template("### $repo\n")

COMMIT_LINE_TMPL = Template("- `$short_hash` $message")

STATS_SECTION_TMPL = Template("---\n\n## Stats\n\n$stats")


def render_document(body: str, stats: str = "") -> str:
    """Combine body and optional stats into a full markdown document."""
    stats_section = ""
    if stats:
        stats_section = STATS_SECTION_TMPL.substitute(stats=stats)
    return DOCUMENT_TMPL.substitute(body=body, stats_section=stats_section).strip()


def render_date_section(date: str, repo_blocks: Dict[str, str]) -> str:
    """Render a single date section containing one or more repo blocks."""
    parts = [DATE_SECTION_TMPL.substitute(date=date)]
    for repo, block in repo_blocks.items():
        parts.append(REPO_SECTION_TMPL.substitute(repo=repo))
        parts.append(block)
    return "\n".join(parts)


def render_commit_line(short_hash: str, message: str) -> str:
    """Render a single commit bullet line."""
    return COMMIT_LINE_TMPL.substitute(short_hash=short_hash, message=message)


def render_repo_block(commits) -> str:
    """Render all commit lines for a single repo."""
    lines = [render_commit_line(c.hash[:7], c.message) for c in commits]
    return "\n".join(lines) + "\n"
