import swisseph as swe

from chart_engine.config import settings


class EphemerisEngine:

    def __init__(self):
        self.ephemeris_path = settings.ephemeris_path

        swe.set_ephe_path(str(self.ephemeris_path))

    def julian_day(
        self,
        year: int,
        month: int,
        day: int,
        hour: float,
    ) -> float:
        return swe.julday(
            year,
            month,
            day,
            hour,
        )