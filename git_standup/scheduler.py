"""Scheduled digest generation — run at a fixed time each day."""

from __future__ import annotations

import datetime
import logging
import time
from dataclasses import dataclass, field
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class SchedulerConfig:
    """Configuration for the daily scheduler."""

    # 24-hour clock, e.g. (9, 0) means 09:00
    run_at_hour: int = 9
    run_at_minute: int = 0
    # How often (seconds) the scheduler wakes up to check the time
    poll_interval: float = 30.0
    # Optional timezone name recognised by zoneinfo / dateutil; None = local time
    timezone: Optional[str] = None


def _next_run_dt(cfg: SchedulerConfig, now: datetime.datetime) -> datetime.datetime:
    """Return the next datetime at which the digest should run."""
    candidate = now.replace(
        hour=cfg.run_at_hour,
        minute=cfg.run_at_minute,
        second=0,
        microsecond=0,
    )
    if candidate <= now:
        candidate += datetime.timedelta(days=1)
    return candidate


def seconds_until_next_run(cfg: SchedulerConfig, now: Optional[datetime.datetime] = None) -> float:
    """Return the number of seconds until the next scheduled run."""
    if now is None:
        now = datetime.datetime.now()
    return (_next_run_dt(cfg, now) - now).total_seconds()


def run_scheduler(
    cfg: SchedulerConfig,
    task: Callable[[], None],
    *,
    _sleep: Callable[[float], None] = time.sleep,
    _now: Callable[[], datetime.datetime] = datetime.datetime.now,
    max_iterations: Optional[int] = None,
) -> None:
    """Block forever, calling *task* once per day at the configured time.

    Parameters
    ----------
    cfg:            Scheduler configuration.
    task:           Zero-argument callable executed on each trigger.
    _sleep/_now:    Injected for testing.
    max_iterations: Stop after this many triggers (useful in tests).
    """
    logger.info(
        "Scheduler started — will run daily at %02d:%02d",
        cfg.run_at_hour,
        cfg.run_at_minute,
    )
    iterations = 0
    while True:
        wait = seconds_until_next_run(cfg, _now())
        logger.debug("Next run in %.0f seconds", wait)
        _sleep(wait)
        logger.info("Triggering scheduled digest")
        try:
            task()
        except Exception:  # noqa: BLE001
            logger.exception("Scheduled task raised an exception")
        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
