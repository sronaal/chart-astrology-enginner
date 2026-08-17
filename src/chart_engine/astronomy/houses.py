import swisseph as swe

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.domain.models import (
    BirthData,
    HouseCusp,
    ChartAngles,
)


class HouseCalculator:

    def __init__(
        self,
        ephemeris: EphemerisEngine,
    ):
        self.ephemeris = ephemeris

    def calculate(
        self,
        birth_data: BirthData,
    ) -> tuple[list[HouseCusp], ChartAngles]:

        julian_day = self.ephemeris.julian_day(
            birth_data,
        )

        cusps, ascmc = swe.houses_ex(
            julian_day,
            birth_data.latitude,
            birth_data.longitude,
            b"P",
        )

        houses = [
            HouseCusp(
                number=index + 1,
                longitude=longitude,
            )
            for index, longitude in enumerate(cusps)
        ]

        angles = ChartAngles(
            ascendant=ascmc[0],
            midheaven=ascmc[1],
        )

        return houses, angles