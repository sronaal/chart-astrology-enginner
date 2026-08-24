from chart_engine.domain.models import NatalChart


PLANET_NAMES_ES = {
    "Sun": "Sol",
    "Moon": "Luna",
    "Mercury": "Mercurio",
    "Venus": "Venus",
    "Mars": "Marte",
    "Jupiter": "Júpiter",
    "Saturn": "Saturno",
    "Uranus": "Urano",
    "Neptune": "Neptuno",
    "Pluto": "Plutón"
}




def format_zodiac_position(position) -> str:
    return f"{position.zodiac.sign} {position.zodiac.degree}°{position.zodiac.minute:02d}'{int(position.zodiac.second):02d}\""


def build_chart_summary(chart: NatalChart) -> str:
    lines = []
    lines.append("DATOS DE LA CARTA NATAL:")
    lines.append(f"- Ascendente: {format_zodiac_position(chart.ascendant)}")
    lines.append(f"- Medio Cielo: {format_zodiac_position(chart.midheaven)}")
    
    # Iterar sobre TODOS los planetas automáticamente
    lines.append("\nPOSICIONES PLANETARIAS:")
    for planet in chart.planets:
        if planet.zodiac and planet.house:
            name_es = PLANET_NAMES_ES.get(planet.name, planet.name)
            retrograde_marker = " ℞" if planet.retrograde else ""
            lines.append(
                f"- {name_es}: {format_zodiac_position(planet)} en Casa {planet.house}{retrograde_marker}"
            )
    
    # Aspectos destacados
    lines.append("\nASPECTOS MAYORES DESTACADOS (Orbe <= 3°):")
    tight_aspects = sorted([a for a in chart.aspects if a.orb <= 3.0], key=lambda x: x.orb)
    
    for a in tight_aspects[:12]:
        name_a = PLANET_NAMES_ES.get(a.planet_a, a.planet_a)
        name_b = PLANET_NAMES_ES.get(a.planet_b, a.planet_b)
        lines.append(f"- {a.name.capitalize()} entre {name_a} y {name_b} (separación: {a.separation:.1f}°, orbe: {a.orb:.1f}°)")
    
    return "\n".join(lines)


def build_rag_search_queries(chart: NatalChart) -> list[str]:
    queries = []
    
    # Generar queries para TODOS los planetas
    for planet in chart.planets:
        if planet.zodiac and planet.house:
            name_es = PLANET_NAMES_ES.get(planet.name, planet.name)
            queries.append(f"{name_es} en {planet.zodiac.sign} casa {planet.house}")
            if planet.retrograde:
                queries.append(f"{name_es} retrógrado en {planet.zodiac.sign}")
    
    # Generar queries para aspectos
    for a in chart.aspects:
        if a.orb <= 2.5:
            name_a = PLANET_NAMES_ES.get(a.planet_a, a.planet_a)
            name_b = PLANET_NAMES_ES.get(a.planet_b, a.planet_b)
            queries.append(f"aspecto {a.name} {name_a} {name_b}")
    
    # Query para el Ascendente
    queries.append(f"Ascendente en {chart.ascendant.zodiac.sign}")
    
    return queries


def build_llm_system_prompt(user_query: str, chart_summary: str, rag_context: str) -> str:
    return f"""Eres un astrólogo profesional, empático y psicológico. Tu tarea es responder a la consulta del usuario basándote ÚNICAMENTE en la información proporcionada en el CONTEXTO DOCUMENTAL y los DATOS DE LA CARTA NATAL.

REGLAS ESTRICTAS:
1. No inventes posiciones planetarias, aspectos o interpretaciones que no estén explícitamente en los datos proporcionados.
2. Si el contexto documental no contiene información suficiente para responder, indícalo claramente y ofrece una interpretación general basada solo en los datos de la carta.
3. Mantén un tono profesional, constructivo y evitá el determinismo fatalista.
4. Parafrasea o cita directamente los conceptos de la base documental cuando sea relevante.

DATOS DE LA CARTA NATAL:
{chart_summary}

CONSULTA DEL USUARIO:
{user_query}

CONTEXTO DOCUMENTAL RECUPERADO:
{rag_context}
"""