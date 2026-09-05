"""User persistence — CRUD for users table."""

from chart_engine.auth.models import User
from chart_engine.persistence.database import get_pool


async def save_user(user: User) -> None:
    pool = await get_pool()
    await pool.execute(
        """
        INSERT INTO users (id, name, email, password_hash, created_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (id) DO NOTHING
        """,
        user.id,
        user.name,
        user.email,
        user.password_hash,
        user.created_at,
    )


async def get_user_by_email(email: str) -> User | None:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id, name, email, password_hash, created_at FROM users WHERE email = $1",
        email,
    )
    if not row:
        return None
    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        password_hash=row["password_hash"],
        created_at=row["created_at"],
    )


async def delete_user(user_id: str) -> None:
    """Delete a user account."""
    pool = await get_pool()
    await pool.execute(
        "DELETE FROM users WHERE id = $1",
        user_id,
    )


async def set_reset_token(user_id: str, token_hash: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET reset_token = $1 WHERE id = $2",
        token_hash,
        user_id,
    )


async def clear_reset_token(user_id: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET reset_token = NULL WHERE id = $1",
        user_id,
    )


async def get_user_by_reset_token(token_hash: str) -> User | None:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id, name, email, password_hash, created_at FROM users WHERE reset_token = $1",
        token_hash,
    )
    if not row:
        return None
    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        password_hash=row["password_hash"],
        created_at=row["created_at"],
    )


async def update_password_hash(user_id: str, password_hash: str) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET password_hash = $1 WHERE id = $2",
        password_hash,
        user_id,
    )


async def get_user_by_id(user_id: str) -> User | None:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT id, name, email, password_hash, created_at FROM users WHERE id = $1",
        user_id,
    )
    if not row:
        return None
    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        password_hash=row["password_hash"],
        created_at=row["created_at"],
    )


async def set_default_chart(user_id: str, chart_id: str | None) -> None:
    pool = await get_pool()
    await pool.execute(
        "UPDATE users SET default_chart_id = $1 WHERE id = $2",
        chart_id,
        user_id,
    )


async def get_default_chart_id(user_id: str) -> str | None:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT default_chart_id FROM users WHERE id = $1",
        user_id,
    )
    if not row:
        return None
    return row["default_chart_id"]
