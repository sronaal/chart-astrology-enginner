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
    # With Sun (1.5) and Moon (1.5), avg_multiplier = 1.5
    # Trine base orb = 8.0, max_orb = 8.0 * 1.5 = 12.0
    # Separation of 123 from 120 = diff of 3, which is within orb 12.0
    aspects = AspectCalculator().calculate(
        [planet("Sun", 0), planet("Moon", 123), planet("Mars", 200)],
        ascendant_longitude=90.0,
        midheaven_longitude=180.0,
    )

    # Filter only Sun-Moon trine aspect for this test
    sun_moon_trines = [a for a in aspects if a.name == "trine" and 
                       ((a.planet_a == "Sun" and a.planet_b == "Moon") or 
                        (a.planet_a == "Moon" and a.planet_b == "Sun"))]
    assert len(sun_moon_trines) == 1
    assert sun_moon_trines[0].orb == 3


def test_aspect_calculator_golden_reference() -> None:
    # Using planets with multiplier 1.0 to match original expected behavior
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
    
    aspects = AspectCalculator().calculate(planets, ascendant_longitude=90.0, midheaven_longitude=180.0)
    
    # Filter only planet-to-planet aspects (exclude Ascendant/Midheaven)
    found_aspect_pairs = {
        (a.planet_a, a.planet_b) for a in aspects 
        if a.planet_a not in ("Ascendant", "Midheaven") and a.planet_b not in ("Ascendant", "Midheaven")
    }
    
    # Updated expected pairs based on dynamic orb calculations
    # Mercury-Venus (sep ~54.66) is not a sextile (60) within orb: diff=5.34, max_orb=6*0.8=4.8 -> NO
    # Mercury-Mars (sep ~84.61) is not a square (90) within orb: diff=5.39, max_orb=6*0.8=4.8 -> NO
    expected_pairs = {
        ("Sun", "Moon"),
        ("Sun", "Jupiter"),
        ("Sun", "Saturn"),
        ("Sun", "Pluto"),
        ("Moon", "Jupiter"),
        ("Moon", "Pluto"),
        ("Moon", "Saturn"),
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
    # Use Uranus (1.0) and Neptune (1.0) so avg_multiplier = 1.0
    # Trine base orb = 8.0, max_orb = 8.0 * 1.0 = 8.0
    
    # Exact trine at 120 degrees
    aspects = AspectCalculator().calculate(
        [planet("Uranus", 0), planet("Neptune", 120)],
        ascendant_longitude=90.0,
        midheaven_longitude=180.0,
    )
    trine_aspects = [a for a in aspects if a.name == "trine" and 
                     ((a.planet_a == "Uranus" and a.planet_b == "Neptune") or 
                      (a.planet_a == "Neptune" and a.planet_b == "Uranus"))]
    assert len(trine_aspects) == 1
    assert trine_aspects[0].separation == 120
    assert trine_aspects[0].orb == 0
    
    # Boundary before at 112 degrees (diff = 8, exactly at max_orb)
    aspects = AspectCalculator().calculate(
        [planet("Uranus", 0), planet("Neptune", 112)],
        ascendant_longitude=90.0,
        midheaven_longitude=180.0,
    )
    trine_aspects = [a for a in aspects if a.name == "trine" and 
                     ((a.planet_a == "Uranus" and a.planet_b == "Neptune") or 
                      (a.planet_a == "Neptune" and a.planet_b == "Uranus"))]
    assert len(trine_aspects) == 1
    assert trine_aspects[0].separation == 112
    assert trine_aspects[0].orb == 8

    # Boundary after at 128 degrees (diff = 8, exactly at max_orb)
    aspects = AspectCalculator().calculate(
        [planet("Uranus", 0), planet("Neptune", 128)],
        ascendant_longitude=90.0,
        midheaven_longitude=180.0,
    )
    trine_aspects = [a for a in aspects if a.name == "trine" and 
                     ((a.planet_a == "Uranus" and a.planet_b == "Neptune") or 
                      (a.planet_a == "Neptune" and a.planet_b == "Uranus"))]
    assert len(trine_aspects) == 1
    assert trine_aspects[0].separation == 128
    assert trine_aspects[0].orb == 8
    
    # Outside orb at 111.9 degrees (diff = 8.1 > max_orb 8.0)
    aspects = AspectCalculator().calculate(
        [planet("Uranus", 0), planet("Neptune", 111.9)],
        ascendant_longitude=90.0,
        midheaven_longitude=180.0,
    )
    trine_aspects = [a for a in aspects if a.name == "trine" and 
                     ((a.planet_a == "Uranus" and a.planet_b == "Neptune") or 
                      (a.planet_a == "Neptune" and a.planet_b == "Uranus"))]
    assert len(trine_aspects) == 0
