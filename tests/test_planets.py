from datetime import date, time

import pytest

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.astronomy.planets import PlanetCalculator
from chart_engine.domain.models import BirthData


@pytest.fixture
def bogota_birth_data() -> BirthData:
    return BirthData(
        data=date(2001, 9, 2),
        time=time(11, 2, 0),
        latitude=4.609722,
        longitude=-74.081667,
        timezone="America/Bogota",
    )


def test_planet_calculator_against_reference_values(bogota_birth_data: BirthData) -> None:
    ephemeris = EphemerisEngine()
    calculator = PlanetCalculator(ephemeris)

    planets = calculator.calculate(bogota_birth_data)
    
    # Asserting exact number of planets
    assert len(planets) == 10

    # Transforming result into a dictionary for easy assertion
    planets_dict = {p.name: p for p in planets}

    # Reference values
    expected = {
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

    retrograde_expected = {"Uranus", "Neptune"}

    for name, expected_longitude in expected.items():
        planet = planets_dict.get(name)
        assert planet is not None, f"Planet {name} not found"
        assert planet.longitude == pytest.approx(expected_longitude, abs=1e-10)
        
        # Verify retrograde flag
        if name in retrograde_expected:
            assert planet.retrograde is True, f"{name} should be retrograde"
            assert planet.speed_longitude < 0
        else:
            assert planet.retrograde is False, f"{name} should not be retrograde"
            assert planet.speed_longitude >= 0
