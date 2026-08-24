from datetime import date as Date, time as Time

import pytest

from chart_engine.domain.models import (
    AnglePosition,
    Aspect,
    BirthData,
    NatalChart,
    PlanetPosition,
    ZodiacPosition,
)
from chart_engine.services.context_builder import (
    build_chart_summary,
    build_llm_system_prompt,
    build_rag_search_queries,
)


@pytest.fixture
def natal_chart() -> NatalChart:
    birth_data = BirthData(
        date=Date(2001, 9, 2),
        time=Time(11, 2),
        latitude=4.711,
        longitude=-74.0721,
        timezone="America/Bogota",
    )
    sun = PlanetPosition(
        name="Sun",
        longitude=160.2457,
        latitude=0.0,
        distance=1.0049,
        speed_longitude=0.9833,
        retrograde=False,
        zodiac=ZodiacPosition(sign="Virgo", degree=10, minute=14, second=44.5),
        house=11,
    )
    mercury = PlanetPosition(
        name="Mercury",
        longitude=92.4055,
        latitude=-1.2345,
        distance=0.7821,
        speed_longitude=-1.2041,
        retrograde=True,
        zodiac=ZodiacPosition(sign="Gemini", degree=2, minute=24, second=19.8),
        house=8,
    )
    ascendant = AnglePosition(
        longitude=238.8396,
        zodiac=ZodiacPosition(sign="Scorpio", degree=28, minute=50, second=22.7),
    )
    midheaven = AnglePosition(
        longitude=146.0379,
        zodiac=ZodiacPosition(sign="Leo", degree=26, minute=2, second=16.5),
    )
    tight_aspect = Aspect(
        planet_a="Sun",
        planet_b="Moon",
        name="conjunction",
        angle=0.0,
        separation=1.0,
        orb=1.0,
    )
    loose_aspect = Aspect(
        planet_a="Mars",
        planet_b="Saturn",
        name="square",
        angle=90.0,
        separation=95.0,
        orb=5.0,
    )

    return NatalChart(
        birth_data=birth_data,
        planets=[sun, mercury],
        houses=[],
        ascendant=ascendant,
        midheaven=midheaven,
        aspects=[tight_aspect, loose_aspect],
    )


def test_build_chart_summary_contains_angles_retrograde_and_only_tight_aspect(
    natal_chart: NatalChart,
) -> None:
    summary = build_chart_summary(natal_chart)

    assert "- Ascendente:" in summary
    assert "- Medio Cielo:" in summary
    assert "Mercurio:" in summary
    assert "℞" in summary
    assert "Sol:" in summary
    assert "ASPECTOS MAYORES" in summary
    assert "Conjunction entre Sol y Luna" in summary
    assert "Square entre Marte y Saturno" not in summary


def test_build_rag_search_queries_covers_planets_retrograde_aspects_and_ascendant(
    natal_chart: NatalChart,
) -> None:
    queries = build_rag_search_queries(natal_chart)

    assert "Sol en Virgo casa 11" in queries
    assert "Mercurio retrógrado en Gemini" in queries
    assert "aspecto conjunction Sol Luna" in queries
    assert all(query != "aspecto square Marte Saturno" for query in queries)
    assert "Ascendente en Scorpio" in queries


def test_build_llm_system_prompt_embeds_query_summary_and_rag_context(
    natal_chart: NatalChart,
) -> None:
    chart_summary = build_chart_summary(natal_chart)
    rag_context = "Fragmentos recuperados de la base vectorial."

    prompt = build_llm_system_prompt(
        user_query="¿Cómo evolucionará mi carrera este año?",
        chart_summary=chart_summary,
        rag_context=rag_context,
    )

    assert "¿Cómo evolucionará mi carrera este año?" in prompt
    assert chart_summary in prompt
    assert rag_context in prompt