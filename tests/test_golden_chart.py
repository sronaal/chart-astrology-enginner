"""Golden test for regression testing of the astrology chart engine."""

import pytest

from chart_engine import ChartEngine
from chart_engine.domain.models import BirthData


def test_einstein_golden_chart() -> None:
    """
    Golden test using Albert Einstein's birth data to ensure calculations
    remain consistent across refactorizations.
    
    Data:
    - Date: 1879-03-14
    - Time: 11:30:00
    - Latitude: 48.398
    - Longitude: 9.991
    - Timezone: Europe/Berlin
    """
    birth_data = BirthData(
        data="1879-03-14",
        time="11:30:00",
        latitude=48.398,
        longitude=9.991,
        timezone="Europe/Berlin",
    )
    
    chart = ChartEngine().calculate(birth_data)
    
    # Find Sun and Moon positions
    sun = next(p for p in chart.planets if p.name == "Sun")
    moon = next(p for p in chart.planets if p.name == "Moon")
    
    # Assertion 1: Sun must be in Pisces (longitude approx 353° - 355°)
    assert sun.zodiac.sign == "Pisces"
    assert sun.longitude == pytest.approx(353.5, abs=0.05)
    
    # Assertion 2: Moon must be in Sagittarius
    assert moon.zodiac.sign == "Sagittarius"
    
    # Assertion 3: Ascendant must be in Cancer (based on actual calculation)
    assert chart.ascendant.zodiac.sign == "Cancer"
    
    # Assertion 4: Aspects list must have length > 0
    assert len(chart.aspects) > 0
    
    # Assertion 5: Must include at least one aspect involving Ascendant or Midheaven
    aspects_with_angles = [
        a for a in chart.aspects
        if a.planet_a in ("Ascendant", "Midheaven") or a.planet_b in ("Ascendant", "Midheaven")
    ]
    assert len(aspects_with_angles) > 0
