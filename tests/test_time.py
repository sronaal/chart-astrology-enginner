from datetime import datetime, timezone

import pytest

from chart_engine.utils.time import local_to_utc


@pytest.mark.parametrize(
    ("local_datetime", "timezone_name", "expected_utc"),
    [
        (
            datetime(2001, 9, 2, 11, 2),
            "America/Bogota",
            datetime(2001, 9, 2, 16, 2, tzinfo=timezone.utc),
        ),
        (
            datetime(2001, 9, 2, 11, 2),
            "UTC",
            datetime(2001, 9, 2, 11, 2, tzinfo=timezone.utc),
        ),
        (
            datetime(2001, 9, 2, 11, 2),
            "America/New_York",
            datetime(2001, 9, 2, 15, 2, tzinfo=timezone.utc),
        ),
        (
            datetime(2001, 9, 2, 0, 0, 0),
            "America/Bogota",
            datetime(2001, 9, 2, 5, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2001, 9, 2, 12, 0, 0),
            "America/Bogota",
            datetime(2001, 9, 2, 17, 0, tzinfo=timezone.utc),
        ),
        (
            datetime(2001, 9, 2, 23, 59, 59),
            "America/Bogota",
            datetime(2001, 9, 3, 4, 59, 59, tzinfo=timezone.utc),
        ),
    ],
)
def test_local_to_utc_uses_the_iana_offset_for_the_input_date(
    local_datetime: datetime,
    timezone_name: str,
    expected_utc: datetime,
) -> None:
    assert local_to_utc(local_datetime, timezone_name) == expected_utc
