import swisseph as swe

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.domain.models import BirthData, ChartAngles, HouseCusp


HOUSE_SYSTEM = b"P"  # Placidus

POLAR_CIRCLE_LATITUDE = 66.5


class HouseCalculator:
    """Calculates Placidus cusps and the primary chart angles."""

    def __init__(self, ephemeris: EphemerisEngine):
        self.ephemeris = ephemeris

    def calculate(self, birth_data: BirthData) -> tuple[list[HouseCusp], ChartAngles]:
        if abs(birth_data.latitude) >= POLAR_CIRCLE_LATITUDE:
            raise ValueError(
                "Placidus is undefined at or beyond the polar circle "
                f"(|latitude| >= {POLAR_CIRCLE_LATITUDE}); "
                f"received latitude {birth_data.latitude}."
            )
        julian_day = self.ephemeris.julian_day(birth_data)
        cusps, ascmc = swe.houses_ex(
            julian_day,
            birth_data.latitude,
            birth_data.longitude,
            HOUSE_SYSTEM,
        )
        # pyswisseph keeps index 0 as a sentinel; the 12 cusps are 1..12.
        houses = [
            HouseCusp(number=index, longitude=longitude % 360)
            for index, longitude in enumerate(cusps[1:], start=1)
        ]
        angles = ChartAngles(
            ascendant=ascmc[0] % 360,
            midheaven=ascmc[1] % 360,
        )
        return houses, angles
