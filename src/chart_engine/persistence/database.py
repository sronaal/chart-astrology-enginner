"""PostgreSQL database connection."""

import json

import asyncpg

from chart_engine.config import settings

_pool: asyncpg.Pool | None = None


def _decode_json_field(value):
    """Decode a JSONB field that might come as string or already-decoded dict/list."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        async def _init_conn(conn):
            await conn.set_type_codec(
                'jsonb',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog',
            )

        _pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=2,
            max_size=10,
            init=_init_conn,
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    """Create tables if they don't exist and add missing columns."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                reset_token TEXT,
                default_chart_id TEXT REFERENCES charts(id) ON DELETE SET NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS user_profiles (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                age INTEGER,
                profession TEXT,
                work_type TEXT,
                job_satisfaction INTEGER,
                relationship_status TEXT,
                children INTEGER DEFAULT 0,
                living_situation TEXT,
                goals TEXT[],
                interests TEXT[],
                short_term_goal TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(user_id)
            );

            CREATE TABLE IF NOT EXISTS charts (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                birth_data JSONB NOT NULL,
                meta JSONB NOT NULL,
                planets JSONB NOT NULL,
                houses JSONB NOT NULL,
                ascendant JSONB NOT NULL,
                midheaven JSONB NOT NULL,
                aspects JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        # Add missing columns for existing databases
        await conn.execute("""
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS gender TEXT;
            ALTER TABLE user_profiles ADD COLUMN IF NOT EXISTS sexual_orientation TEXT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS reset_token TEXT;
            ALTER TABLE users ADD COLUMN IF NOT EXISTS default_chart_id TEXT REFERENCES charts(id) ON DELETE SET NULL;
        """)
