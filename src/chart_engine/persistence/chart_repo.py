"""Chart persistence — CRUD for charts table."""

import json
from uuid import uuid4

from chart_engine.persistence.database import get_pool


def _decode_jsonb(value):
    """Safely decode a JSONB field that may arrive as string or already-decoded object."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


def _decode_chart_row(row: dict) -> dict:
    """Decode all JSONB columns in a chart row."""
    return {
        "id": row["id"],
        "birth": _decode_jsonb(row["birth_data"]),
        "meta": _decode_jsonb(row["meta"]),
        "planets": _decode_jsonb(row["planets"]),
        "houses": _decode_jsonb(row["houses"]),
        "ascendant": _decode_jsonb(row["ascendant"]),
        "midheaven": _decode_jsonb(row["midheaven"]),
        "aspects": _decode_jsonb(row["aspects"]),
        "creada": row["created_at"].isoformat(),
    }


async def save_chart(user_id: str, birth_data: dict, meta: dict, planets: list, houses: list, ascendant: dict, midheaven: dict, aspects: list) -> str:
    """Save a chart and return its ID."""
    chart_id = str(uuid4())
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO charts (id, user_id, birth_data, meta, planets, houses, ascendant, midheaven, aspects, created_at)
        VALUES ($1, $2, $3::jsonb, $4::jsonb, $5::jsonb, $6::jsonb, $7::jsonb, $8::jsonb, $9::jsonb, NOW())
        """,
        chart_id,
        user_id,
        json.dumps(birth_data),
        json.dumps(meta),
        json.dumps(planets),
        json.dumps(houses),
        json.dumps(ascendant),
        json.dumps(midheaven),
        json.dumps(aspects),
    )
    return chart_id


async def get_charts_by_user(user_id: str) -> list[dict]:
    """Get all charts for a user (with full data for frontend rendering)."""
    pool = await get_pool()
    rows = await pool.fetch(
        """
        SELECT id, birth_data, meta, planets, houses, ascendant, midheaven, aspects, created_at
        FROM charts WHERE user_id = $1
        ORDER BY created_at DESC
        """,
        user_id,
    )
    return [_decode_chart_row(dict(row)) for row in rows]


async def get_chart_by_id(chart_id: str, user_id: str) -> dict | None:
    """Get a chart by ID, ensuring it belongs to the user."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT id, birth_data, meta, planets, houses, ascendant, midheaven, aspects, created_at
        FROM charts WHERE id = $1 AND user_id = $2
        """,
        chart_id,
        user_id,
    )
    if not row:
        return None
    return _decode_chart_row(dict(row))


async def delete_chart(chart_id: str, user_id: str) -> bool:
    """Delete a chart. Returns True if deleted."""
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM charts WHERE id = $1 AND user_id = $2",
        chart_id,
        user_id,
    )
    return result == "DELETE 1"


async def delete_charts_by_user(user_id: str) -> int:
    """Delete all charts for a user. Returns count of deleted rows."""
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM charts WHERE user_id = $1",
        user_id,
    )
    return int(result.split()[-1])
