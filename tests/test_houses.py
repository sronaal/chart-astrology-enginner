import pytest

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.astronomy.houses import HOUSE_SYSTEM, HouseCalculator
from chart_engine.astrology.houses import house_for_longitude
from chart_engine.domain.models import BirthData, HouseCusp


@pytest.fixture
def bogota_birth_data() -> BirthData:
    return BirthData(
        date="2001-09-02",
        time="11:02:00",
        latitude=4.7110,
        longitude=-74.0721,
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


def test_house_for_longitude_handles_cusp_and_aries_wraparound() -> None:
    houses = [HouseCusp(number=index + 1, longitude=(350 + index * 30) % 360) for index in range(12)]

    assert house_for_longitude(350, houses) == 1
    assert house_for_longitude(359.99, houses) == 1
    assert house_for_longitude(0, houses) == 1
    assert house_for_longitude(19.99, houses) == 1
    assert house_for_longitude(20, houses) == 2


def test_house_for_longitude_requires_all_cusps() -> None:
    with pytest.raises(ValueError, match="Exactly 12"):
        house_for_longitude(10, [HouseCusp(number=1, longitude=0)])
