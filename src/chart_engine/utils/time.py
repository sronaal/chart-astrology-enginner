from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def local_to_utc(
    local_datetime: datetime,
    timezone_name: str,
) -> datetime:
    tz = ZoneInfo(timezone_name)
    # Construir el datetime directamente con la zona para que zoneinfo resuelva DST correctamente
    localized_datetime = datetime(
        local_datetime.year,
        local_datetime.month,
        local_datetime.day,
        local_datetime.hour,
        local_datetime.minute,
        local_datetime.second,
        tzinfo=tz
    )
    return localized_datetime.astimezone(timezone.utc)
