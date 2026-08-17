from itertools import combinations

from chart_engine.domain.models import Aspect, PlanetPosition


ASPECTS: dict[str, tuple[float, float]] = {
    "conjunction": (0.0, 8.0),
    "sextile": (60.0, 6.0),
    "square": (90.0, 6.0),
    "trine": (120.0, 8.0),
    "opposition": (180.0, 8.0),
}


def angular_separation(first_longitude: float, second_longitude: float) -> float:
    """Return the smallest separation between two ecliptic longitudes."""
    difference = abs((first_longitude - second_longitude) % 360)
    return min(difference, 360 - difference)


class AspectCalculator:
    """Finds major Ptolemaic aspects using configurable default orbs."""

    def __init__(self, aspects: dict[str, tuple[float, float]] | None = None):
        self.aspects = aspects or ASPECTS

    def calculate(self, planets: list[PlanetPosition]) -> list[Aspect]:
        found: list[Aspect] = []
        for first, second in combinations(planets, 2):
            separation = angular_separation(first.longitude, second.longitude)
            matches = [
                (name, exact_angle, abs(separation - exact_angle))
                for name, (exact_angle, max_orb) in self.aspects.items()
                if abs(separation - exact_angle) <= max_orb
            ]
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
