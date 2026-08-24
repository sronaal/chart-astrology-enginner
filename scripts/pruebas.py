from chart_engine.astronomy.ephemeris import EphemerisEngine
from chart_engine.astronomy.planets import PlanetCalculator
from chart_engine.domain.models import BirthData


def main():

    birth_data = BirthData(
        data="2001-09-02",
        time="11:02:00",
        latitude=4.7110,
        longitude=-74.0721,
        timezone="America/Bogota",
    )

    ephemeris = EphemerisEngine()

    calculator = PlanetCalculator(
        ephemeris,
    )

    planets = calculator.calculate(
        birth_data,
    )

    for planet in planets:

        print(
            f"{planet.name:10} "
            f"{planet.longitude:10.6f}° "
            f"speed={planet.speed_longitude:10.6f} "
            f"retrograde={planet.retrograde}"
        )
        
        
    


if __name__ == "__main__":
    main()