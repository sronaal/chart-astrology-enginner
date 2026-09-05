"""Auth service — register and login."""

import bcrypt

from chart_engine.auth.jwt import create_access_token
from chart_engine.auth.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


async def register_user(name: str, email: str, password: str) -> User:
    """Create a new user. Raises ValueError if email exists."""
    from chart_engine.persistence.user_repo import get_user_by_email, save_user

    existing = await get_user_by_email(email)
    if existing:
        raise ValueError("El correo ya está registrado.")

    user = User.create(name=name, email=email, password_hash=hash_password(password))
    await save_user(user)
    return user


async def login_user(email: str, password: str) -> tuple[User, str]:
    """Login and return (user, token). Raises ValueError if invalid."""
    from chart_engine.persistence.user_repo import get_user_by_email

    user = await get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Correo o contraseña incorrectos.")

    token = create_access_token(user.id)
    return user, token
