"""Tests for auth and chart endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient


# Mock database before importing app
@pytest.fixture(autouse=True)
def mock_database():
    with patch("chart_engine.persistence.database.init_db", new_callable=AsyncMock):
        with patch("chart_engine.persistence.database.close_pool", new_callable=AsyncMock):
            with patch("chart_engine.persistence.database.get_conn") as mock_conn:
                # Mock connection context manager
                mock_connection = AsyncMock()
                mock_conn.return_value.__aenter__ = AsyncMock(return_value=mock_connection)
                mock_conn.return_value.__aexit__ = AsyncMock(return_value=False)
                yield mock_connection


@pytest.fixture
def client():
    from chart_engine.api.app import create_app
    return TestClient(create_app())


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={"name": "Test User", "email": "test@example.com", "password": "password123"},
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
        json={"name": "Test User", "email": "test@example.com", "password": "password123"},
    )
    # Login
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    assert "token" in response.json()


def test_me_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 403  # No token


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
    assert response.status_code == 403
