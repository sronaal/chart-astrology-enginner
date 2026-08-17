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
    [
        (0, 0, 0),
        (0, 60, 60),
        (0, 180, 180),
        (350, 10, 20),
        (350, 360, 10),
        (10, 350, 20),
        (180, 0, 180),
        (120, 240, 120),
    ],
)
def test_angular_separation_is_the_smallest_arc(first: float, second: float, expected: float) -> None:
    assert angular_separation(first, second) == expected


def test_aspect_calculator_uses_major_aspects_and_orbs() -> None:
    aspects = AspectCalculator().calculate([planet("Sun", 0), planet("Moon", 123), planet("Mars", 200)])

    assert [(aspect.planet_a, aspect.planet_b, aspect.name, aspect.orb) for aspect in aspects] == [
        ("Sun", "Moon", "trine", 3),
    ]


def test_aspect_calculator_golden_reference() -> None:
    planet_positions = {
        "Sun": 160.24559731743716,
        "Moon": 337.6608434919619,
        "Mercury": 182.40549024060013,
        "Venus": 127.74266936099627,
        "Mars": 267.0159384788321,
        "Jupiter": 100.22002002843766,
        "Saturn": 74.43500243814238,
        "Uranus": 322.15508492050645,
        "Neptune": 306.51846490859475,
        "Pluto": 252.56714288238058,
    }
    planets = [planet(name, lon) for name, lon in planet_positions.items()]
    
    aspects = AspectCalculator().calculate(planets)
    
    found_aspect_pairs = {(a.planet_a, a.planet_b) for a in aspects}
    
    expected_pairs = {
        ("Sun", "Moon"),
        ("Sun", "Jupiter"),
        ("Sun", "Saturn"),
        ("Sun", "Pluto"),
        ("Moon", "Jupiter"),
        ("Moon", "Pluto"),
        ("Mercury", "Venus"),
        ("Mercury", "Mars"),
        ("Mercury", "Neptune"),
        ("Venus", "Neptune"),
        ("Venus", "Pluto"),
        ("Mars", "Uranus"),
        ("Saturn", "Uranus"),
        ("Saturn", "Neptune"),
        ("Saturn", "Pluto"),
    }
    
    assert found_aspect_pairs == expected_pairs


def test_aspect_calculator_orb_logic() -> None:
    # Trine is 120, default orb is 8
    # Exact
    aspects = AspectCalculator().calculate([planet("Sun", 0), planet("Moon", 120)])
    assert len(aspects) == 1
    assert aspects[0].name == "trine"
    assert aspects[0].separation == 120
    assert aspects[0].orb == 0
    
    # Boundary before
    aspects = AspectCalculator().calculate([planet("Sun", 0), planet("Moon", 112)])
    assert len(aspects) == 1
    assert aspects[0].name == "trine"
    assert aspects[0].separation == 112
    assert aspects[0].orb == 8

    # Boundary after
    aspects = AspectCalculator().calculate([planet("Sun", 0), planet("Moon", 128)])
    assert len(aspects) == 1
    assert aspects[0].name == "trine"
    assert aspects[0].separation == 128
    assert aspects[0].orb == 8
    
    # Outside orb
    aspects = AspectCalculator().calculate([planet("Sun", 0), planet("Moon", 111.9)])
    assert len(aspects) == 0
