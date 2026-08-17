from chart_engine import ChartEngine
from chart_engine.domain.models import BirthData


def test_chart_engine_returns_the_complete_deterministic_contract() -> None:
    chart = ChartEngine().calculate(
        BirthData(
            data="2001-09-02",
            time="11:02:00",
            latitude=4.7110,
            longitude=-74.0721,
            timezone="America/Bogota",
        )
    )

    assert chart.birth_data.date.isoformat() == "2001-09-02"
    assert len(chart.planets) == 10
    assert len(chart.houses) == 12
    assert chart.houses[0].longitude == chart.ascendant.longitude
    assert all(planet.zodiac is not None for planet in chart.planets)
    assert all(1 <= planet.house <= 12 for planet in chart.planets)
    assert chart.model_dump(mode="json").keys() == {
        "birth_data", "planets", "houses", "ascendant", "midheaven", "aspects"
    }
