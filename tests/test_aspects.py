import pytest

from chart_engine.astrology.aspects import AspectCalculator, angular_separation
from chart_engine.domain.models import PlanetPosition


def planet(name: str, longitude: float) -> PlanetPosition:
    return PlanetPosition(
        name=name,
        longitude=longitude,
        latitude=0,
        distance=1,
        speed_longitude=1,
        retrograde=False,
    )


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [(0, 0, 0), (0, 60, 60), (0, 180, 180), (350, 10, 20)],
)
def test_angular_separation_is_the_smallest_arc(first: float, second: float, expected: float) -> None:
    assert angular_separation(first, second) == expected


def test_aspect_calculator_uses_major_aspects_and_orbs() -> None:
    aspects = AspectCalculator().calculate([planet("Sun", 0), planet("Moon", 123), planet("Mars", 200)])

    assert [(aspect.planet_a, aspect.planet_b, aspect.name, aspect.orb) for aspect in aspects] == [
        ("Sun", "Moon", "trine", 3),
    ]
