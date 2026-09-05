# Plan de Implementación — Backend Chart Engine

## Estado Real del Backend (según documentación y código)

### ✅ Ya implementado y funcionando

#### Domain Layer (`domain/`)
- **models.py**: BirthData, NatalChart, PlanetPosition, HouseCusp, Aspect, ZodiacPosition, AnglePosition, ChartAngles
- **enums.py**: Enums de soporte

#### Astronomy Layer (`astronomy/`)
- **ephemeris.py**: EphemerisEngine — cálculo de día juliano con Swiss Ephemeris
- **planets.py**: PlanetCalculator — Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, Urano, Neptuno, Plutón
- **houses.py**: HouseCalculator — Casas Placidus, ASC y MC
- **zodiac.py**: Conversión longitud eclíptica → signo zodiacal

#### Astrology Layer (`astrology/`)
- **aspects.py**: AspectCalculator — conjunción, sextil, cuadratura, trígono, oposición con orbes dinámicos
- **houses.py**: Asignación de planeta a casa

#### Services (`services/`)
- **chart_service.py**: ChartEngine — facade completo
- **context_builder.py**: 
  - `build_chart_summary()` — resumen de carta en español
  - `build_rag_search_queries()` — queries para búsqueda RAG
  - `build_llm_system_prompt()` — prompt para LLM

#### API (`api/app.py`)
- `POST /charts` — crear carta ✅
- `GET /charts/{id}` — obtener carta ✅
- `POST /chat` — preparar contexto (mock) ✅

#### Tests
- 3 tests pasan: create chart, get chart, openapi docs

### ❌ Lo que FALTA (según README)

> "La API no incluye autenticación, usuarios ni límites de uso."
> "No existe persistencia PostgreSQL todavía."

---

## Lo que el Frontend Espera (api.js)

```javascript
// Auth
POST /auth/register     → { nombre, email, token }
POST /auth/login        → { email, password, token }
GET  /auth/me           → { user }

// Charts
POST /charts            → calcular carta (YA EXISTE)
GET  /charts            → listar cartas del usuario (FALTA)
GET  /charts/:id        → obtener carta (YA EXISTE)
DELETE /charts/:id      → eliminar carta (FALTA)

// Interpretations
POST /charts/:id/interpretations/:itemId/generate (FALTA)
POST /charts/:id/interpretations/:itemId/regenerate (FALTA)

// Chat
GET  /charts/:id/chat   (FALTA)
POST /charts/:id/chat   (FALTA parcialmente)
```

---

## Plan de Implementación por Fases

### Fase 1: Schemas API (1-2 horas)
Crear `api/schemas.py` con los request/response models:

```python
# Auth schemas
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    nombre: str
    email: str
    token: str

# Chart schemas  
class ChartListResponse(BaseModel):
    charts: list[ChartResponse]

# Interpretation schemas
class InterpretRequest(BaseModel):
    item_id: str

class InterpretResponse(BaseModel):
    item_id: str
    title: str
    content: str
    sources: list[str]
```

### Fase 2: Auth con JWT (3-4 horas)

#### 2.1 Modelos de usuario
```python
# auth/models.py
class User(BaseModel):
    id: str
    name: str
    email: str
    password_hash: str
    created_at: datetime
```

#### 2.2 Servicio de auth
```python
# auth/service.py
def register(name, email, password) -> User
def login(email, password) -> str  # retorna token
def verify_token(token) -> User
```

#### 2.3 JWT
```python
# auth/jwt.py
SECRET_KEY = "tu-secreto-aqui"
ALGORITHM = "HS256"

def create_token(user_id: str) -> str
def decode_token(token: str) -> str  # retorna user_id
```

#### 2.4 Endpoints
```python
@app.post("/auth/register", response_model=AuthResponse)
@app.post("/auth/login", response_model=AuthResponse)
@app.get("/auth/me", response_model=UserResponse)
```

### Fase 3: Persistencia (2-3 horas)

#### Opción recomendada: SQLite (rápido para prototipo)

```python
# persistence/database.py
import sqlite3
from contextlib import asynccontextmanager

DATABASE_URL = "astrogyia.db"

async def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
```

#### Tablas necesarias
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE charts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    birth_data JSON NOT NULL,
    planets JSON NOT NULL,
    houses JSON NOT NULL,
    ascendant JSON NOT NULL,
    midheaven JSON NOT NULL,
    aspects JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE interpretations (
    id TEXT PRIMARY KEY,
    chart_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    content TEXT NOT NULL,
    sources JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chart_id) REFERENCES charts(id)
);
```

### Fase 4: Chart CRUD (2 horas)

```python
@app.get("/charts", response_model=list[ChartResponse])
def list_charts(current_user: User = Depends(get_current_user)):
    # Retorna cartas del usuario

@app.delete("/charts/{chart_id}")
def delete_chart(chart_id: str, current_user: User = Depends(get_current_user)):
    # Eliminar carta (solo si es del usuario)
```

### Fase 5: Interpretación con IA (4-5 horas)

#### 5.1 Servicio de interpretación
```python
# services/interpretation.py
def generate_interpretation(chart: NatalChart, item_id: str) -> Interpretation:
    # 1. Obtener posición relevante de la carta
    # 2. Buscar en RAG (libros de astrología)
    # 3. Generar prompt con context_builder
    # 4. Llamar a LLM (OpenAI/local)
    # 5. Guardar y retornar
```

#### 5.2 Items de interpretación
```python
# Mapeo item_id → posición de la carta
INTERPRETATION_ITEMS = {
    "sol_signo": lambda c: f"Sol en {c.planets[0].zodiac.sign}",
    "sol_casa": lambda c: f"Sol en Casa {c.planets[0].house}",
    "luna_signo": lambda c: f"Luna en {c.planets[1].zodiac.sign}",
    "mercurio_retro": lambda c: c.planets[2].retrograde,
    # ... más items
}
```

### Fase 6: Chat Contextual (3-4 horas)

El context_builder ya existe. Falta:
1. Integrar con RAG real (astrogyia-rag)
2. Integrar con LLM real
3. Manejar historial de chat

```python
@app.post("/charts/{chart_id}/chat", response_model=ChatResponse)
def chat(chart_id: str, request: ChatRequest):
    chart = store.get(chart_id)
    chart_summary = build_chart_summary(chart)
    rag_queries = build_rag_search_queries(chart)
    
    # Buscar en RAG
    rag_context = rag_service.search(rag_queries)
    
    # Generar respuesta con LLM
    prompt = build_llm_system_prompt(request.user_query, chart_summary, rag_context)
    response = llm_service.generate(prompt)
    
    return ChatResponse(text=response, sources=rag_context.sources)
```

---

## Dependencias a Agregar

```toml
# pyproject.toml
dependencies = [
    "fastapi",
    "pysweph",
    "pydantic",
    "pydantic-settings",
    "uvicorn",
    # Nuevas:
    "python-jose[cryptography]",  # JWT
    "passlib[bcrypt]",             # Password hashing
    "python-multipart",            # Form data
    "aiosqlite",                   # SQLite async
]
```

---

## Orden de Implementación Recomendado

| Día | Fase | Horas | Entregable |
|-----|------|-------|------------|
| 1 | Schemas + Auth models | 2h | Estructura base |
| 2 | JWT + Register/Login | 3h | Auth funcional |
| 3 | SQLite + User/Chart repos | 3h | Persistencia |
| 4 | Chart CRUD endpoints | 2h | Frontend conecta |
| 5 | Interpretación service | 4h | IA funcionando |
| 6 | Chat + RAG integration | 4h | Chat completo |
| 7 | Testing + refinamiento | 3h | Producción lista |

**Total estimado: ~21 horas**

---

## Integración con Frontend

### 1. Configurar CORS en backend
```python
# app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Frontend api.js
```javascript
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### 3. Iniciar backend
```bash
cd chart_enginner
source .venv/bin/activate
uvicorn chart_engine.api.app:app --reload --port 8000
```

---

## Preguntas para Decidir

1. **¿SQLite o PostgreSQL?** → Recomendación: SQLite para prototipo rápido
2. **¿OpenAI o LLM local?** → OpenAI para empezar (más fácil)
3. **¿RAG integration?** → Fase 6, no bloqueante para uso básico
4. **¿External auth (Google, etc.)?** → No por ahora, solo email/password

---

## Próximos Pasos Inmediatos

1. **Crear `api/schemas.py`** con todos los models
2. **Crear `auth/`** con models, service, jwt
3. **Crear `persistence/`** con database y repos
4. **Modificar `api/app.py`** para agregar auth middleware y nuevos endpoints
5. **Testing** de cada endpoint
