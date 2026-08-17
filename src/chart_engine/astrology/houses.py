"""Astrological helpers built from house-cusp calculations."""

from chart_engine.domain.models import HouseCusp


def house_for_longitude(longitude: float, houses: list[HouseCusp]) -> int:
    """Return the house containing a longitude, including its own cusp."""
    if len(houses) != 12:
        raise ValueError("Exactly 12 house cusps are required")
    normalized_longitude = longitude % 360
    for index, cusp in enumerate(houses):
        next_cusp = houses[(index + 1) % len(houses)]
        span = (next_cusp.longitude - cusp.longitude) % 360
        offset = (normalized_longitude - cusp.longitude) % 360
        if offset < span or (span == 0 and offset == 0):
            return cusp.number
    raise ValueError("House cusps do not define a valid circular sequence")
