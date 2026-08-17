from itertools import combinations
from typing import NamedTuple

from chart_engine.domain.models import Aspect, PlanetPosition


# Multiplicadores de orbe dinámicos para cada cuerpo celeste
PLANET_ORB_MULTIPLIER: dict[str, float] = {
    "Sun": 1.5,
    "Moon": 1.5,
    "Mercury": 0.8,
    "Venus": 0.8,
    "Mars": 0.8,
    "Jupiter": 1.2,
    "Saturn": 1.2,
    "Uranus": 1.0,
    "Neptune": 1.0,
    "Pluto": 1.0,
    "Ascendant": 1.5,
    "Midheaven": 1.5,
}


ASPECTS: dict[str, tuple[float, float]] = {
    "conjunction": (0.0, 8.0),
    "sextile": (60.0, 6.0),
    "square": (90.0, 6.0),
    "trine": (120.0, 8.0),
    "opposition": (180.0, 8.0),
}


class CelestialBody(NamedTuple):
    """Representa un cuerpo celeste (planeta o ángulo) para cálculo de aspectos."""
    name: str
    longitude: float


def angular_separation(first_longitude: float, second_longitude: float) -> float:
    """Return the smallest separation between two ecliptic longitudes."""
    difference = abs((first_longitude - second_longitude) % 360)
    return min(difference, 360 - difference)


class AspectCalculator:
    """Finds major Ptolemaic aspects using configurable default orbs."""

    def __init__(self, aspects: dict[str, tuple[float, float]] | None = None):
        self.aspects = aspects or ASPECTS

    def calculate(
        self,
        planets: list[PlanetPosition],
        ascendant_longitude: float,
        midheaven_longitude: float,
    ) -> list[Aspect]:
        found: list[Aspect] = []
        
        # Construir lista de cuerpos incluyendo planetas y ángulos
        bodies: list[CelestialBody] = [
            CelestialBody(p.name, p.longitude) for p in planets
        ]
        bodies.append(CelestialBody("Ascendant", ascendant_longitude))
        bodies.append(CelestialBody("Midheaven", midheaven_longitude))
        
        for first, second in combinations(bodies, 2):
            separation = angular_separation(first.longitude, second.longitude)
            
            # Calcular el multiplicador de orbe promedio entre los dos cuerpos
            multiplier_a = PLANET_ORB_MULTIPLIER.get(first.name, 1.0)
            multiplier_b = PLANET_ORB_MULTIPLIER.get(second.name, 1.0)
            avg_multiplier = (multiplier_a + multiplier_b) / 2
            
            matches = []
            for name, (exact_angle, base_max_orb) in self.aspects.items():
                # Aplicar el multiplicador dinámico al orbe base
                max_orb = base_max_orb * avg_multiplier
                orb_diff = abs(separation - exact_angle)
                if orb_diff <= max_orb:
                    matches.append((name, exact_angle, orb_diff))
            
            if matches:
                name, angle, orb = min(matches, key=lambda match: match[2])
                found.append(
                    Aspect(
                        planet_a=first.name,
                        planet_b=second.name,
                        name=name,
                        angle=angle,
                        separation=separation,
                        orb=orb,
                    )
                )
        return found
