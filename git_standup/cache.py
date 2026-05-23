"""Simple file-based cache for git commit results to speed up repeated runs."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "git-standup"
DEFAULT_TTL_SECONDS = 300  # 5 minutes


@dataclass
class CacheConfig:
    cache_dir: Path = field(default_factory=lambda: DEFAULT_CACHE_DIR)
    ttl_seconds: int = DEFAULT_TTL_SECONDS
    enabled: bool = True


def _cache_key(repo_path: str, author: str, since: str) -> str:
    """Derive a stable filename-safe cache key from query parameters."""
    raw = f"{repo_path}|{author}|{since}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _cache_file(config: CacheConfig, key: str) -> Path:
    return config.cache_dir / f"{key}.json"


def load_cached(
    config: CacheConfig, repo_path: str, author: str, since: str
) -> list[dict[str, Any]] | None:
    """Return cached commit dicts if present and fresh, else None."""
    if not config.enabled:
        return None
    key = _cache_key(repo_path, author, since)
    path = _cache_file(config, key)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        if time.time() - data["ts"] > config.ttl_seconds:
            path.unlink(missing_ok=True)
            return None
        return data["commits"]
    except (json.JSONDecodeError, KeyError, OSError):
        return None


def save_cached(
    config: CacheConfig,
    repo_path: str,
    author: str,
    since: str,
    commits: list[dict[str, Any]],
) -> None:
    """Persist commit dicts to cache."""
    if not config.enabled:
        return
    key = _cache_key(repo_path, author, since)
    path = _cache_file(config, key)
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    payload = {"ts": time.time(), "commits": commits}
    path.write_text(json.dumps(payload))


def clear_cache(config: CacheConfig) -> int:
    """Delete all cache files. Returns number of files removed."""
    if not config.cache_dir.exists():
        return 0
    removed = 0
    for f in config.cache_dir.glob("*.json"):
        f.unlink(missing_ok=True)
        removed += 1
    return removed
