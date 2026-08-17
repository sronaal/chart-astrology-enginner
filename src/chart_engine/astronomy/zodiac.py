SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def longitude_to_zodiac(longitude: float) -> tuple[str, int, int, float]:
    """
    Convierte una longitud eclíptica de 0° a 360°
    en signo, grado, minuto y segundo.
    """

    longitude = longitude % 360

    sign_index = int(longitude // 30)

    sign = SIGNS[sign_index]

    position_in_sign = longitude % 30

    degree = int(position_in_sign)

    minutes_decimal = (
        position_in_sign - degree
    ) * 60

    minute = int(minutes_decimal)

    second = (
        minutes_decimal - minute
    ) * 60

    return (
        sign,
        degree,
        minute,
        second,
    )