"""Renders the formatted digest to various outputs (stdout, file, clipboard)."""

import sys
from pathlib import Path
from typing import Optional


def render_to_stdout(digest: str) -> None:
    """Print the digest to standard output."""
    sys.stdout.write(digest)


def render_to_file(digest: str, path: Path, append: bool = False) -> None:
    """Write the digest to a file.

    Args:
        digest: The formatted digest string.
        path: Destination file path.
        append: If True, append to existing file instead of overwriting.
    """
    mode = "a" if append else "w"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(digest, encoding="utf-8") if not append else _append(path, digest)


def _append(path: Path, content: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(content)


def render_to_clipboard(digest: str) -> bool:
    """Copy the digest to the system clipboard.

    Returns True on success, False if clipboard support is unavailable.
    """
    try:
        import subprocess

        if sys.platform == "darwin":
            proc = subprocess.run(["pbcopy"], input=digest.encode(), check=True)
        elif sys.platform.startswith("linux"):
            proc = subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=digest.encode(),
                check=True,
            )
        elif sys.platform == "win32":
            proc = subprocess.run(["clip"], input=digest.encode("utf-16"), check=True)
        else:
            return False
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def render(
    digest: str,
    *,
    stdout: bool = True,
    file_path: Optional[Path] = None,
    append: bool = False,
    clipboard: bool = False,
) -> None:
    """Dispatch rendering to one or more outputs."""
    if stdout:
        render_to_stdout(digest)
    if file_path is not None:
        render_to_file(digest, file_path, append=append)
    if clipboard:
        success = render_to_clipboard(digest)
        if not success:
            sys.stderr.write("warning: clipboard copy failed or unsupported\n")
