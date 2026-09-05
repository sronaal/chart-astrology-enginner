"""Tests for auth and chart endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def mock_database():
    mock_pool = MagicMock()
    # In-memory user store for the mock
    _users = {}
    _user_counter = [0]

    async def mock_fetchrow(query, *args):
        if "SELECT id, name, email, password_hash, created_at FROM users WHERE email" in query:
            email = args[0]
            return _users.get(email)
        elif "SELECT id, name, email, password_hash, created_at FROM users WHERE id" in query:
            user_id = args[0]
            for u in _users.values():
                if u["id"] == user_id:
                    return u
            return None
        elif "SELECT id FROM user_profiles WHERE user_id" in query:
            return None
        elif "SELECT default_chart_id FROM users WHERE id" in query:
            return {"default_chart_id": None}
        return None

    async def mock_execute(query, *args):
        if "INSERT INTO users" in query:
            # Simulate INSERT — extract fields from args
            user_id = args[0]
            name = args[1]
            email = args[2]
            password_hash = args[3]
            created_at = args[4]
            _users[email] = {
                "id": user_id,
                "name": name,
                "email": email,
                "password_hash": password_hash,
                "created_at": created_at,
            }
            _user_counter[0] += 1
            return "INSERT 0 1"
        elif "UPDATE users SET reset_token" in query:
            return "UPDATE 1"
        elif "UPDATE users SET password_hash" in query:
            return "UPDATE 1"
        return "DELETE 0"

    mock_pool.fetchrow = mock_fetchrow
    mock_pool.fetch = AsyncMock(return_value=[])
    mock_pool.execute = mock_execute

    with patch("chart_engine.persistence.database.init_db", new_callable=AsyncMock):
        with patch("chart_engine.persistence.database.close_pool", new_callable=AsyncMock):
            with patch("chart_engine.persistence.user_repo.get_pool", return_value=mock_pool):
                with patch("chart_engine.persistence.chart_repo.get_pool", return_value=mock_pool):
                    with patch("chart_engine.persistence.profile_repo.get_pool", return_value=mock_pool):
                        yield mock_pool


@pytest.fixture
def client():
    from chart_engine.api.app import create_app

    return TestClient(create_app())


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Test User"
    assert data["email"] == "test@example.com"
    assert "token" in data


def test_login_user(client):
    # Register first
    client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Password123",
        },
    )
    # Login
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_me_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_create_chart_requires_auth(client):
    response = client.post(
        "/charts",
        json={
            "name": "Test Chart",
            "birth_date": "2001-09-02",
            "birth_time": "11:02:00",
            "city": "Bogotá",
            "country": "Colombia",
            "latitude": 4.711,
            "longitude": -74.0721,
            "timezone": "America/Bogota",
        },
    )
    assert response.status_code == 401
