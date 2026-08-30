from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.astronomy.houses import HouseCalculator
from chart_engine.astronomy.lunar_nodes import LilithCalculator, LunarNodesCalculator
from chart_engine.astronomy.planets import PlanetCalculator
from chart_engine.astronomy.zodiac import longitude_to_zodiac
from chart_engine.astrology.aspects import AspectCalculator
from chart_engine.astrology.houses import house_for_longitude
from chart_engine.domain.models import (
    AnglePosition,
    BirthData,
    LilithPosition,
    LunarNode,
    NatalChart,
    PlanetPosition,
    ZodiacPosition,
)


def _zodiac_position(longitude: float) -> ZodiacPosition:
    sign, degree, minute, second = longitude_to_zodiac(longitude)
    return ZodiacPosition(sign=sign, degree=degree, minute=minute, second=second)


class ChartEngine:
    """Public facade for the deterministic natal-chart calculation pipeline."""

    def __init__(
        self,
        ephemeris: EphemerisEngine | None = None,
        include_minor_aspects: bool = False,
    ):
        ephemeris = ephemeris or EphemerisEngine()
        self.planets = PlanetCalculator(ephemeris)
        self.houses = HouseCalculator(ephemeris)
        self.lunar_nodes = LunarNodesCalculator(ephemeris)
        self.lilith = LilithCalculator(ephemeris)
        self.aspects = AspectCalculator(include_minor_aspects=include_minor_aspects)

    def calculate(self, birth_data: BirthData) -> NatalChart:
        houses, angles = self.houses.calculate(birth_data)
        houses = [
            house.model_copy(update={"zodiac": _zodiac_position(house.longitude)})
            for house in houses
        ]
        
        # Calculate planets with zodiac and house positions
        raw_planets = self.planets.calculate(birth_data)
        planets = []
        for planet in raw_planets:
            house = house_for_longitude(planet.longitude, houses)
            on_cusp = self._is_on_cusp(planet.longitude, houses)
            planets.append(
                planet.model_copy(
                    update={
                        "zodiac": _zodiac_position(planet.longitude),
                        "house": house,
                        "on_cusp": on_cusp,
                    }
                )
            )
        
        # Calculate lunar nodes
        north_lon, south_lon = self.lunar_nodes.calculate(birth_data)
        north_node = LunarNode(
            longitude=north_lon,
            zodiac=_zodiac_position(north_lon),
            house=house_for_longitude(north_lon, houses),
        )
        south_node = LunarNode(
            longitude=south_lon,
            zodiac=_zodiac_position(south_lon),
            house=house_for_longitude(south_lon, houses),
        )
        lunar_nodes = {"north_node": north_node, "south_node": south_node}
        
        # Calculate Lilith
        lilith_lon = self.lilith.calculate(birth_data)
        lilith = LilithPosition(
            longitude=lilith_lon,
            zodiac=_zodiac_position(lilith_lon),
            house=house_for_longitude(lilith_lon, houses),
        )
        
        # Combine planets with lunar nodes and lilith for aspect calculation
        all_points = list(planets)
        
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
            lunar_nodes=lunar_nodes,
            lilith=lilith,
            aspects=self.aspects.calculate(planets, angles.ascendant, angles.midheaven),
        )
    
    def _is_on_cusp(self, longitude: float, houses: list) -> bool:
        """Check if a planet is within 2 degrees of a house cusp."""
        for house in houses:
            distance = abs((longitude - house.longitude) % 360)
            if distance > 180:
                distance = 360 - distance
            if distance <= 2:
                return True
        return False
