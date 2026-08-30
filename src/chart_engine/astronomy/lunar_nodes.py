import swisseph as swe

from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.domain.models import BirthData, LilithPosition, LunarNode


class LunarNodesCalculator:
    """Calculates True and Mean Lunar Nodes."""

    def __init__(self, ephemeris: EphemerisEngine):
        self.ephemeris = ephemeris

    def calculate(self, birth_data: BirthData) -> tuple[float, float]:
        """Calculate North and South lunar nodes.
        
        Returns:
            Tuple of (north_node_longitude, south_node_longitude)
        """
        julian_day = self.ephemeris.julian_day(birth_data)

        # Calculate Mean Node using Swiss Ephemeris
        north_node_result_tuple = swe.calc_ut(julian_day, swe.MEAN_NODE)
        north_node_result = north_node_result_tuple[0]
        
        north_longitude = north_node_result[0] % 360
        south_longitude = (north_longitude + 180) % 360

        return north_longitude, south_longitude


class LilithCalculator:
    """Calculates Black Moon Lilith position."""

    def __init__(self, ephemeris: EphemerisEngine):
        self.ephemeris = ephemeris

    def calculate(self, birth_data: BirthData) -> float:
        """Calculate Black Moon Lilith (oscillating apogee)."""
        julian_day = self.ephemeris.julian_day(birth_data)

        # Calculate Lilith using SE_LILITH (Black Moon - osculating apogee)
        lilith_result_tuple = swe.calc_ut(julian_day, swe.LILITH)
        lilith_result = lilith_result_tuple[0]
        
        return lilith_result[0] % 360
