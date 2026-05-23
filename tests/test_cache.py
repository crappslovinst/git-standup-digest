"""Tests for git_standup.cache."""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from git_standup.cache import (
    CacheConfig,
    _cache_key,
    clear_cache,
    load_cached,
    save_cached,
)

REPO = "/home/user/myproject"
AUTHOR = "alice"
SINCE = "2024-01-01"
SAMPLE_COMMITS = [{"hash": "abc123", "message": "fix bug"}]


@pytest.fixture()
def cfg(tmp_path: Path) -> CacheConfig:
    return CacheConfig(cache_dir=tmp_path / "cache", ttl_seconds=60, enabled=True)


def test_cache_key_is_deterministic() -> None:
    k1 = _cache_key(REPO, AUTHOR, SINCE)
    k2 = _cache_key(REPO, AUTHOR, SINCE)
    assert k1 == k2


def test_cache_key_differs_for_different_inputs() -> None:
    k1 = _cache_key(REPO, AUTHOR, SINCE)
    k2 = _cache_key(REPO, "bob", SINCE)
    assert k1 != k2


def test_load_cached_returns_none_when_missing(cfg: CacheConfig) -> None:
    assert load_cached(cfg, REPO, AUTHOR, SINCE) is None


def test_save_and_load_roundtrip(cfg: CacheConfig) -> None:
    save_cached(cfg, REPO, AUTHOR, SINCE, SAMPLE_COMMITS)
    result = load_cached(cfg, REPO, AUTHOR, SINCE)
    assert result == SAMPLE_COMMITS


def test_load_returns_none_when_disabled(cfg: CacheConfig) -> None:
    save_cached(cfg, REPO, AUTHOR, SINCE, SAMPLE_COMMITS)
    cfg.enabled = False
    assert load_cached(cfg, REPO, AUTHOR, SINCE) is None


def test_save_does_nothing_when_disabled(cfg: CacheConfig) -> None:
    cfg.enabled = False
    save_cached(cfg, REPO, AUTHOR, SINCE, SAMPLE_COMMITS)
    assert not any(cfg.cache_dir.glob("*.json")) if cfg.cache_dir.exists() else True


def test_load_returns_none_after_ttl_expired(cfg: CacheConfig, tmp_path: Path) -> None:
    cfg.ttl_seconds = 1
    save_cached(cfg, REPO, AUTHOR, SINCE, SAMPLE_COMMITS)
    # Backdate the timestamp so it appears expired
    cache_files = list(cfg.cache_dir.glob("*.json"))
    assert cache_files
    data = json.loads(cache_files[0].read_text())
    data["ts"] = time.time() - 10
    cache_files[0].write_text(json.dumps(data))
    assert load_cached(cfg, REPO, AUTHOR, SINCE) is None


def test_clear_cache_removes_files(cfg: CacheConfig) -> None:
    save_cached(cfg, REPO, AUTHOR, SINCE, SAMPLE_COMMITS)
    save_cached(cfg, REPO, "bob", SINCE, SAMPLE_COMMITS)
    removed = clear_cache(cfg)
    assert removed == 2
    assert list(cfg.cache_dir.glob("*.json")) == []


def test_clear_cache_returns_zero_if_no_dir(cfg: CacheConfig) -> None:
    assert clear_cache(cfg) == 0
