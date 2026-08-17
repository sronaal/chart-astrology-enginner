import swisseph as swe

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.domain.models import BirdData, PlanetPosition


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
    "Pluto": swe.PLUTO
    
}


class PlanetCalculator:
    
    def __init__(self, ephemeris: EphemerisEngine):
        self.ephemeris = ephemeris
    
    def calculute(
        self,
        birth_data: BirdData,
    ) -> list[PlanetPosition]:
        
        julian_day = self.ephemeris.julian_day(
            birth_data.date.year,
            birth_data.date.month,
            birth_data.date.day,
            birth_data.time.hour
            + birth_data.time.minute / 60
            + birth_data.time.second / 3600
        )
        
        planets = []
        
        for name, planet_id in PLANETS.items():
            result, flags = swe.calc_ut(
                julian_day,
                planet_id
            )
            
        longitude = result[0]
        latitude = result[1]
        distance = result[2]
        speed_longitude = result[3]
        
        planets.append(
            PlanetPosition(
                name=name,
                longitude=longitude,
                latitude=latitude,
                distance=distance,
                speed_longitude=speed_longitude,
                retrograde=speed_longitude < 0,
            )
        )