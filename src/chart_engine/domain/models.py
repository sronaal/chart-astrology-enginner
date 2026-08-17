from datetime import date, time
from pydantic import BaseModel, Field

"""
BirdData For Calculate Cart 
"""

class BirdData(BaseModel):
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
    
    bird_data: BirdData
    planets: list[PlanetPosition] = Field(
        default_factory=list
    )