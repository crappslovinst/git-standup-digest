"""Tests for git_standup/templates.py"""

from __future__ import annotations

from types import SimpleNamespace

from git_standup.templates import (
    render_commit_line,
    render_date_section,
    render_document,
    render_repo_block,
)


def _commit(hash_="abc1234ff", message="chore: tidy up"):
    return SimpleNamespace(hash=hash_, message=message)


def test_render_commit_line_format():
    line = render_commit_line("abc1234", "fix: oops")
    assert line == "- `abc1234` fix: oops"


def test_render_repo_block_multiple_commits():
    commits = [_commit("aaa0001", "feat: a"), _commit("bbb0002", "feat: b")]
    block = render_repo_block(commits)
    assert "- `aaa0001` feat: a" in block
    assert "- `bbb0002` feat: b" in block


def test_render_repo_block_truncates_hash():
    commit = _commit("abc1234xyz", "fix: hash")
    block = render_repo_block([commit])
    assert "abc1234" in block
    assert "xyz" not in block


def test_render_date_section_contains_date():
    section = render_date_section("2024-05-01", {"my-repo": "- `abc1234` msg\n"})
    assert "## 2024-05-01" in section


def test_render_date_section_contains_repo_header():
    section = render_date_section("2024-05-01", {"my-repo": "- `abc1234` msg\n"})
    assert "### my-repo" in section


def test_render_date_section_contains_commit_block():
    section = render_date_section("2024-05-01", {"my-repo": "- `abc1234` msg\n"})
    assert "- `abc1234` msg" in section


def test_render_document_no_stats():
    doc = render_document("some body")
    assert "some body" in doc
    assert "Stats" not in doc


def test_render_document_with_stats():
    doc = render_document("some body", stats="total commits: 5")
    assert "## Stats" in doc
    assert "total commits: 5" in doc


def test_render_document_strips_trailing_whitespace():
    doc = render_document("body")
    assert doc == doc.strip()
