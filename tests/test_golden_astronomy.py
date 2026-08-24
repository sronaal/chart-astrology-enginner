"""Golden Tests for astronomical calculations validation.

These tests validate that the Chart Engine produces correct and deterministic
astronomical results using known birth data and reference values from Swiss
Ephemeris (swisseph) library.

Reference data sources:
- Albert Einstein: March 14, 1879, 11:30 AM, Ulm, Germany
- Steve Jobs: February 24, 1955, 7:15 PM, San Francisco, CA
- Test case: September 2, 2001, 11:02 AM, Bogotá, Colombia

All longitude values are in degrees (0-360 ecliptic longitude).
Tolerances are set based on Swiss Ephemeris precision expectations.
"""

from datetime import date, time

import pytest

from chart_engine import ChartEngine
from chart_engine.domain.models import BirthData


class TestEinsteinGoldenChart:
    """Golden test suite for Albert Einstein's natal chart.
    
    Birth Data:
    - Date: March 14, 1879
    - Time: 11:30:00 (local)
    - Location: Ulm, Germany (48.398°N, 9.991°E)
    - Timezone: Europe/Berlin
    
    These values were computed using Swiss Ephemeris and represent
    the expected output of the Chart Engine.
    """
    
    @classmethod
    @pytest.fixture(scope="class")
    def einstein_chart(cls):
        """Calculate Einstein's natal chart once for all tests."""
        birth_data = BirthData(
            data=date(1879, 3, 14),
            time=time(11, 30, 0),
            latitude=48.398,
            longitude=9.991,
            timezone="Europe/Berlin",
        )
        cls._chart = ChartEngine().calculate(birth_data)
        return cls._chart
    
    def test_sun_position(self, einstein_chart):
        """Validate Sun position: should be in Pisces at ~23°."""
        sun = next(p for p in einstein_chart.planets if p.name == "Sun")
        assert sun.zodiac.sign == "Pisces"
        assert sun.longitude == pytest.approx(353.4984260312, abs=0.0001)
        assert sun.zodiac.degree == 23
        assert sun.retrograde is False
    
    def test_moon_position(self, einstein_chart):
        """Validate Moon position: should be in Sagittarius."""
        moon = next(p for p in einstein_chart.planets if p.name == "Moon")
        assert moon.zodiac.sign == "Sagittarius"
        assert moon.longitude == pytest.approx(254.3957314261, abs=0.0001)
        assert moon.zodiac.degree == 14
    
    def test_mercury_position(self, einstein_chart):
        """Validate Mercury position: should be in Aries."""
        mercury = next(p for p in einstein_chart.planets if p.name == "Mercury")
        assert mercury.zodiac.sign == "Aries"
        assert mercury.longitude == pytest.approx(3.1256300207, abs=0.0001)
        assert mercury.zodiac.degree == 3
    
    def test_venus_position(self, einstein_chart):
        """Validate Venus position: should be in Aries."""
        venus = next(p for p in einstein_chart.planets if p.name == "Venus")
        assert venus.zodiac.sign == "Aries"
        assert venus.longitude == pytest.approx(16.9734960753, abs=0.0001)
        assert venus.zodiac.degree == 16
    
    def test_mars_position(self, einstein_chart):
        """Validate Mars position: should be in Capricorn."""
        mars = next(p for p in einstein_chart.planets if p.name == "Mars")
        assert mars.zodiac.sign == "Capricorn"
        assert mars.longitude == pytest.approx(296.9074017675, abs=0.0001)
        assert mars.zodiac.degree == 26
    
    def test_jupiter_position(self, einstein_chart):
        """Validate Jupiter position: should be in Aquarius."""
        jupiter = next(p for p in einstein_chart.planets if p.name == "Jupiter")
        assert jupiter.zodiac.sign == "Aquarius"
        assert jupiter.longitude == pytest.approx(327.4818936436, abs=0.0001)
        assert jupiter.zodiac.degree == 27
    
    def test_saturn_position(self, einstein_chart):
        """Validate Saturn position: should be in Aries."""
        saturn = next(p for p in einstein_chart.planets if p.name == "Saturn")
        assert saturn.zodiac.sign == "Aries"
        assert saturn.longitude == pytest.approx(4.1886600281, abs=0.0001)
        assert saturn.zodiac.degree == 4
    
    def test_uranus_position(self, einstein_chart):
        """Validate Uranus position: should be in Virgo, retrograde."""
        uranus = next(p for p in einstein_chart.planets if p.name == "Uranus")
        assert uranus.zodiac.sign == "Virgo"
        assert uranus.longitude == pytest.approx(151.2887604654, abs=0.0001)
        assert uranus.zodiac.degree == 1
        assert uranus.retrograde is True
    
    def test_neptune_position(self, einstein_chart):
        """Validate Neptune position: should be in Taurus."""
        neptune = next(p for p in einstein_chart.planets if p.name == "Neptune")
        assert neptune.zodiac.sign == "Taurus"
        assert neptune.longitude == pytest.approx(37.8719385404, abs=0.0001)
        assert neptune.zodiac.degree == 7
    
    def test_pluto_position(self, einstein_chart):
        """Validate Pluto position: should be in Taurus."""
        pluto = next(p for p in einstein_chart.planets if p.name == "Pluto")
        assert pluto.zodiac.sign == "Taurus"
        assert pluto.longitude == pytest.approx(54.7252425208, abs=0.0001)
        assert pluto.zodiac.degree == 24
    
    def test_ascendant_position(self, einstein_chart):
        """Validate Ascendant: should be in Cancer at ~98.8°."""
        assert einstein_chart.ascendant.zodiac.sign == "Cancer"
        assert einstein_chart.ascendant.longitude == pytest.approx(98.8240852799, abs=0.0001)
    
    def test_midheaven_position(self, einstein_chart):
        """Validate Midheaven: should be in Pisces at ~339.2°."""
        assert einstein_chart.midheaven.zodiac.sign == "Pisces"
        assert einstein_chart.midheaven.longitude == pytest.approx(339.2120367259, abs=0.0001)
    
    def test_house_cusp_1(self, einstein_chart):
        """Validate 1st house cusp (Ascendant)."""
        house_1 = einstein_chart.houses[0]
        assert house_1.number == 1
        assert house_1.longitude == pytest.approx(98.8240852799, abs=0.0001)
        assert house_1.zodiac.sign == "Cancer"
    
    def test_house_cusp_10(self, einstein_chart):
        """Validate 10th house cusp (Midheaven)."""
        house_10 = einstein_chart.houses[9]
        assert house_10.number == 10
        assert house_10.longitude == pytest.approx(339.2120367259, abs=0.0001)
        assert house_10.zodiac.sign == "Pisces"
    
    def test_all_houses_present(self, einstein_chart):
        """Validate all 12 houses are present."""
        assert len(einstein_chart.houses) == 12
        house_numbers = [h.number for h in einstein_chart.houses]
        assert house_numbers == list(range(1, 13))
    
    def test_aspects_exist(self, einstein_chart):
        """Validate aspects are calculated."""
        assert len(einstein_chart.aspects) > 0


class TestSteveJobsGoldenChart:
    """Golden test suite for Steve Jobs' natal chart.
    
    Birth Data:
    - Date: February 24, 1955
    - Time: 19:15:00 (local)
    - Location: San Francisco, CA (37.7749°N, -122.4194°W)
    - Timezone: America/Los_Angeles
    
    Notable features:
    - Sun in Pisces
    - Multiple retrograde planets (Mercury, Jupiter, Uranus, Neptune, Pluto)
    """
    
    @classmethod
    @pytest.fixture(scope="class")
    def jobs_chart(cls):
        """Calculate Steve Jobs' natal chart once for all tests."""
        birth_data = BirthData(
            data=date(1955, 2, 24),
            time=time(19, 15, 0),
            latitude=37.7749,
            longitude=-122.4194,
            timezone="America/Los_Angeles",
        )
        cls._chart = ChartEngine().calculate(birth_data)
        return cls._chart
    
    def test_sun_pisces(self, jobs_chart):
        """Validate Sun in Pisces."""
        sun = next(p for p in jobs_chart.planets if p.name == "Sun")
        assert sun.zodiac.sign == "Pisces"
        assert sun.longitude == pytest.approx(335.7481395143, abs=0.0001)
        assert sun.zodiac.degree == 5
    
    def test_moon_aries(self, jobs_chart):
        """Validate Moon in Aries."""
        moon = next(p for p in jobs_chart.planets if p.name == "Moon")
        assert moon.zodiac.sign == "Aries"
        assert moon.longitude == pytest.approx(7.7471745128, abs=0.0001)
        assert moon.zodiac.degree == 7
    
    def test_mercury_retrograde(self, jobs_chart):
        """Validate Mercury retrograde in Aquarius."""
        mercury = next(p for p in jobs_chart.planets if p.name == "Mercury")
        assert mercury.zodiac.sign == "Aquarius"
        assert mercury.longitude == pytest.approx(314.3617262608, abs=0.0001)
        assert mercury.retrograde is True
    
    def test_venus_capricorn(self, jobs_chart):
        """Validate Venus in Capricorn."""
        venus = next(p for p in jobs_chart.planets if p.name == "Venus")
        assert venus.zodiac.sign == "Capricorn"
        assert venus.longitude == pytest.approx(291.1718822271, abs=0.0001)
    
    def test_mars_aries(self, jobs_chart):
        """Validate Mars in Aries."""
        mars = next(p for p in jobs_chart.planets if p.name == "Mars")
        assert mars.zodiac.sign == "Aries"
        assert mars.longitude == pytest.approx(29.0904761468, abs=0.0001)
        assert mars.zodiac.degree == 29
    
    def test_jupiter_retrograde(self, jobs_chart):
        """Validate Jupiter retrograde in Cancer."""
        jupiter = next(p for p in jobs_chart.planets if p.name == "Jupiter")
        assert jupiter.zodiac.sign == "Cancer"
        assert jupiter.longitude == pytest.approx(110.5078892374, abs=0.0001)
        assert jupiter.retrograde is True
    
    def test_saturn_scorpio(self, jobs_chart):
        """Validate Saturn in Scorpio."""
        saturn = next(p for p in jobs_chart.planets if p.name == "Saturn")
        assert saturn.zodiac.sign == "Scorpio"
        assert saturn.longitude == pytest.approx(231.1626938900, abs=0.0001)
    
    def test_uranus_retrograde(self, jobs_chart):
        """Validate Uranus retrograde in Cancer."""
        uranus = next(p for p in jobs_chart.planets if p.name == "Uranus")
        assert uranus.zodiac.sign == "Cancer"
        assert uranus.longitude == pytest.approx(114.1349056594, abs=0.0001)
        assert uranus.retrograde is True
    
    def test_neptune_retrograde(self, jobs_chart):
        """Validate Neptune retrograde in Libra."""
        neptune = next(p for p in jobs_chart.planets if p.name == "Neptune")
        assert neptune.zodiac.sign == "Libra"
        assert neptune.longitude == pytest.approx(208.0512980429, abs=0.0001)
        assert neptune.retrograde is True
    
    def test_pluto_retrograde(self, jobs_chart):
        """Validate Pluto retrograde in Leo."""
        pluto = next(p for p in jobs_chart.planets if p.name == "Pluto")
        assert pluto.zodiac.sign == "Leo"
        assert pluto.longitude == pytest.approx(145.3227882214, abs=0.0001)
        assert pluto.retrograde is True
    
    def test_ascendant_virgo(self, jobs_chart):
        """Validate Ascendant in Virgo."""
        assert jobs_chart.ascendant.zodiac.sign == "Virgo"
        assert jobs_chart.ascendant.longitude == pytest.approx(172.2912528082, abs=0.0001)
    
    def test_midheaven_gemini(self, jobs_chart):
        """Validate Midheaven in Gemini."""
        assert jobs_chart.midheaven.zodiac.sign == "Gemini"
        assert jobs_chart.midheaven.longitude == pytest.approx(81.3151149744, abs=0.0001)
    
    def test_house_system_consistency(self, jobs_chart):
        """Validate house system produces consistent oppositions."""
        # Houses 1-7, 2-8, etc. should be approximately 180° apart
        for i in range(6):
            house_a = jobs_chart.houses[i].longitude
            house_b = jobs_chart.houses[i + 6].longitude
            separation = abs((house_a - house_b) % 360 - 180)
            assert separation == pytest.approx(0, abs=0.01)


class TestBogotaStandardChart:
    """Golden test suite for standard Bogotá test case.
    
    Birth Data:
    - Date: September 2, 2001
    - Time: 11:02:00 (local)
    - Location: Bogotá, Colombia (4.609722°N, -74.081667°W)
    - Timezone: America/Bogota
    
    This is the primary reference case used throughout the test suite.
    """
    
    @classmethod
    @pytest.fixture(scope="class")
    def bogota_chart(cls):
        """Calculate Bogotá chart once for all tests."""
        birth_data = BirthData(
            data=date(2001, 9, 2),
            time=time(11, 2, 0),
            latitude=4.609722,
            longitude=-74.081667,
            timezone="America/Bogota",
        )
        cls._chart = ChartEngine().calculate(birth_data)
        return cls._chart
    
    def test_all_planets_longitudes(self, bogota_chart):
        """Validate all planet longitudes against reference values."""
        planets_dict = {p.name: p.longitude for p in bogota_chart.planets}
        
        expected_longitudes = {
            "Sun": 160.24559731743716,
            "Moon": 337.6608434919619,
            "Mercury": 182.40549024060013,
            "Venus": 127.74266936099627,
            "Mars": 267.0159384788321,
            "Jupiter": 100.22002002843766,
            "Saturn": 74.43500243814238,
            "Uranus": 322.15508492050645,
            "Neptune": 306.51846490859475,
            "Pluto": 252.56714288238058,
        }
        
        for name, expected in expected_longitudes.items():
            assert planets_dict[name] == pytest.approx(expected, abs=1e-8)
    
    def test_retrograde_planets(self, bogota_chart):
        """Validate retrograde status for all planets."""
        planets_dict = {p.name: p for p in bogota_chart.planets}
        
        # Expected retrograde planets for this date
        retrograde_expected = {"Uranus", "Neptune"}
        
        for name, planet in planets_dict.items():
            if name in retrograde_expected:
                assert planet.retrograde is True, f"{name} should be retrograde"
                assert planet.speed_longitude < 0
            else:
                assert planet.retrograde is False, f"{name} should not be retrograde"
                assert planet.speed_longitude >= 0
    
    def test_house_cusps_all(self, bogota_chart):
        """Validate all 12 house cusps against reference values."""
        expected_cusps = [
            238.839658966542,   # 1
            267.202815987659,   # 2
            295.714014153486,   # 3
            326.037951251709,   # 4
            358.152731721913,   # 5
            29.743184459779,    # 6
            58.839658966542,    # 7
            87.202815987659,    # 8
            115.714014153486,   # 9
            146.037951251709,   # 10
            178.152731721913,   # 11
            209.743184459779,   # 12
        ]
        
        for index, expected in enumerate(expected_cusps):
            assert bogota_chart.houses[index].longitude == pytest.approx(expected, abs=1e-8)
    
    def test_angles_reference(self, bogota_chart):
        """Validate Ascendant and Midheaven angles."""
        assert bogota_chart.ascendant.longitude == pytest.approx(238.839658966542, abs=1e-8)
        assert bogota_chart.midheaven.longitude == pytest.approx(146.037951251709, abs=1e-8)
    
    def test_planet_house_assignments(self, bogota_chart):
        """Validate planets are assigned to correct houses."""
        planets_dict = {p.name: p.house for p in bogota_chart.planets}
        
        expected_houses = {
            "Sun": 10,
            "Moon": 4,
            "Mercury": 11,
            "Venus": 9,
            "Mars": 1,
            "Jupiter": 8,
            "Saturn": 7,
            "Uranus": 3,
            "Neptune": 3,
            "Pluto": 1,
        }
        
        for name, expected_house in expected_houses.items():
            assert planets_dict[name] == expected_house


class TestDeterminismAndConsistency:
    """Tests to verify calculations are deterministic and consistent."""
    
    def test_same_input_same_output(self):
        """Verify identical inputs always produce identical outputs."""
        birth_data = BirthData(
            data=date(2001, 9, 2),
            time=time(11, 2, 0),
            latitude=4.609722,
            longitude=-74.081667,
            timezone="America/Bogota",
        )
        
        chart1 = ChartEngine().calculate(birth_data)
        chart2 = ChartEngine().calculate(birth_data)
        
        # Compare all planet positions
        for p1, p2 in zip(chart1.planets, chart2.planets):
            assert p1.name == p2.name
            assert p1.longitude == p2.longitude
            assert p1.latitude == p2.latitude
            assert p1.distance == p2.distance
            assert p1.retrograde == p2.retrograde
        
        # Compare houses
        for h1, h2 in zip(chart1.houses, chart2.houses):
            assert h1.longitude == h2.longitude
        
        # Compare angles
        assert chart1.ascendant.longitude == chart2.ascendant.longitude
        assert chart1.midheaven.longitude == chart2.midheaven.longitude
    
    def test_different_timezones_same_utc(self):
        """Verify same moment in different timezones produces same results."""
        # UTC time directly
        utc_birth = BirthData(
            data=date(2001, 9, 2),
            time=time(16, 2, 0),  # 11:02 AM Bogota = 16:02 UTC
            latitude=4.609722,
            longitude=-74.081667,
            timezone="UTC",
        )
        
        # Bogota local time
        bogota_birth = BirthData(
            data=date(2001, 9, 2),
            time=time(11, 2, 0),
            latitude=4.609722,
            longitude=-74.081667,
            timezone="America/Bogota",
        )
        
        chart_utc = ChartEngine().calculate(utc_birth)
        chart_bogota = ChartEngine().calculate(bogota_birth)
        
        # All planetary positions should match
        for p1, p2 in zip(chart_utc.planets, chart_bogota.planets):
            assert p1.longitude == pytest.approx(p2.longitude, abs=1e-8)
        
        # House cusps should match (same location, same time)
        for h1, h2 in zip(chart_utc.houses, chart_bogota.houses):
            assert h1.longitude == pytest.approx(h2.longitude, abs=1e-8)
