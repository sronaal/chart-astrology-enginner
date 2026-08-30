from datetime import datetime

import swisseph as swe

from chart_engine.config import settings
from chart_engine.domain.models import BirthData
from chart_engine.utils.time import local_to_utc



class EphemerisEngine:

    def __init__(self):
        self.ephemeris_path = settings.ephemeris_path

        swe.set_ephe_path(str(self.ephemeris_path))

    def julian_day(
        self,
        birth_data: BirthData,
    ) -> float:

        local_datetime = datetime.combine(
            birth_data.date,
            birth_data.time,
        )

        utc_datetime = local_to_utc(
            local_datetime,
            birth_data.timezone,
        )

        hour = (
            utc_datetime.hour
            + utc_datetime.minute / 60
            + utc_datetime.second / 3600
            + utc_datetime.microsecond / 3_600_000_000
        )

        return swe.julday(
            utc_datetime.year,
            utc_datetime.month,
            utc_datetime.day,
            hour,
        )