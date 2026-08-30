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


# Aspectos mayores con orbs base (angle, max_orb)
MAJOR_ASPECTS: dict[str, tuple[float, float]] = {
    "conjunction": (0.0, 8.0),
    "sextile": (60.0, 4.0),
    "square": (90.0, 6.0),
    "trine": (120.0, 6.0),
    "opposition": (180.0, 8.0),
}

# Aspectos menores con orbs más ajustados
MINOR_ASPECTS: dict[str, tuple[float, float]] = {
    "semisextile": (30.0, 2.0),
    "quincunx": (150.0, 2.0),
    "semisquare": (45.0, 2.0),
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

    def __init__(
        self,
        major_aspects: dict[str, tuple[float, float]] | None = None,
        minor_aspects: dict[str, tuple[float, float]] | None = None,
        include_minor_aspects: bool = False,
    ):
        self.major_aspects = major_aspects or MAJOR_ASPECTS
        self.minor_aspects = minor_aspects or MINOR_ASPECTS
        self.include_minor_aspects = include_minor_aspects

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
        
        # Combinar aspectos según configuración
        aspects_to_check = dict(self.major_aspects)
        if self.include_minor_aspects:
            aspects_to_check.update(self.minor_aspects)
        
        for first, second in combinations(bodies, 2):
            # Excluir aspecto tautológico entre Ascendente y MC
            if (first.name == "Ascendant" and second.name == "Midheaven") or \
               (first.name == "Midheaven" and second.name == "Ascendant"):
                continue
            
            separation = angular_separation(first.longitude, second.longitude)
            
            # Calcular el multiplicador de orbe promedio entre los dos cuerpos
            multiplier_a = PLANET_ORB_MULTIPLIER.get(first.name, 1.0)
            multiplier_b = PLANET_ORB_MULTIPLIER.get(second.name, 1.0)
            avg_multiplier = (multiplier_a + multiplier_b) / 2
            
            matches = []
            for name, (exact_angle, base_max_orb) in aspects_to_check.items():
                # Aplicar el multiplicador dinámico al orbe base
                max_orb = base_max_orb * avg_multiplier
                orb_diff = abs(separation - exact_angle)
                if orb_diff <= max_orb:
                    matches.append((name, exact_angle, orb_diff))
            
            if matches:
                name, angle, orb = min(matches, key=lambda match: match[2])
                found.append(
                    Aspect(
                        point_a=first.name,
                        point_b=second.name,
                        type=name,
                        angle=angle,
                        separation=separation,
                        orb=orb,
                    )
                )
        return found
