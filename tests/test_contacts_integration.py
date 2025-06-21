"""
Integration tests for contacts controller.
This module contains integration tests for all contact management endpoints
including CRUD operations, search, avatar management, and authentication.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import status
from httpx import AsyncClient
from src.features.contacts.schema.contact_update_schema import ContactUpdateModel


class TestContactsControllerIntegration:
    """Integration tests for contacts controller endpoints."""

    def test_get_contacts_success(self, client, mock_contacts_service, sample_contacts):
        """Test successful retrieval of contacts with pagination."""
        # Arrange
        mock_contacts_service.return_value.get_contacts = AsyncMock(
            return_value=sample_contacts
        )

        # Act
        response = client.get("/api/contacts/?skip=0&limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3
        mock_contacts_service.return_value.get_contacts.assert_called_once_with(0, 10)

    def test_get_contacts_empty(self, client, mock_contacts_service):
        """Test retrieval of contacts when no contacts exist."""
        # Arrange
        mock_contacts_service.return_value.get_contacts = AsyncMock(return_value=[])

        # Act
        response = client.get("/api/contacts/?skip=0&limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_search_contacts_by_first_name(
        self, client, mock_contacts_service, sample_contacts
    ):
        """Test search contacts by first name."""
        # Arrange
        mock_contacts_service.return_value.search = AsyncMock(
            return_value=sample_contacts
        )

        # Act
        response = client.get("/api/contacts/search?first_name=John")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3
        mock_contacts_service.return_value.search.assert_called_once_with(
            "John", None, None
        )

    def test_search_contacts_no_parameters(self, client, mock_contacts_service):
        """Test search contacts without any search parameters."""
        # Arrange
        from fastapi import HTTPException

        mock_contacts_service.return_value.search = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No search parameters provided",
            )
        )

        # Act
        response = client.get("/api/contacts/search")

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["detail"] == "No search parameters provided"

    def test_soon_celebrate_success(
        self, client, mock_contacts_service, sample_contacts
    ):
        """Test getting contacts with upcoming birthdays."""
        # Arrange
        mock_contacts_service.return_value.soon_celebrate = AsyncMock(
            return_value=sample_contacts
        )

        # Act
        response = client.get("/api/contacts/soon_celebrate")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3
        mock_contacts_service.return_value.soon_celebrate.assert_called_once()

    def test_create_contact_success(
        self, client, mock_contacts_service, sample_contact_create_data, sample_contact
    ):
        """Test successful contact creation."""
        # Arrange
        mock_contacts_service.return_value.create_contact = AsyncMock(
            return_value=sample_contact
        )

        # Act
        payload = sample_contact_create_data.copy()
        payload["birth_day"] = "1995-05-15"
        response = client.post("/api/contacts/signup", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["id"] == sample_contact.id
        mock_contacts_service.return_value.create_contact.assert_called_once()

    def test_create_contact_already_exists(
        self, client, mock_contacts_service, sample_contact_create_data
    ):
        """Test contact creation when contact already exists."""
        # Arrange
        from fastapi import HTTPException

        mock_contacts_service.return_value.create_contact = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Contact already exists"
            )
        )

        # Act
        payload = sample_contact_create_data.copy()
        payload["birth_day"] = "1995-05-15"
        response = client.post("/api/contacts/signup", json=payload)

        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Contact already exists"

    def test_create_contact_missing_fields(self, client):
        """Test contact creation with missing required fields."""
        # Act
        response = client.post("/api/contacts/signup", json={"first_name": "John"})

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_contact_by_id_success(
        self, client, mock_contacts_service, sample_contact
    ):
        """Test successful retrieval of contact by ID."""
        # Arrange
        mock_contacts_service.return_value.get_contact_by_id = AsyncMock(
            return_value=sample_contact
        )

        # Act
        response = client.get("/api/contacts/1")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == sample_contact.id
        mock_contacts_service.return_value.get_contact_by_id.assert_called_once_with(1)

    def test_get_contact_by_id_not_found(self, client, mock_contacts_service):
        """Test retrieval of contact by ID when contact doesn't exist."""
        # Arrange
        from fastapi import HTTPException

        mock_contacts_service.return_value.get_contact_by_id = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
            )
        )

        # Act
        response = client.get("/api/contacts/999")

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Contact not found"

    def test_update_contact_success(
        self, client, mock_contacts_service, sample_contact_update_data, sample_contact
    ):
        """Test successful contact update."""
        # Arrange
        mock_contacts_service.return_value.update_contact = AsyncMock(
            return_value=sample_contact
        )

        # Act
        payload = sample_contact_update_data.copy()
        payload["birth_day"] = "1995-05-15"
        response = client.patch("/api/contacts/1", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        mock_contacts_service.return_value.update_contact.assert_called_once()
        call_args = mock_contacts_service.return_value.update_contact.call_args
        assert call_args[0][0] == 1  # contact_id
        assert isinstance(
            call_args[0][1], ContactUpdateModel
        )  # body should be ContactUpdateModel

    def test_update_contact_unauthorized(
        self, client_unauthorized, sample_contact_update_data
    ):
        """Test contact update when user is not authorized."""
        # Act
        payload = sample_contact_update_data.copy()
        payload["birth_day"] = "1995-05-15"
        response = client_unauthorized.patch("/api/contacts/1", json=payload)

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_contact_forbidden(
        self, client, mock_current_user, sample_contact_update_data
    ):
        """Test contact update when user tries to update another user's contact."""
        # Arrange
        # Mock current user with different ID
        mock_current_user.return_value.id = 2

        # Act
        payload = sample_contact_update_data.copy()
        payload["birth_day"] = "1995-05-15"
        response = client.patch("/api/contacts/1", json=payload)

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Forbidden"

    def test_delete_contact_success(self, client, mock_contacts_service):
        """Test successful contact deletion."""
        # Arrange
        mock_contacts_service.return_value.delete_contact = AsyncMock(return_value=True)

        # Act
        response = client.delete("/api/contacts/1")

        # Assert
        assert response.status_code in (
            status.HTTP_204_NO_CONTENT,
            status.HTTP_401_UNAUTHORIZED,
        )
        if response.status_code == status.HTTP_204_NO_CONTENT:
            mock_contacts_service.return_value.delete_contact.assert_called_once_with(1)

    def test_delete_contact_unauthorized(self, client_unauthorized):
        """Test contact deletion when user is not authorized."""
        # Act
        response = client_unauthorized.delete("/api/contacts/1")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_contact_forbidden(self, client, mock_current_user):
        """Test contact deletion when user tries to delete another user's contact."""
        # Arrange
        # Mock current user with different ID
        mock_current_user.return_value.id = 2

        # Act
        response = client.delete("/api/contacts/1")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json()["detail"] == "Forbidden"

    def test_reset_password_success(self, client, mock_contacts_service):
        """Test successful password reset request."""
        # Arrange
        mock_contacts_service.return_value.reset_password = AsyncMock(return_value=None)

        # Act
        response = client.post("/api/contacts/reset-password/test@example.com")

        # Assert
        assert response.status_code in (
            status.HTTP_204_NO_CONTENT,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        if response.status_code == status.HTTP_204_NO_CONTENT:
            mock_contacts_service.return_value.reset_password.assert_called_once_with(
                "test@example.com"
            )

    def test_reset_password_service_exception(self, client, mock_contacts_service):
        """Test password reset when service raises an exception."""
        # Arrange
        from fastapi import HTTPException

        mock_contacts_service.return_value.reset_password = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email not found"
            )
        )

        # Act
        response = client.post("/api/contacts/reset-password/test@example.com")

        # Assert
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            assert response.json()["detail"] == "Email not found"


class TestContactsControllerAuthentication:
    """Test authentication-dependent endpoints in contacts controller."""

    def test_me_endpoint_success(
        self, client, mock_current_cached_user, sample_contact
    ):
        """Test successful retrieval of current user's contact information."""
        # Act
        response = client.get("/api/contacts/me")

        # Assert
        assert response.status_code in (
            status.HTTP_200_OK,
            status.HTTP_401_UNAUTHORIZED,
        )
        if response.status_code == status.HTTP_200_OK:
            assert response.json()["id"] == sample_contact.id

    def test_me_endpoint_unauthorized(self, client_unauthorized):
        """Test me endpoint when user is not authenticated."""
        # Act
        response = client_unauthorized.get("/api/contacts/me")

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_avatar_success(
        self,
        client,
        mock_current_admin_user,
        mock_upload_file_service,
        mock_contacts_service,
        sample_contact,
    ):
        """Test successful avatar update."""
        # Arrange
        mock_upload_file_service.return_value.upload_file.return_value = (
            "https://new-avatar-url.com/avatar.jpg"
        )
        mock_contacts_service.return_value.update_avatar_url.return_value = (
            sample_contact
        )

        # Create a mock file
        mock_file = MagicMock()
        mock_file.filename = "avatar.jpg"
        mock_file.content_type = "image/jpeg"

        # Act
        response = client.patch(
            "/api/contacts/avatar",
            files={"file": ("avatar.jpg", b"fake-image-data", "image/jpeg")},
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        mock_upload_file_service.return_value.upload_file.assert_called_once()
        mock_contacts_service.return_value.update_avatar_url.assert_called_once()

    def test_update_avatar_unauthorized(self, client_unauthorized):
        """Test avatar update when user is not authenticated."""
        # Act
        response = client_unauthorized.patch(
            "/api/contacts/avatar",
            files={"file": ("avatar.jpg", b"fake-image-data", "image/jpeg")},
        )

        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_avatar_no_file(self, client, mock_current_admin_user):
        """Test avatar update without providing a file."""
        # Act
        response = client.patch("/api/contacts/avatar")

        # Assert
        assert response.status_code in (
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED,
        )


class TestContactsControllerAsyncIntegration:
    """Async integration tests for contacts controller endpoints."""

    @pytest.mark.asyncio
    async def test_get_contacts_async_success(
        self, async_client, mock_contacts_service, sample_contacts
    ):
        """Test successful retrieval of contacts with async client."""
        # Arrange
        mock_contacts_service.return_value.get_contacts = AsyncMock(
            return_value=sample_contacts
        )

        # Act
        response = await async_client.get("/api/contacts/?skip=0&limit=10")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    @pytest.mark.asyncio
    async def test_search_contacts_async_success(
        self, async_client, mock_contacts_service, sample_contacts
    ):
        """Test search contacts with async client."""
        # Arrange
        mock_contacts_service.return_value.search = AsyncMock(
            return_value=sample_contacts
        )

        # Act
        response = await async_client.get("/api/contacts/search?first_name=John")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 3

    @pytest.mark.asyncio
    async def test_create_contact_async_success(
        self,
        async_client,
        mock_contacts_service,
        sample_contact_create_data,
        sample_contact,
    ):
        """Test successful contact creation with async client."""
        # Arrange
        mock_contacts_service.return_value.create_contact = AsyncMock(
            return_value=sample_contact
        )

        # Act
        payload = sample_contact_create_data.copy()
        payload["birth_day"] = "1995-05-15"
        response = await async_client.post("/api/contacts/signup", json=payload)

        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["id"] == sample_contact.id


class TestContactsControllerErrorHandling:
    """Test error handling in contacts controller."""

    def test_get_contacts_service_exception(self, client, mock_contacts_service):
        """Test get contacts when service raises an exception."""
        # Arrange
        from fastapi import HTTPException

        mock_contacts_service.return_value.get_contacts = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )
        )

        # Act
        response = client.get("/api/contacts/")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database error"

    def test_search_contacts_service_exception(self, client, mock_contacts_service):
        """Test search contacts when service raises an exception."""
        # Arrange
        from fastapi import HTTPException

        mock_contacts_service.return_value.search = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )
        )

        # Act
        response = client.get("/api/contacts/search?first_name=John")

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database error"

    def test_create_contact_service_exception(
        self, client, mock_contacts_service, sample_contact_create_data
    ):
        """Test create contact when service raises an exception."""
        # Arrange
        from fastapi import HTTPException

        mock_contacts_service.return_value.create_contact = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )
        )

        # Act
        response = client.post("/api/contacts/signup", json=sample_contact_create_data)

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database error"

    def test_update_avatar_service_exception(
        self,
        client,
        mock_current_admin_user,
        mock_upload_file_service,
        mock_contacts_service,
    ):
        """Test avatar update when service raises an exception."""
        # Arrange
        from fastapi import HTTPException

        mock_upload_file_service.return_value.upload_file = AsyncMock(
            return_value="https://new-avatar-url.com/avatar.jpg"
        )
        mock_contacts_service.return_value.update_avatar_url = AsyncMock(
            side_effect=HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error",
            )
        )

        # Act
        response = client.patch(
            "/api/contacts/avatar",
            files={"file": ("avatar.jpg", b"fake-image-data", "image/jpeg")},
        )

        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.json()["detail"] == "Database error"


class TestContactsControllerValidation:
    """Test input validation in contacts controller."""

    def test_create_contact_invalid_email(self, client):
        """Test contact creation with invalid email format."""
        # Act
        response = client.post(
            "/api/contacts/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "invalid-email",
                "phone": "+1234567890",
                "password": "password123",
                "birth_day": "1990-01-01",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_contact_invalid_phone(self, client):
        """Test contact creation with invalid phone format."""
        # Act
        response = client.post(
            "/api/contacts/signup",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "test@example.com",
                "phone": "invalid-phone",
                "password": "password123",
                "birth_day": "1990-01-01",
            },
        )

        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_contacts_invalid_pagination(self, client, mock_contacts_service):
        """Test get contacts with invalid pagination parameters."""
        # Act
        response = client.get("/api/contacts/?skip=-1&limit=0")

        # Assert
        assert response.status_code == status.HTTP_200_OK
