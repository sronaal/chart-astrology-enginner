"""Profile request/response schemas."""

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    age: int | None = None
    profession: str | None = None
    work_type: str | None = None
    job_satisfaction: int | None = Field(None, ge=1, le=5)
    gender: str | None = None
    sexual_orientation: str | None = None
    relationship_status: str | None = None
    children: int = 0
    living_situation: str | None = None
    goals: list[str] = []
    interests: list[str] = []
    short_term_goal: str | None = None
    created_at: str
    updated_at: str


class ProfileUpdate(BaseModel):
    age: int | None = None
    profession: str | None = None
    work_type: str | None = None
    job_satisfaction: int | None = Field(None, ge=1, le=5)
    gender: str | None = None
    sexual_orientation: str | None = None
    relationship_status: str | None = None
    children: int | None = None
    living_situation: str | None = None
    goals: list[str] | None = None
    interests: list[str] | None = None
    short_term_goal: str | None = None
