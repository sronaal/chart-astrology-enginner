from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def local_to_utc(
    local_datetime: datetime,
    timezone_name: str,
) -> datetime:
    local_timezone = ZoneInfo(timezone_name)
    localized_datetime = local_datetime.replace(tzinfo=local_timezone)
    return localized_datetime.astimezone(timezone.utc)
