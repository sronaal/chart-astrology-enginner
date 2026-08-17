from datetime import date, time

import pytest

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.domain.models import BirthData


def test_julian_day_calculation() -> None:
    engine = EphemerisEngine()
    
    birth_data = BirthData(
        data=date(2001, 9, 2),
        time=time(11, 2, 0),
        latitude=4.609722,
        longitude=-74.081667,
        timezone="America/Bogota",
    )
    
    julian_day = engine.julian_day(birth_data)
    
    # Expected Julian Day for 2001-09-02 16:02 UTC
    expected = 2452155.168055555783
    assert julian_day == pytest.approx(expected, abs=1e-10)
