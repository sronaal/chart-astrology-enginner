from datetime import date as Date, time as Time

from pydantic import BaseModel, ConfigDict, Field


class BirthData(BaseModel):
    """Validated input required to calculate a natal chart."""

    model_config = ConfigDict(populate_by_name=True)

    date: Date = Field(alias="data")
    time: Time
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timezone: str

    @property
    def data(self) -> Date:
        """Backward-compatible alias for the original Spanish field name."""
        return self.date


class ZodiacPosition(BaseModel):
    sign: str
    degree: int = Field(ge=0, le=29)
    minute: int = Field(ge=0, le=59)
    second: float = Field(ge=0, lt=60)


class PlanetPosition(BaseModel):
    name: str
    longitude: float = Field(ge=0, lt=360)
    latitude: float
    distance: float
    speed_longitude: float
    retrograde: bool
    zodiac: ZodiacPosition | None = None
    house: int | None = Field(default=None, ge=1, le=12)


class HouseCusp(BaseModel):
    """Ecliptic longitude of one Placidus house cusp."""

    number: int = Field(ge=1, le=12)
    longitude: float = Field(ge=0, lt=360)
    zodiac: ZodiacPosition | None = None


class ChartAngles(BaseModel):
    ascendant: float = Field(ge=0, lt=360)
    midheaven: float = Field(ge=0, lt=360)


class AnglePosition(BaseModel):
    longitude: float = Field(ge=0, lt=360)
    zodiac: ZodiacPosition


class Aspect(BaseModel):
    planet_a: str
    planet_b: str
    name: str
    angle: float = Field(ge=0, le=180)
    separation: float = Field(ge=0, le=180)
    orb: float = Field(ge=0)


class NatalChart(BaseModel):
    """The deterministic, serializable result of a natal-chart calculation."""

    birth_data: BirthData
    planets: list[PlanetPosition] = Field(default_factory=list)
    houses: list[HouseCusp] = Field(default_factory=list)
    ascendant: AnglePosition
    midheaven: AnglePosition
    aspects: list[Aspect] = Field(default_factory=list)
