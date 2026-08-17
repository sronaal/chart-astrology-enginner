import swisseph as swe

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.domain.models import BirthData, PlanetPosition


PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}


class PlanetCalculator:

    def __init__(
        self,
        ephemeris: EphemerisEngine,
    ):
        self.ephemeris = ephemeris

    def calculate(
        self,
        birth_data: BirthData,
    ) -> list[PlanetPosition]:

        julian_day = self.ephemeris.julian_day(
            birth_data,
        )

        planets = []

        for name, planet_id in PLANETS.items():

            result, flags, message = swe.calc_ut(
                julian_day,
                planet_id,
            )

            longitude = result[0]
            latitude = result[1]
            distance = result[2]
            speed_longitude = result[3]

            # La retrogradación se determina por velocidad longitudinal negativa
            # Esta es la forma estándar ya que pyswisseph no exporta FLG_RETROGRADE
            retrograde = speed_longitude < 0

            planets.append(
                PlanetPosition(
                    name=name,
                    longitude=longitude,
                    latitude=latitude,
                    distance=distance,
                    speed_longitude=speed_longitude,
                    retrograde=retrograde,
                )
            )

        return planets