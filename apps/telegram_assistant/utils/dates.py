from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo


def day_bounds(dt: datetime, tz: str) -> tuple[datetime, datetime]:
    zone = ZoneInfo(tz)
    localized = dt.astimezone(zone)
    start = datetime.combine(localized.date(), time.min, tzinfo=zone)
    end = start + timedelta(days=1)
    return start, end


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
