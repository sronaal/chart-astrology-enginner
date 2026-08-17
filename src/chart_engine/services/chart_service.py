from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.astronomy.houses import HouseCalculator
from chart_engine.astronomy.planets import PlanetCalculator
from chart_engine.astronomy.zodiac import longitude_to_zodiac
from chart_engine.astrology.aspects import AspectCalculator
from chart_engine.astrology.houses import house_for_longitude
from chart_engine.domain.models import AnglePosition, BirthData, NatalChart, ZodiacPosition


def _zodiac_position(longitude: float) -> ZodiacPosition:
    sign, degree, minute, second = longitude_to_zodiac(longitude)
    return ZodiacPosition(sign=sign, degree=degree, minute=minute, second=second)


class ChartEngine:
    """Public facade for the deterministic natal-chart calculation pipeline."""

    def __init__(self, ephemeris: EphemerisEngine | None = None):
        ephemeris = ephemeris or EphemerisEngine()
        self.planets = PlanetCalculator(ephemeris)
        self.houses = HouseCalculator(ephemeris)
        self.aspects = AspectCalculator()

    def calculate(self, birth_data: BirthData) -> NatalChart:
        houses, angles = self.houses.calculate(birth_data)
        houses = [
            house.model_copy(update={"zodiac": _zodiac_position(house.longitude)})
            for house in houses
        ]
        planets = [
            planet.model_copy(
                update={
                    "zodiac": _zodiac_position(planet.longitude),
                    "house": house_for_longitude(planet.longitude, houses),
                }
            )
            for planet in self.planets.calculate(birth_data)
        ]
        return NatalChart(
            birth_data=birth_data,
            planets=planets,
            houses=houses,
            ascendant=AnglePosition(
                longitude=angles.ascendant,
                zodiac=_zodiac_position(angles.ascendant),
            ),
            midheaven=AnglePosition(
                longitude=angles.midheaven,
                zodiac=_zodiac_position(angles.midheaven),
            ),
            aspects=self.aspects.calculate(planets),
        )
