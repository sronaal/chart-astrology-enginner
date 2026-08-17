from datetime  import datetime

from chart_engine.utils.time import local_to_utc


local = datetime(
    2001,
    9,
    2,
    11,
    2
)

utc = local_to_utc(local, "America/Bogota")

print(utc)