"""Tests for git_standup.renderer."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from git_standup.renderer import render, render_to_file, render_to_stdout

DIGEST = "=== Standup ===\n  [abc1234] fix bug\n"


def test_render_to_stdout_writes(capsys):
    render_to_stdout(DIGEST)
    captured = capsys.readouterr()
    assert captured.out == DIGEST


def test_render_to_file_creates_file(tmp_path):
    dest = tmp_path / "digest.txt"
    render_to_file(DIGEST, dest)
    assert dest.read_text(encoding="utf-8") == DIGEST


def test_render_to_file_overwrites_by_default(tmp_path):
    dest = tmp_path / "digest.txt"
    dest.write_text("old content", encoding="utf-8")
    render_to_file(DIGEST, dest)
    assert dest.read_text(encoding="utf-8") == DIGEST


def test_render_to_file_append(tmp_path):
    dest = tmp_path / "digest.txt"
    dest.write_text("previous\n", encoding="utf-8")
    render_to_file(DIGEST, dest, append=True)
    content = dest.read_text(encoding="utf-8")
    assert content.startswith("previous\n")
    assert DIGEST in content


def test_render_to_file_creates_parent_dirs(tmp_path):
    dest = tmp_path / "nested" / "dir" / "digest.txt"
    render_to_file(DIGEST, dest)
    assert dest.exists()


def test_render_dispatches_to_stdout(capsys):
    render(DIGEST, stdout=True)
    assert capsys.readouterr().out == DIGEST


def test_render_dispatches_to_file(tmp_path, capsys):
    dest = tmp_path / "out.txt"
    render(DIGEST, stdout=False, file_path=dest)
    assert dest.read_text() == DIGEST
    assert capsys.readouterr().out == ""


def test_render_clipboard_failure_writes_warning(capsys):
    with patch("git_standup.renderer.render_to_clipboard", return_value=False):
        render(DIGEST, stdout=False, clipboard=True)
    assert "warning" in capsys.readouterr().err


def test_render_clipboard_success_no_warning(capsys):
    """Verify that a successful clipboard copy does not emit a warning."""
    with patch("git_standup.renderer.render_to_clipboard", return_value=True):
        render(DIGEST, stdout=False, clipboard=True)
    assert capsys.readouterr().err == ""
