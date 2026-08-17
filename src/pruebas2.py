import swisseph as swe
from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.domain.models import BirthData


birth_data = BirthData(
    data="2001-09-02",
    time="11:02:00",
    latitude=4.7110,
    longitude=-74.0721,
    timezone="America/Bogota",
)

ephemeris = EphemerisEngine()

julian_day = ephemeris.julian_day(
    birth_data
)

print("Julian Day:", julian_day)

result = swe.houses_ex(
    julian_day,
    birth_data.latitude,
    birth_data.longitude,
    b"P",
)

print(result)