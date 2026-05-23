"""Tests for git_standup/exporter.py"""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from git_standup.exporter import (
    ExportConfig,
    export_digest,
    export_as_json,
    export_as_markdown,
    export_as_text,
)


def _commit(hash_="abc1234ff", message="fix: something", author="Alice"):
    return SimpleNamespace(hash=hash_, message=message, author=author)


@pytest.fixture()
def grouped():
    return {
        "2024-05-01": {
            "repo-a": [_commit("aaa0001", "feat: add thing")],
            "repo-b": [_commit("bbb0002", "fix: broken pipe")],
        }
    }


def test_markdown_contains_date_header(grouped):
    cfg = ExportConfig(format="markdown", include_stats=False)
    result = export_as_markdown(grouped, "", cfg)
    assert "## 2024-05-01" in result


def test_markdown_contains_repo_header(grouped):
    cfg = ExportConfig(format="markdown", include_stats=False)
    result = export_as_markdown(grouped, "", cfg)
    assert "### repo-a" in result


def test_markdown_includes_stats_when_enabled(grouped):
    cfg = ExportConfig(format="markdown", include_stats=True)
    result = export_as_markdown(grouped, "total commits: 2", cfg)
    assert "total commits: 2" in result


def test_markdown_omits_stats_when_disabled(grouped):
    cfg = ExportConfig(format="markdown", include_stats=False)
    result = export_as_markdown(grouped, "total commits: 2", cfg)
    assert "total commits: 2" not in result


def test_text_format_uses_equals_header(grouped):
    cfg = ExportConfig(format="text", include_stats=False)
    result = export_as_text(grouped, "", cfg)
    assert "=== 2024-05-01 ===" in result


def test_json_format_is_valid_json(grouped):
    cfg = ExportConfig(format="json", include_stats=False)
    result = export_as_json(grouped, "", cfg)
    parsed = json.loads(result)
    assert "digest" in parsed
    assert "2024-05-01" in parsed["digest"]


def test_json_includes_commit_fields(grouped):
    cfg = ExportConfig(format="json", include_stats=False)
    result = export_as_json(grouped, "", cfg)
    parsed = json.loads(result)
    commit = parsed["digest"]["2024-05-01"]["repo-a"][0]
    assert commit["hash"] == "aaa0001"
    assert commit["message"] == "feat: add thing"


def test_export_digest_writes_file(tmp_path, grouped):
    out = tmp_path / "output" / "digest.md"
    cfg = ExportConfig(format="markdown", output_path=out, include_stats=False)
    export_digest(grouped, "", cfg)
    assert out.exists()
    assert "## 2024-05-01" in out.read_text()


def test_export_digest_raises_on_unknown_format(grouped):
    cfg = ExportConfig(format="csv")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Unknown export format"):
        export_digest(grouped, "", cfg)


def test_export_digest_returns_string(grouped):
    cfg = ExportConfig(format="text", include_stats=False)
    result = export_digest(grouped, "", cfg)
    assert isinstance(result, str)
