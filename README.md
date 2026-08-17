# Chart Astrology Engine

Motor Python determinista para calcular una carta natal con datos astronómicos de
[Swiss Ephemeris](https://www.astro.com/swisseph/). El proyecto calcula y
estructura los datos; no realiza interpretación astrológica mediante IA.

## Qué incluye

- Posiciones geocéntricas de Sol, Luna y planetas (longitud, latitud,
  distancia, velocidad y retrogradación).
- Posición zodiacal para planetas, cúspides y ángulos.
- Casas Placidus: las 12 cúspides, Ascendente y Medio Cielo.
- Asignación de cada planeta a una casa.
- Aspectos mayores: conjunción, sextil, cuadratura, trígono y oposición.
- API REST con FastAPI y especificación OpenAPI.

## Requisitos

- Python 3.12 o superior.
- Datos de efemérides de Swiss Ephemeris, opcionalmente configurados mediante
  `EPHEMERIS_PATH` (por defecto: `/data/ephemeris`).

## Instalación

Ejecuta estos comandos desde la raíz del repositorio, el directorio que contiene
`pyproject.toml`:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Uso como librería

```python
from chart_engine import ChartEngine
from chart_engine.domain.models import BirthData

birth_data = BirthData(
    data="2001-09-02",
    time="11:02:00",
    latitude=4.7110,
    longitude=-74.0721,
    timezone="America/Bogota",
)

chart = ChartEngine().calculate(birth_data)
chart_json = chart.model_dump(mode="json")
```

El resultado contiene esta estructura:

```text
NatalChart
├── birth_data
├── planets
├── houses
├── ascendant
├── midheaven
└── aspects
```

## Hora y zona horaria

Introduce siempre la **hora local de nacimiento**, sin sufijo `Z` ni desfase UTC.
La zona debe ser un identificador IANA válido.

```json
{
  "data": "2001-09-02",
  "time": "11:02:00",
  "latitude": 4.711,
  "longitude": -74.0721,
  "timezone": "America/Bogota"
}
```

`11:02:00Z` no es correcto para una persona nacida a las 11:02 en Bogotá: `Z`
indica que ese valor ya está expresado en UTC. El motor recibe la hora local y
debe convertirla a UTC antes de calcular el día juliano.

## API REST

Inicia el servidor:

```bash
uvicorn chart_engine.api.app:app --reload
```

Documentación interactiva:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI JSON: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

Crear una carta:

```bash
curl -X POST http://127.0.0.1:8000/charts \
  -H 'Content-Type: application/json' \
  -d '{
    "data": "2001-09-02",
    "time": "11:02:00",
    "latitude": 4.711,
    "longitude": -74.0721,
    "timezone": "America/Bogota"
  }'
```

La respuesta es un recurso JSON con el identificador y la carta:

```json
{
  "id": "uuid",
  "chart": {
    "birth_data": {},
    "planets": [],
    "houses": [],
    "ascendant": {},
    "midheaven": {},
    "aspects": []
  }
}
```

Recuperar una carta durante la vida del proceso:

```bash
curl http://127.0.0.1:8000/charts/<id>
```

Actualmente el almacén de cartas es **en memoria**; se vacía al reiniciar el
servidor. PostgreSQL corresponde a la siguiente fase de persistencia.

## Pruebas

```bash
pytest -q
```

La suite cubre cálculos de casas, límites circulares, aspectos, integración del
motor y rutas de la API.

## Arquitectura

```text
BirthData
    ↓
EphemerisEngine → Julian Day (UTC)
    ├── PlanetCalculator → posiciones y retrogradación
    ├── HouseCalculator  → Placidus, cúspides, ASC y MC
    └── AspectCalculator → aspectos mayores
    ↓
NatalChart → JSON / API REST
```

## Estado y límites actuales

- La API no incluye autenticación, usuarios ni límites de uso.
- No existe persistencia PostgreSQL todavía.
- La conversión de hora local a UTC requiere una corrección antes de usar el
  proyecto para resultados de producción; debe emplear el `datetime`
  localizado con la zona IANA recibida. Este caso debe estar cubierto con una
  prueba de regresión antes de publicar resultados astrológicos.
