from chart_engine.astronomy.zodiac import longitude_to_zodiac


def test_sun_in_virgo():

    result = longitude_to_zodiac(
        160.245597
    )
    print(result)

    assert result.sign == "Virgo"
    assert result.degree == 10
    assert result.minute == 14
    assert round(result.second, 2) == 44.15
 
if __name__ == "__main__":
    test_sun_in_virgo()