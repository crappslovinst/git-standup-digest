"""Collect git commits from local repositories for a given author and date range."""

import subprocess
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path


@dataclass
class Commit:
    repo: str
    hash: str
    message: str
    timestamp: datetime


@dataclass
class CollectorConfig:
    repos: list[Path]
    author: str
    since: date
    until: date = field(default_factory=date.today)


def _run_git_log(repo: Path, author: str, since: date, until: date) -> list[Commit]:
    """Run git log in a single repo and return Commit objects."""
    fmt = "%H|||%s|||%ai"
    cmd = [
        "git",
        "-C",
        str(repo),
        "log",
        f"--author={author}",
        f"--since={since.isoformat()}",
        f"--until={until.isoformat()} 23:59:59",
        f"--pretty=format:{fmt}",
        "--no-merges",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError:
        return []

    commits = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("|||")
        if len(parts) != 3:
            continue
        hash_, message, ts_str = parts
        try:
            timestamp = datetime.fromisoformat(ts_str)
        except ValueError:
            continue
        commits.append(
            Commit(
                repo=repo.name,
                hash=hash_[:7],
                message=message.strip(),
                timestamp=timestamp,
            )
        )
    return commits


def collect_commits(config: CollectorConfig) -> list[Commit]:
    """Collect commits across all configured repositories."""
    all_commits: list[Commit] = []
    for repo in config.repos:
        repo_path = Path(repo).expanduser().resolve()
        if not (repo_path / ".git").exists():
            continue
        commits = _run_git_log(repo_path, config.author, config.since, config.until)
        all_commits.extend(commits)
    all_commits.sort(key=lambda c: c.timestamp)
    return all_commits
