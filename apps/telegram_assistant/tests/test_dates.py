from datetime import datetime, timezone

from apps.telegram_assistant.utils.dates import day_bounds


def test_day_bounds_returns_24h_range():
    now = datetime(2026, 1, 13, 10, 0, tzinfo=timezone.utc)
    start, end = day_bounds(now, "Europe/Moscow")
    assert (end - start).total_seconds() == 24 * 3600
