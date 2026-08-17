from datetime import date, time
from pydantic import BaseModel, Field

"""
BirdData For Calculate Cart 
"""

class BirthData(BaseModel):
    data: date
    time: time
    
    latitude: float = Field(
        ge=-90,
        le=90
    )
    
    longitude: float = Field(
        ge=-180,
        le=180
    )
    
    timezone: str
    
    
class PlanetPosition(BaseModel):
    
    name: str
    longitude: float
    latitude: float
    distance: float
    speed_longitude: float
    retrograde: bool
    
class NatalChart(BaseModel):
    
    bird_data: BirthData
    planets: list[PlanetPosition] = Field(
        default_factory=list
    )
    
class HouseCusp(BaseModel):
    """
    Representa la cúspide de una casa astrológica.
    """

    number: int = Field(
        ge=1,
        le=12
    )

    longitude: float = Field(
        ge=0,
        lt=360
    )