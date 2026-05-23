"""Tests for git_standup.scheduler."""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, call, patch

import pytest

from git_standup.scheduler import (
    SchedulerConfig,
    _next_run_dt,
    run_scheduler,
    seconds_until_next_run,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dt(hour: int, minute: int, second: int = 0) -> datetime.datetime:
    return datetime.datetime(2024, 6, 10, hour, minute, second)


# ---------------------------------------------------------------------------
# _next_run_dt
# ---------------------------------------------------------------------------

def test_next_run_same_day_when_before_scheduled_time():
    cfg = SchedulerConfig(run_at_hour=9, run_at_minute=0)
    now = _dt(8, 30)
    nxt = _next_run_dt(cfg, now)
    assert nxt == datetime.datetime(2024, 6, 10, 9, 0, 0)


def test_next_run_next_day_when_after_scheduled_time():
    cfg = SchedulerConfig(run_at_hour=9, run_at_minute=0)
    now = _dt(9, 30)
    nxt = _next_run_dt(cfg, now)
    assert nxt == datetime.datetime(2024, 6, 11, 9, 0, 0)


def test_next_run_next_day_when_exactly_on_scheduled_time():
    """Exact match should still schedule for tomorrow (already triggered)."""
    cfg = SchedulerConfig(run_at_hour=9, run_at_minute=0)
    now = _dt(9, 0, 0)
    nxt = _next_run_dt(cfg, now)
    assert nxt == datetime.datetime(2024, 6, 11, 9, 0, 0)


# ---------------------------------------------------------------------------
# seconds_until_next_run
# ---------------------------------------------------------------------------

def test_seconds_until_next_run_positive():
    cfg = SchedulerConfig(run_at_hour=9, run_at_minute=0)
    now = _dt(8, 0)  # 1 hour before
    secs = seconds_until_next_run(cfg, now)
    assert secs == pytest.approx(3600.0)


def test_seconds_until_next_run_uses_current_time_when_none():
    cfg = SchedulerConfig(run_at_hour=23, run_at_minute=59)
    secs = seconds_until_next_run(cfg)  # no 'now' supplied
    assert secs > 0


# ---------------------------------------------------------------------------
# run_scheduler
# ---------------------------------------------------------------------------

def test_run_scheduler_calls_task_once():
    cfg = SchedulerConfig(run_at_hour=9, run_at_minute=0)
    task = MagicMock()
    fixed_now = _dt(8, 0)

    run_scheduler(
        cfg,
        task,
        _sleep=MagicMock(),
        _now=lambda: fixed_now,
        max_iterations=1,
    )

    task.assert_called_once()


def test_run_scheduler_sleeps_correct_duration():
    cfg = SchedulerConfig(run_at_hour=10, run_at_minute=0)
    sleep_mock = MagicMock()
    fixed_now = _dt(9, 0)  # 1 hour before

    run_scheduler(
        cfg,
        MagicMock(),
        _sleep=sleep_mock,
        _now=lambda: fixed_now,
        max_iterations=1,
    )

    sleep_mock.assert_called_once_with(pytest.approx(3600.0))


def test_run_scheduler_swallows_task_exception():
    cfg = SchedulerConfig(run_at_hour=9, run_at_minute=0)

    def bad_task():
        raise RuntimeError("boom")

    # Should not propagate
    run_scheduler(
        cfg,
        bad_task,
        _sleep=MagicMock(),
        _now=lambda: _dt(8, 0),
        max_iterations=1,
    )


def test_run_scheduler_multiple_iterations():
    cfg = SchedulerConfig(run_at_hour=9, run_at_minute=0)
    task = MagicMock()

    run_scheduler(
        cfg,
        task,
        _sleep=MagicMock(),
        _now=lambda: _dt(8, 0),
        max_iterations=3,
    )

    assert task.call_count == 3
