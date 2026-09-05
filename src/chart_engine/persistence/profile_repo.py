"""Profile persistence — CRUD for user_profiles table."""

from uuid import uuid4

from chart_engine.persistence.database import get_pool


async def get_profile(user_id: str) -> dict | None:
    """Get a user profile by user_id."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """
        SELECT id, user_id, age, profession, work_type, job_satisfaction,
               gender, sexual_orientation, relationship_status, children,
               living_situation, goals, interests, short_term_goal,
               created_at, updated_at
        FROM user_profiles WHERE user_id = $1
        """,
        user_id,
    )
    if not row:
        return None
    return _row_to_dict(row)


async def upsert_profile(user_id: str, data: dict) -> dict:
    """Create or update a user profile. Returns the profile."""
    pool = await get_pool()

    # Check if profile exists
    existing = await pool.fetchrow(
        "SELECT id FROM user_profiles WHERE user_id = $1",
        user_id,
    )

    if existing:
        # Build UPDATE dynamically from non-None fields
        set_clauses = []
        values = []
        idx = 1
        for key, val in data.items():
            if val is not None:
                idx += 1
                set_clauses.append(f"{key} = ${idx}")
                values.append(val)

        if not set_clauses:
            return await get_profile(user_id)

        set_clauses.append("updated_at = NOW()")
        query = f"""
            UPDATE user_profiles
            SET {', '.join(set_clauses)}
            WHERE user_id = $1
            RETURNING id, user_id, age, profession, work_type, job_satisfaction,
                      gender, sexual_orientation, relationship_status, children,
                      living_situation, goals, interests, short_term_goal,
                      created_at, updated_at
        """
        row = await pool.fetchrow(query, user_id, *values)
    else:
        profile_id = str(uuid4())
        row = await pool.fetchrow(
            """
            INSERT INTO user_profiles (id, user_id, age, profession, work_type,
                job_satisfaction, gender, sexual_orientation, relationship_status,
                children, living_situation, goals, interests, short_term_goal)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            RETURNING id, user_id, age, profession, work_type, job_satisfaction,
                      gender, sexual_orientation, relationship_status, children,
                      living_situation, goals, interests, short_term_goal,
                      created_at, updated_at
            """,
            profile_id,
            user_id,
            data.get("age"),
            data.get("profession"),
            data.get("work_type"),
            data.get("job_satisfaction"),
            data.get("gender"),
            data.get("sexual_orientation"),
            data.get("relationship_status"),
            data.get("children", 0),
            data.get("living_situation"),
            data.get("goals", []),
            data.get("interests", []),
            data.get("short_term_goal"),
        )

    return _row_to_dict(row)


async def delete_profile(user_id: str) -> None:
    """Delete a user profile (if exists)."""
    pool = await get_pool()
    await pool.execute(
        "DELETE FROM user_profiles WHERE user_id = $1",
        user_id,
    )


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "age": row["age"],
        "profession": row["profession"],
        "work_type": row["work_type"],
        "job_satisfaction": row["job_satisfaction"],
        "gender": row["gender"],
        "sexual_orientation": row["sexual_orientation"],
        "relationship_status": row["relationship_status"],
        "children": row["children"],
        "living_situation": row["living_situation"],
        "goals": row["goals"] or [],
        "interests": row["interests"] or [],
        "short_term_goal": row["short_term_goal"],
        "created_at": row["created_at"].isoformat(),
        "updated_at": row["updated_at"].isoformat(),
    }
