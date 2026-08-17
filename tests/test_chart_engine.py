import pytest
from pydantic import ValidationError

from chart_engine import ChartEngine
from chart_engine.domain.models import BirthData


def test_chart_engine_returns_the_complete_deterministic_contract() -> None:
    chart = ChartEngine().calculate(
        BirthData(
            data="2001-09-02",
            time="11:02:00",
            latitude=4.609722,
            longitude=-74.081667,
            timezone="America/Bogota",
        )
    )

    assert chart.birth_data.date.isoformat() == "2001-09-02"
    assert len(chart.planets) == 10
    assert len(chart.houses) == 12
    assert chart.houses[0].longitude == pytest.approx(chart.ascendant.longitude)
    assert all(planet.zodiac is not None for planet in chart.planets)
    assert all(1 <= planet.house <= 12 for planet in chart.planets)
    assert chart.model_dump(mode="json").keys() == {
        "birth_data", "planets", "houses", "ascendant", "midheaven", "aspects"
    }


def test_chart_engine_determinism() -> None:
    birth_data = BirthData(
        data="2001-09-02",
        time="11:02:00",
        latitude=4.609722,
        longitude=-74.081667,
        timezone="America/Bogota",
    )
    
    engine = ChartEngine()
    chart1 = engine.calculate(birth_data)
    chart2 = engine.calculate(birth_data)
    chart3 = ChartEngine().calculate(birth_data)
    
    # Dump models and compare exactly to ensure deterministic output
    dump1 = chart1.model_dump(mode="json")
    dump2 = chart2.model_dump(mode="json")
    dump3 = chart3.model_dump(mode="json")
    
    assert dump1 == dump2
    assert dump2 == dump3


@pytest.mark.parametrize(
    ("city", "latitude", "longitude", "timezone"),
    [
        ("Bogota", 4.609722, -74.081667, "America/Bogota"),
        ("New York", 40.7128, -74.0060, "America/New_York"),
        ("London", 51.5074, -0.1278, "Europe/London"),
        ("Tokyo", 35.6762, 139.6503, "Asia/Tokyo"),
        ("Sydney", -33.8688, 151.2093, "Australia/Sydney"),
    ]
)
def test_chart_engine_multi_location(city: str, latitude: float, longitude: float, timezone: str) -> None:
    birth_data = BirthData(
        data="2001-09-02",
        time="11:02:00",
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
    )
    chart = ChartEngine().calculate(birth_data)
    
    # Ensure basic validation holds for all these locations
    assert len(chart.houses) == 12
    assert len(chart.planets) == 10
    assert 0 <= chart.ascendant.longitude < 360
    assert 0 <= chart.midheaven.longitude < 360


@pytest.mark.parametrize(
    "date_str",
    [
        "2000-01-01",
        "2001-09-02",
        "2010-06-15",
        "2020-12-31",
        "2025-03-20",
    ]
)
def test_chart_engine_multi_date(date_str: str) -> None:
    birth_data = BirthData(
        data=date_str,
        time="12:00:00",
        latitude=4.609722,
        longitude=-74.081667,
        timezone="America/Bogota",
    )
    chart = ChartEngine().calculate(birth_data)
    
    # Ensure basic validation holds
    assert len(chart.houses) == 12
    assert len(chart.planets) == 10


def test_chart_engine_serialization() -> None:
    birth_data = BirthData(
        data="2001-09-02",
        time="11:02:00",
        latitude=4.609722,
        longitude=-74.081667,
        timezone="America/Bogota",
    )
    chart = ChartEngine().calculate(birth_data)
    
    # Testing Pydantic serialization
    dump = chart.model_dump()
    assert isinstance(dump, dict)
    
    json_str = chart.model_dump_json()
    assert isinstance(json_str, str)
    assert "2001-09-02" in json_str
    assert "Sun" in json_str


def test_chart_engine_invalid_inputs_rejected() -> None:
    with pytest.raises(ValidationError):
        BirthData(
            data="not-a-date",
            time="11:02:00",
            latitude=4.609722,
            longitude=-74.081667,
            timezone="America/Bogota",
        )
        
    with pytest.raises(ValidationError):
        BirthData(
            data="2001-09-02",
            time="not-a-time",
            latitude=4.609722,
            longitude=-74.081667,
            timezone="America/Bogota",
        )
