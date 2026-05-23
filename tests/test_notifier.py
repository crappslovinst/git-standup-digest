"""Tests for git_standup.notifier."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from git_standup.notifier import (
    NotifierConfig,
    _detect_backend,
    _send_terminal,
    notify,
)


# ---------------------------------------------------------------------------
# _detect_backend
# ---------------------------------------------------------------------------

def test_detect_backend_prefers_notify_send():
    with patch("shutil.which", side_effect=lambda x: x if x == "notify-send" else None):
        assert _detect_backend() == "notify-send"


def test_detect_backend_falls_back_to_osascript():
    with patch("shutil.which", side_effect=lambda x: x if x == "osascript" else None):
        assert _detect_backend() == "osascript"


def test_detect_backend_falls_back_to_terminal():
    with patch("shutil.which", return_value=None):
        assert _detect_backend() == "terminal"


# ---------------------------------------------------------------------------
# notify — disabled
# ---------------------------------------------------------------------------

def test_notify_disabled_does_nothing():
    cfg = NotifierConfig(enabled=False)
    with patch("git_standup.notifier._detect_backend") as mock_detect:
        notify("hello", cfg)
        mock_detect.assert_not_called()


# ---------------------------------------------------------------------------
# notify — terminal backend
# ---------------------------------------------------------------------------

def test_notify_terminal_backend_prints(capsys):
    cfg = NotifierConfig(backend="terminal")
    notify("standup ready", cfg)
    captured = capsys.readouterr()
    assert "standup ready" in captured.out
    assert "git-standup-digest" in captured.out


# ---------------------------------------------------------------------------
# notify — notify-send backend
# ---------------------------------------------------------------------------

def test_notify_send_called_with_correct_args():
    cfg = NotifierConfig(backend="notify-send", extra_args=["-u", "normal"])
    with patch("subprocess.run") as mock_run:
        notify("3 commits today", cfg)
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "notify-send"
        assert "-u" in cmd
        assert "normal" in cmd
        assert "3 commits today" in cmd


# ---------------------------------------------------------------------------
# notify — osascript backend
# ---------------------------------------------------------------------------

def test_osascript_called_with_script():
    cfg = NotifierConfig(backend="osascript")
    with patch("subprocess.run") as mock_run:
        notify("done", cfg)
        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "osascript"
        assert any("display notification" in arg for arg in cmd)


# ---------------------------------------------------------------------------
# notify — unknown backend falls back to terminal
# ---------------------------------------------------------------------------

def test_unknown_backend_uses_terminal(capsys):
    cfg = NotifierConfig(backend="unknown-tool")
    notify("fallback test", cfg)
    out = capsys.readouterr().out
    assert "fallback test" in out


# ---------------------------------------------------------------------------
# notify — no config uses defaults
# ---------------------------------------------------------------------------

def test_notify_no_config_uses_defaults(capsys):
    with patch("git_standup.notifier._detect_backend", return_value="terminal"):
        notify("default cfg")
    out = capsys.readouterr().out
    assert "default cfg" in out
