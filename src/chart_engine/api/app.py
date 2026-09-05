"""FastAPI application — auth + chart CRUD."""

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from chart_engine.auth.jwt import create_reset_token, decode_reset_token, decode_token
from chart_engine.auth.models import User
from chart_engine.auth.service import hash_password, login_user, register_user, verify_password
from chart_engine.config import settings
from chart_engine.domain.models import BirthData, NatalChart
from chart_engine.persistence import chart_repo, database, profile_repo, user_repo
from chart_engine.services.chart_service import ChartEngine

from .profile_schemas import ProfileResponse, ProfileUpdate
from .schemas import (
    AuthResponse,
    CalculateChartRequest,
    ChartDetail,
    DefaultChartRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserResponse,
)


# ── Security ──────────────────────────────────────────────────────────────

security = HTTPBearer(auto_error=False)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    user_id = decode_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return user


# ── App Factory ───────────────────────────────────────────────────────────

def create_app(
    engine_factory: Callable[[], ChartEngine] = ChartEngine,
) -> FastAPI:
    app = FastAPI(
        title="AstrogyIA API",
        version="0.2.0",
        description="Natal chart calculation engine with auth and persistence.",
    )

    # Rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # CORS (from config)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Startup / Shutdown ────────────────────────────────────────────

    @app.on_event("startup")
    async def startup():
        await database.init_db()

    @app.on_event("shutdown")
    async def shutdown():
        await database.close_pool()

    # ── Health Check ──────────────────────────────────────────────────

    @app.get("/health", tags=["health"])
    @limiter.exempt
    async def health_check():
        try:
            pool = await database.get_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return {"status": "ok", "database": "connected"}
        except Exception as e:
            return {"status": "error", "database": str(e)}

    # ── Auth Endpoints ────────────────────────────────────────────────

    @app.post("/auth/register", response_model=AuthResponse, tags=["auth"])
    @limiter.limit("5/minute")
    async def register(request: Request, req: RegisterRequest):
        try:
            user = await register_user(req.name, req.email, req.password)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        _, token = await login_user(req.email, req.password)
        return AuthResponse(nombre=user.name, email=user.email, token=token)

    @app.post("/auth/login", response_model=AuthResponse, tags=["auth"])
    @limiter.limit("5/minute")
    async def login(request: Request, req: LoginRequest):
        try:
            user, token = await login_user(req.email, req.password)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=str(e))

        return AuthResponse(nombre=user.name, email=user.email, token=token)

    @app.post("/auth/forgot-password", response_model=MessageResponse, tags=["auth"])
    @limiter.limit("3/minute")
    async def forgot_password(request: Request, req: ForgotPasswordRequest):
        user = await user_repo.get_user_by_email(req.email)
        if user:
            token = create_reset_token(user.id)
            print(f"[PASSWORD RESET] Email: {req.email}, Token: {token}")

        return MessageResponse(
            message="Si el email está registrado, recibirás un enlace de recuperación."
        )

    @app.post("/auth/reset-password", response_model=MessageResponse, tags=["auth"])
    @limiter.limit("5/minute")
    async def reset_password(request: Request, req: ResetPasswordRequest):
        user_id = decode_reset_token(req.token)
        if not user_id:
            raise HTTPException(
                status_code=400, detail="Token inválido o expirado."
            )

        user = await user_repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=400, detail="Token inválido o expirado."
            )

        hashed = hash_password(req.new_password)
        await user_repo.update_password_hash(user_id, hashed)
        await user_repo.clear_reset_token(user_id)

        return MessageResponse(message="Contraseña actualizada correctamente.")

    @app.get("/auth/me", response_model=UserResponse, tags=["auth"])
    async def me(current_user: User = Depends(get_current_user)):
        return UserResponse(
            id=current_user.id,
            nombre=current_user.name,
            email=current_user.email,
            created_at=current_user.created_at.isoformat(),
        )

    # ── Chart Endpoints ───────────────────────────────────────────────

    @app.post("/charts", response_model=dict, status_code=201, tags=["charts"])
    @limiter.limit("20/minute")
    async def create_chart(
        request: Request,
        req: CalculateChartRequest,
        current_user: User = Depends(get_current_user),
    ):
        # Build BirthData for the engine
        birth_data = BirthData(
            data=req.birth_date,
            time=req.birth_time or "12:00:00",
            latitude=req.latitude,
            longitude=req.longitude,
            timezone=req.timezone,
        )

        chart = engine_factory().calculate(birth_data)

        # Map to frontend format
        birth = {
            "nombre": req.name,
            "fecha": req.birth_date,
            "hora": req.birth_time,
            "ciudad": req.city,
            "pais": req.country,
        }
        meta = {
            "casas": "Placidus",
            "zodiaco": "Trópico",
            "tz": req.timezone,
            "lat": req.latitude,
            "lon": req.longitude,
        }

        # Convert chart to JSON-serializable dicts
        planets = [p.model_dump(mode="json") for p in chart.planets]
        houses = [h.model_dump(mode="json") for h in chart.houses]
        ascendant = chart.ascendant.model_dump(mode="json")
        midheaven = chart.midheaven.model_dump(mode="json")
        aspects = [a.model_dump(mode="json") for a in chart.aspects]

        chart_id = await chart_repo.save_chart(
            user_id=current_user.id,
            birth_data=birth,
            meta=meta,
            planets=planets,
            houses=houses,
            ascendant=ascendant,
            midheaven=midheaven,
            aspects=aspects,
        )

        return {
            "id": chart_id,
            "birth": birth,
            "meta": meta,
            "planets": planets,
            "houses": houses,
            "ascendant": ascendant,
            "midheaven": midheaven,
            "aspects": aspects,
            "creada": datetime.utcnow().strftime("%d %b %Y"),
        }

    @app.get("/charts", response_model=list[dict], tags=["charts"])
    @limiter.limit("20/minute")
    async def list_charts(request: Request, current_user: User = Depends(get_current_user)):
        charts = await chart_repo.get_charts_by_user(current_user.id)
        default_id = await user_repo.get_default_chart_id(current_user.id)
        for chart in charts:
            chart["is_default"] = chart["id"] == default_id
        return charts

    @app.get("/charts/{chart_id}", response_model=dict, tags=["charts"])
    async def get_chart(
        chart_id: str,
        current_user: User = Depends(get_current_user),
    ):
        chart = await chart_repo.get_chart_by_id(chart_id, current_user.id)
        if not chart:
            raise HTTPException(status_code=404, detail="Carta no encontrada")
        default_id = await user_repo.get_default_chart_id(current_user.id)
        chart["is_default"] = chart["id"] == default_id
        return chart

    @app.delete("/charts/{chart_id}", status_code=204, tags=["charts"])
    async def delete_chart(
        chart_id: str,
        current_user: User = Depends(get_current_user),
    ):
        deleted = await chart_repo.delete_chart(chart_id, current_user.id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Carta no encontrada")

    # ── Default Chart Endpoints ────────────────────────────────────

    @app.put("/users/default-chart", response_model=dict, tags=["charts"])
    async def set_default_chart(
        req: DefaultChartRequest,
        current_user: User = Depends(get_current_user),
    ):
        if req.chart_id is not None:
            chart = await chart_repo.get_chart_by_id(req.chart_id, current_user.id)
            if not chart:
                raise HTTPException(status_code=404, detail="Carta no encontrada")
            await user_repo.set_default_chart(current_user.id, req.chart_id)
        else:
            await user_repo.set_default_chart(current_user.id, None)
        return {"default_chart_id": req.chart_id}

    @app.get("/users/default-chart", response_model=dict, tags=["charts"])
    async def get_default_chart(
        current_user: User = Depends(get_current_user),
    ):
        default_id = await user_repo.get_default_chart_id(current_user.id)
        if not default_id:
            return {"default_chart_id": None, "chart": None}
        chart = await chart_repo.get_chart_by_id(default_id, current_user.id)
        if not chart:
            await user_repo.set_default_chart(current_user.id, None)
            return {"default_chart_id": None, "chart": None}
        chart["is_default"] = True
        return {"default_chart_id": default_id, "chart": chart}

    # ── Profile Endpoints ─────────────────────────────────────────────

    @app.get("/profile", response_model=ProfileResponse, tags=["profile"])
    async def get_profile(current_user: User = Depends(get_current_user)):
        profile = await profile_repo.get_profile(current_user.id)
        if not profile:
            raise HTTPException(status_code=404, detail="Perfil no encontrado")
        return profile

    @app.put("/profile", response_model=ProfileResponse, tags=["profile"])
    async def upsert_profile(
        req: ProfileUpdate,
        current_user: User = Depends(get_current_user),
    ):
        data = req.model_dump(exclude_unset=True)
        profile = await profile_repo.upsert_profile(current_user.id, data)
        return profile

    @app.get("/profile/age", tags=["profile"])
    async def get_age(current_user: User = Depends(get_current_user)):
        """Calculate age from the user's stored birth_date in charts."""
        from datetime import date

        charts = await chart_repo.get_charts_by_user(current_user.id)
        if not charts:
            raise HTTPException(status_code=404, detail="No hay cartas natales para calcular la edad")

        # Use the most recent chart's birth date
        birth_data = charts[0].get("birth", {})
        fecha = birth_data.get("fecha")
        if not fecha:
            raise HTTPException(status_code=400, detail="Fecha de nacimiento no encontrada en la carta")

        try:
            birth_date = date.fromisoformat(fecha)
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            return {"age": age, "birth_date": fecha}
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido")

    # ── GDPR Endpoints ───────────────────────────────────────────────

    @app.get("/profile/export", tags=["profile"])
    async def export_profile(current_user: User = Depends(get_current_user)):
        profile = await profile_repo.get_profile(current_user.id)
        charts = await chart_repo.get_charts_by_user(current_user.id)

        return {
            "user": {
                "id": str(current_user.id),
                "name": current_user.name,
                "email": current_user.email,
                "created_at": current_user.created_at.isoformat(),
            },
            "profile": profile,
            "charts": charts,
            "exported_at": datetime.utcnow().isoformat(),
        }

    @app.delete("/profile", status_code=200, tags=["profile"])
    async def delete_account(current_user: User = Depends(get_current_user)):
        pool = await database.get_pool()
        async with pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "DELETE FROM charts WHERE user_id = $1",
                    current_user.id,
                )
                await conn.execute(
                    "DELETE FROM user_profiles WHERE user_id = $1",
                    current_user.id,
                )
                await conn.execute(
                    "DELETE FROM users WHERE id = $1",
                    current_user.id,
                )
        return {"deleted": True}

    return app


app = create_app()
