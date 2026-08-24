from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def local_to_utc(
    local_datetime: datetime,
    timezone_name: str,
) -> datetime:
    tz = ZoneInfo(timezone_name)
    # Build the datetime directly with the zone so zoneinfo resolves DST correctly.
    localized_datetime = datetime(
        local_datetime.year,
        local_datetime.month,
        local_datetime.day,
        local_datetime.hour,
        local_datetime.minute,
        local_datetime.second,
        tzinfo=tz
    )
    if localized_datetime.astimezone(timezone.utc).astimezone(tz) != localized_datetime:
        raise ValueError(
            f"Local time {localized_datetime.isoformat()} does not exist in timezone "
            f"'{timezone_name}' because it was skipped by a DST spring-forward."
        )
    if localized_datetime.replace(fold=1).utcoffset() != localized_datetime.utcoffset():
        raise ValueError(
            f"Local time {localized_datetime.isoformat()} is ambiguous in timezone "
            f"'{timezone_name}' because it occurs twice due to a DST fall-back."
        )
    return localized_datetime.astimezone(timezone.utc)
