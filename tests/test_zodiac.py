import pytest

from chart_engine.astronomy.zodiac import longitude_to_zodiac


@pytest.mark.parametrize(
    ("longitude", "expected_sign", "expected_degree", "expected_minute", "expected_second"),
    [
        # Reference values
        (160.24559731743716, "Virgo", 10, 14, 44.150342773766645),
        (337.6608434919619, "Pisces", 7, 39, 39.0365710628286),
        (182.40549024060013, "Libra", 2, 24, 19.76486616047242),
        (127.74266936099627, "Leo", 7, 44, 33.60969958656641),
        (267.0159384788321, "Sagittarius", 27, 0, 57.378523795551945),
        # Limits and boundaries
        (0.0, "Aries", 0, 0, 0.0),
        (29.999722222222222, "Aries", 29, 59, 59.0),
        (30.0, "Taurus", 0, 0, 0.0),
        (59.999722222222222, "Taurus", 29, 59, 59.0),
        (60.0, "Gemini", 0, 0, 0.0),
        (359.9997222222222, "Pisces", 29, 59, 59.0),
        (360.0, "Aries", 0, 0, 0.0),
        # Negative normalization
        (-1.0, "Pisces", 29, 0, 0.0),
        (-360.0, "Aries", 0, 0, 0.0),
        (-361.0, "Pisces", 29, 0, 0.0),
        # Exceeding 360 normalization
        (361.0, "Aries", 1, 0, 0.0),
        (720.0, "Aries", 0, 0, 0.0),
    ],
)
def test_longitude_to_zodiac_conversion(
    longitude: float,
    expected_sign: str,
    expected_degree: int,
    expected_minute: int,
    expected_second: float,
) -> None:
    sign, degree, minute, second = longitude_to_zodiac(longitude)

    assert sign == expected_sign
    assert degree == expected_degree
    assert minute == expected_minute
    assert second == pytest.approx(expected_second, abs=1e-5)
