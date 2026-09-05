"""Tests for security fixes — P0 validation."""

import pytest
from pydantic import ValidationError

from chart_engine.api.schemas import RegisterRequest, ResetPasswordRequest


class TestPasswordComplexity:
    """Password must have uppercase, lowercase, and digit."""

    def test_rejects_no_uppercase(self):
        with pytest.raises(ValidationError, match="mayúscula"):
            RegisterRequest(
                name="Test", email="t@t.com", password="alllower123"
            )

    def test_rejects_no_lowercase(self):
        with pytest.raises(ValidationError, match="minúscula"):
            RegisterRequest(
                name="Test", email="t@t.com", password="ALLUPPER123"
            )

    def test_rejects_no_digit(self):
        with pytest.raises(ValidationError, match="número"):
            RegisterRequest(
                name="Test", email="t@t.com", password="NoDigitsHere"
            )

    def test_rejects_too_short(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                name="Test", email="t@t.com", password="Ab1"
            )

    def test_accepts_valid_password(self):
        req = RegisterRequest(
            name="Test", email="t@t.com", password="ValidPass1"
        )
        assert req.password == "ValidPass1"

    def test_reset_password_validates_complexity(self):
        with pytest.raises(ValidationError, match="mayúscula"):
            ResetPasswordRequest(
                token="some-token", new_password="nouppercase1"
            )
