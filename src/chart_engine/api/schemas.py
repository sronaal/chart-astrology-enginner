"""API request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class MessageResponse(BaseModel):
    message: str


class AuthResponse(BaseModel):
    nombre: str
    email: str
    token: str


class UserResponse(BaseModel):
    id: str
    nombre: str
    email: str
    created_at: str


# ── Charts ────────────────────────────────────────────────────────────────

class ChartBirthData(BaseModel):
    nombre: str
    fecha: str
    hora: str | None = None
    ciudad: str
    pais: str | None = None


class ChartMeta(BaseModel):
    casas: str = "Placidus"
    zodiaco: str = "Trópico"
    tz: str | None = None
    lat: float | None = None
    lon: float | None = None


class CalculateChartRequest(BaseModel):
    name: str = Field(min_length=2)
    birth_date: str
    birth_time: str | None = None
    city: str
    country: str | None = None
    latitude: float
    longitude: float
    timezone: str


class ChartSummary(BaseModel):
    id: str
    nombre: str
    fecha: str
    hora: str | None = None
    ciudad: str
    pais: str | None = None
    created_at: str


class ChartDetail(BaseModel):
    id: str
    birth: ChartBirthData
    meta: ChartMeta
    planets: list[dict]
    houses: list[dict]
    ascendant: dict
    midheaven: dict
    aspects: list[dict]
    created_at: str


class DefaultChartRequest(BaseModel):
    chart_id: str | None = None
