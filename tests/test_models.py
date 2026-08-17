from datetime import date, time

import pytest
from pydantic import ValidationError

from chart_engine.domain.models import (
    Aspect,
    BirthData,
    HouseCusp,
    PlanetPosition,
    ZodiacPosition,
)


def test_birth_data_accepts_valid_data() -> None:
    birth_data = BirthData(
        data=date(2001, 9, 2),
        time=time(11, 2, 0),
        latitude=4.609722,
        longitude=-74.081667,
        timezone="America/Bogota",
    )
    assert birth_data.date == date(2001, 9, 2)
    assert birth_data.data == date(2001, 9, 2)
    assert birth_data.latitude == 4.609722
    assert birth_data.longitude == -74.081667
    assert birth_data.timezone == "America/Bogota"


def test_birth_data_accepts_limits() -> None:
    BirthData(
        data=date(2001, 9, 2),
        time=time(11, 2, 0),
        latitude=90.0,
        longitude=180.0,
        timezone="UTC",
    )
    BirthData(
        data=date(2001, 9, 2),
        time=time(11, 2, 0),
        latitude=-90.0,
        longitude=-180.0,
        timezone="UTC",
    )


def test_birth_data_rejects_invalid_latitude() -> None:
    with pytest.raises(ValidationError):
        BirthData(
            data=date(2001, 9, 2),
            time=time(11, 2, 0),
            latitude=90.1,
            longitude=0,
            timezone="UTC",
        )
    with pytest.raises(ValidationError):
        BirthData(
            data=date(2001, 9, 2),
            time=time(11, 2, 0),
            latitude=-90.1,
            longitude=0,
            timezone="UTC",
        )


def test_birth_data_rejects_invalid_longitude() -> None:
    with pytest.raises(ValidationError):
        BirthData(
            data=date(2001, 9, 2),
            time=time(11, 2, 0),
            latitude=0,
            longitude=180.1,
            timezone="UTC",
        )
    with pytest.raises(ValidationError):
        BirthData(
            data=date(2001, 9, 2),
            time=time(11, 2, 0),
            latitude=0,
            longitude=-180.1,
            timezone="UTC",
        )


def test_zodiac_position_limits() -> None:
    ZodiacPosition(sign="Aries", degree=0, minute=0, second=0.0)
    ZodiacPosition(sign="Aries", degree=29, minute=59, second=59.999)

    with pytest.raises(ValidationError):
        ZodiacPosition(sign="Aries", degree=30, minute=0, second=0.0)
    with pytest.raises(ValidationError):
        ZodiacPosition(sign="Aries", degree=0, minute=60, second=0.0)
    with pytest.raises(ValidationError):
        ZodiacPosition(sign="Aries", degree=0, minute=0, second=60.0)


def test_planet_position_limits() -> None:
    PlanetPosition(
        name="Sun",
        longitude=0.0,
        latitude=0.0,
        distance=1.0,
        speed_longitude=1.0,
        retrograde=False,
    )
    PlanetPosition(
        name="Sun",
        longitude=359.999,
        latitude=0.0,
        distance=1.0,
        speed_longitude=1.0,
        retrograde=False,
    )

    with pytest.raises(ValidationError):
        PlanetPosition(
            name="Sun",
            longitude=360.0,
            latitude=0.0,
            distance=1.0,
            speed_longitude=1.0,
            retrograde=False,
        )


def test_house_cusp_limits() -> None:
    HouseCusp(number=1, longitude=0.0)
    HouseCusp(number=12, longitude=359.999)

    with pytest.raises(ValidationError):
        HouseCusp(number=0, longitude=0.0)
    with pytest.raises(ValidationError):
        HouseCusp(number=13, longitude=0.0)
    with pytest.raises(ValidationError):
        HouseCusp(number=1, longitude=360.0)


def test_aspect_limits() -> None:
    Aspect(
        planet_a="Sun",
        planet_b="Moon",
        name="conjunction",
        angle=0.0,
        separation=0.0,
        orb=0.0,
    )
    Aspect(
        planet_a="Sun",
        planet_b="Moon",
        name="opposition",
        angle=180.0,
        separation=180.0,
        orb=8.0,
    )

    with pytest.raises(ValidationError):
        Aspect(
            planet_a="Sun",
            planet_b="Moon",
            name="opposition",
            angle=180.1,
            separation=0.0,
            orb=0.0,
        )
    with pytest.raises(ValidationError):
        Aspect(
            planet_a="Sun",
            planet_b="Moon",
            name="opposition",
            angle=0.0,
            separation=180.1,
            orb=0.0,
        )
