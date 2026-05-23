"""Desktop / terminal notifications for standup digest events."""
from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class NotifierConfig:
    title: str = "git-standup-digest"
    enabled: bool = True
    # Override auto-detected backend: 'notify-send', 'osascript', 'terminal', or None
    backend: Optional[str] = None
    extra_args: list[str] = field(default_factory=list)


def _detect_backend() -> Optional[str]:
    """Return the first available notification backend."""
    if shutil.which("notify-send"):
        return "notify-send"
    if shutil.which("osascript"):
        return "osascript"
    return "terminal"


def _send_notify_send(title: str, message: str, extra_args: list[str]) -> None:
    cmd = ["notify-send", *extra_args, title, message]
    subprocess.run(cmd, check=False, capture_output=True)


def _send_osascript(title: str, message: str, extra_args: list[str]) -> None:
    script = f'display notification "{message}" with title "{title}"'
    cmd = ["osascript", "-e", script, *extra_args]
    subprocess.run(cmd, check=False, capture_output=True)


def _send_terminal(title: str, message: str, _extra_args: list[str]) -> None:
    print(f"[{title}] {message}")


_BACKENDS = {
    "notify-send": _send_notify_send,
    "osascript": _send_osascript,
    "terminal": _send_terminal,
}


def notify(message: str, cfg: Optional[NotifierConfig] = None) -> None:
    """Send a desktop or terminal notification with *message*."""
    if cfg is None:
        cfg = NotifierConfig()
    if not cfg.enabled:
        return
    backend = cfg.backend or _detect_backend()
    if backend is None:
        return
    sender = _BACKENDS.get(backend, _send_terminal)
    sender(cfg.title, message, cfg.extra_args)
