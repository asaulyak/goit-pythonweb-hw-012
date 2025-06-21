"""
Integration tests for authentication controller.
This module contains integration tests for all authentication-related endpoints
including login, email verification, and password management.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status
from httpx import AsyncClient


class TestAuthControllerIntegration:
    """Integration tests for authentication controller endpoints."""

    def test_login_success(self, client, mock_auth_service, sample_login_data):
        """Test successful login endpoint."""
        # Arrange
        expected_response = {
            "access_token": "test_access_token",
            "token_type": "bearer"
        }
        mock_auth_service.return_value.login.return_value = expected_response

        # Act
        response = client.post("/api/auth/login", json=sample_login_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response
        mock_auth_service.return_value.login.assert_called_once()

    def test_login_invalid_credentials(self, client, mock_auth_service, sample_login_data):
        """Test login with invalid credentials."""
        # Arrange
        from fastapi import HTTPException
        mock_auth_service.return_value.login.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

        # Act
        response = client.post("/api/auth/login", json=sample_login_data)

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Incorrect email or password"

    def test_login_missing_fields(self, client):
        """Test login with missing required fields."""
        # Act
        response = client.post("/api/auth/login", json={"email": "test@example.com"})

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_invalid_email_format(self, client, mock_contacts_repository_for_auth):
        """Test login with invalid email format."""
        # Act
        response = client.post("/api/auth/login", json={
            "email": "invalid-email",
            "password": "password123"
        })

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_verify_email_success(self, client, mock_auth_service):
        """Test successful email verification."""
        # Arrange
        verification_token = "test_verification_token"
        mock_auth_service.return_value.verify_email.return_value = None

        # Act
        response = client.get(f"/api/auth/verify/{verification_token}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.text == '"Verified"'
        mock_auth_service.return_value.verify_email.assert_called_once_with(verification_token)

    def test_verify_email_invalid_token(self, client, mock_auth_service):
        """Test email verification with invalid token."""
        # Arrange
        from fastapi import HTTPException
        verification_token = "invalid_token"
        mock_auth_service.return_value.verify_email.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification failed"
        )

        # Act
        response = client.get(f"/api/auth/verify/{verification_token}")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Verification failed"

    def test_verify_email_already_verified(self, client, mock_auth_service):
        """Test email verification for already verified email."""
        # Arrange
        from fastapi import HTTPException
        verification_token = "test_token"
        mock_auth_service.return_value.verify_email.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )

        # Act
        response = client.get(f"/api/auth/verify/{verification_token}")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Email already verified"

    def test_set_password_success(self, client, mock_auth_service, sample_password_set_data):
        """Test successful password reset."""
        # Arrange
        password_reset_token = "test_reset_token"
        mock_auth_service.return_value.set_password.return_value = None

        # Act
        response = client.post(
            f"/api/auth/set-password/{password_reset_token}",
            json=sample_password_set_data
        )

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_auth_service.return_value.set_password.assert_called_once_with(
            password_reset_token, sample_password_set_data["password"]
        )

    def test_set_password_invalid_token(self, client, mock_auth_service, sample_password_set_data):
        """Test password reset with invalid token."""
        # Arrange
        from fastapi import HTTPException
        password_reset_token = "invalid_token"
        mock_auth_service.return_value.set_password.side_effect = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )

        # Act
        response = client.post(
            f"/api/auth/set-password/{password_reset_token}",
            json=sample_password_set_data
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "Invalid reset token"

    def test_set_password_missing_password(self, client):
        """Test password reset with missing password field."""
        # Act
        response = client.post("/api/auth/set-password/test_token", json={})

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_set_password_invalid_password_format(self, client, mock_contacts_repository_for_auth):
        """Test password reset with invalid password format."""
        # Act
        response = client.post("/api/auth/set-password/test_token", json={
            "password": "short"  # Too short password
        })

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthControllerAsyncIntegration:
    """Async integration tests for authentication controller endpoints."""

    @pytest.mark.asyncio
    async def test_login_async_success(self, async_client, mock_auth_service, sample_login_data):
        """Test successful login endpoint with async client."""
        # Arrange
        expected_response = {
            "access_token": "test_access_token",
            "token_type": "bearer"
        }
        mock_auth_service.return_value.login.return_value = expected_response

        # Act
        response = await async_client.post("/api/auth/login", json=sample_login_data)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response

    @pytest.mark.asyncio
    async def test_verify_email_async_success(self, async_client, mock_auth_service):
        """Test successful email verification with async client."""
        # Arrange
        verification_token = "test_verification_token"
        mock_auth_service.return_value.verify_email.return_value = None

        # Act
        response = await async_client.get(f"/api/auth/verify/{verification_token}")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.text == '"Verified"'

    @pytest.mark.asyncio
    async def test_set_password_async_success(self, async_client, mock_auth_service, sample_password_set_data):
        """Test successful password reset with async client."""
        # Arrange
        password_reset_token = "test_reset_token"
        mock_auth_service.return_value.set_password.return_value = None

        # Act
        response = await async_client.post(
            f"/api/auth/set-password/{password_reset_token}",
            json=sample_password_set_data
        )

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestAuthControllerErrorHandling:
    """Test error handling in authentication controller."""

    def test_login_service_exception(self, client, mock_auth_service, sample_login_data):
        """Test login when service raises an exception."""
        # Arrange
        from fastapi import HTTPException
        mock_auth_service.return_value.login = AsyncMock(side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        ))

        # Act
        response = client.post("/api/auth/login", json=sample_login_data)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database error"

    def test_verify_email_service_exception(self, client, mock_auth_service):
        """Test email verification when service raises an exception."""
        # Arrange
        from fastapi import HTTPException
        mock_auth_service.return_value.verify_email = AsyncMock(side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        ))

        # Act
        response = client.get("/api/auth/verify/invalid-token")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database error"

    def test_set_password_service_exception(self, client, mock_auth_service, sample_password_set_data):
        """Test password set when service raises an exception."""
        # Arrange
        from fastapi import HTTPException
        mock_auth_service.return_value.set_password = AsyncMock(side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        ))

        # Act
        response = client.post("/api/auth/set-password/invalid-token", json=sample_password_set_data)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database error"


class TestAuthControllerValidation:
    """Test input validation in authentication controller."""

    def test_login_email_too_long(self, client):
        """Test login with email that exceeds maximum length."""
        # Act
        response = client.post("/api/auth/login", json={
            "email": "a" * 121 + "@example.com",  # 121 characters + domain
            "password": "password123"
        })

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_password_too_long(self, client):
        """Test login with password that exceeds maximum length."""
        # Act
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "a" * 251  # 251 characters
        })

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_set_password_too_long(self, client):
        """Test password reset with password that exceeds maximum length."""
        # Act
        response = client.post("/api/auth/set-password/test_token", json={
            "password": "a" * 251  # 251 characters
        })

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_verification_token_empty(self, client, mock_auth_service):
        """Test email verification with empty token."""
        # Act
        response = client.get("/api/auth/verify/")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_password_reset_token_empty(self, client, sample_password_set_data):
        """Test password reset with empty token."""
        # Act
        response = client.post("/api/auth/set-password/", json=sample_password_set_data)

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND 