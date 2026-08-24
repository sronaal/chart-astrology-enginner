import pytest

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.astronomy.houses import HOUSE_SYSTEM, POLAR_CIRCLE_LATITUDE, HouseCalculator
from chart_engine.astrology.houses import house_for_longitude
from chart_engine.domain.models import BirthData, HouseCusp


@pytest.fixture
def bogota_birth_data() -> BirthData:
    return BirthData(
        data="2001-09-02",
        time="11:02:00",
        latitude=4.609722,  # Fixed to the exact golden test value
        longitude=-74.081667, # Fixed to the exact golden test value
        timezone="America/Bogota",
    )


def test_house_calculator_returns_placidus_cusps_and_angles(bogota_birth_data: BirthData) -> None:
    houses, angles = HouseCalculator(EphemerisEngine()).calculate(bogota_birth_data)

    assert HOUSE_SYSTEM == b"P"
    assert [house.number for house in houses] == list(range(1, 13))
    assert len(houses) == 12
    assert all(0 <= house.longitude < 360 for house in houses)
    assert 0 <= angles.ascendant < 360
    assert 0 <= angles.midheaven < 360
    assert houses[0].longitude == pytest.approx(angles.ascendant)


def test_house_calculator_reference_values(bogota_birth_data: BirthData) -> None:
    houses, _ = HouseCalculator(EphemerisEngine()).calculate(bogota_birth_data)

    expected_houses = [
        238.839658966542, # 1
        267.202815987659, # 2
        295.714014153486, # 3
        326.037951251709, # 4
        358.152731721913, # 5
        29.743184459779,  # 6
        58.839658966542,  # 7
        87.202815987659,  # 8
        115.714014153486, # 9
        146.037951251709, # 10
        178.152731721913, # 11
        209.743184459779, # 12
    ]

    for index, expected in enumerate(expected_houses):
        assert houses[index].longitude == pytest.approx(expected, abs=1e-10)

    # Test opposing houses are separated by 180 degrees
    for i in range(6):
        house_a = houses[i].longitude
        house_b = houses[i + 6].longitude
        assert abs((house_a - house_b) % 360 - 180) == pytest.approx(0, abs=1e-10)


def test_house_calculator_angles_reference(bogota_birth_data: BirthData) -> None:
    houses, angles = HouseCalculator(EphemerisEngine()).calculate(bogota_birth_data)

    expected_asc = 238.839658966542
    expected_dsc = 58.839658966542
    expected_mc = 146.037951251709
    expected_ic = 326.037951251709

    # Pyswisseph outputs ascendant and midheaven. DSC and IC are calculated manually or from opposite houses
    assert angles.ascendant == pytest.approx(expected_asc, abs=1e-10)
    assert angles.midheaven == pytest.approx(expected_mc, abs=1e-10)
    
    # Calculate DSC and IC mathematically
    dsc = (angles.ascendant + 180.0) % 360
    ic = (angles.midheaven + 180.0) % 360

    assert dsc == pytest.approx(expected_dsc, abs=1e-10)
    assert ic == pytest.approx(expected_ic, abs=1e-10)

    # Check they align with 1st, 7th, 10th and 4th houses exactly
    assert houses[0].longitude == pytest.approx(angles.ascendant, abs=1e-10) # 1st = ASC
    assert houses[6].longitude == pytest.approx(dsc, abs=1e-10)             # 7th = DSC
    assert houses[9].longitude == pytest.approx(angles.midheaven, abs=1e-10)# 10th = MC
    assert houses[3].longitude == pytest.approx(ic, abs=1e-10)              # 4th = IC


def test_house_for_longitude_handles_cusp_and_aries_wraparound() -> None:
    houses = [HouseCusp(number=index + 1, longitude=(350 + index * 30) % 360) for index in range(12)]

    assert house_for_longitude(350, houses) == 1
    assert house_for_longitude(359.99, houses) == 1
    assert house_for_longitude(0, houses) == 1
    assert house_for_longitude(19.99, houses) == 1
    assert house_for_longitude(20, houses) == 2


def test_house_for_longitude_boundaries() -> None:
    houses = [HouseCusp(number=index + 1, longitude=(index * 30)) for index in range(12)]
    # House 1 is exactly at 0
    # House 2 is exactly at 30
    
    # Exactly on the cusp 30 -> should be house 2
    assert house_for_longitude(30.0, houses) == 2
    
    # Slightly before -> should be house 1
    assert house_for_longitude(29.9999, houses) == 1
    
    # Slightly after -> should be house 2
    assert house_for_longitude(30.0001, houses) == 2


def test_house_for_longitude_reference_assignment() -> None:
    expected_houses = [
        238.839658966542, # 1
        267.202815987659, # 2
        295.714014153486, # 3
        326.037951251709, # 4
        358.152731721913, # 5
        29.743184459779,  # 6
        58.839658966542,  # 7
        87.202815987659,  # 8
        115.714014153486, # 9
        146.037951251709, # 10
        178.152731721913, # 11
        209.743184459779, # 12
    ]
    houses = [HouseCusp(number=i+1, longitude=lon) for i, lon in enumerate(expected_houses)]

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

    expected_assignment = {
        "Sun": 10,
        "Moon": 4,
        "Mercury": 11,
        "Venus": 9,
        "Mars": 1,
        "Jupiter": 8,
        "Saturn": 7,
        "Uranus": 3,
        "Neptune": 3,
        "Pluto": 1,
    }

    for name, expected in expected_assignment.items():
        assert house_for_longitude(planet_positions[name], houses) == expected


def test_house_for_longitude_requires_all_cusps() -> None:
    with pytest.raises(ValueError, match="Exactly 12"):
        house_for_longitude(10, [HouseCusp(number=1, longitude=0)])


@pytest.mark.parametrize("latitude", [67.0, -67.0, 66.5, -66.5])
def test_house_calculator_rejects_latitudes_at_or_beyond_polar_circle(
    bogota_birth_data: BirthData, latitude: float
) -> None:
    birth_data = bogota_birth_data.model_copy(update={"latitude": latitude})

    with pytest.raises(ValueError) as exc_info:
        HouseCalculator(EphemerisEngine()).calculate(birth_data)

    assert "polar circle" in str(exc_info.value)
    assert f"received latitude {latitude}" in str(exc_info.value)
    assert POLAR_CIRCLE_LATITUDE == 66.5


@pytest.mark.parametrize("latitude", [59.3, 60.0])
def test_house_calculator_allows_high_but_valid_latitudes(
    bogota_birth_data: BirthData, latitude: float
) -> None:
    birth_data = bogota_birth_data.model_copy(update={"latitude": latitude})

    houses, angles = HouseCalculator(EphemerisEngine()).calculate(birth_data)

    assert len(houses) == 12
    assert all(0 <= house.longitude < 360 for house in houses)
    assert 0 <= angles.ascendant < 360
    assert 0 <= angles.midheaven < 360
    assert houses[0].longitude == pytest.approx(angles.ascendant)
