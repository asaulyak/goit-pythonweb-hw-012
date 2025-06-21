import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date, timedelta
from sqlalchemy import select

from src.auth.contacts_repository import ContactsRepository
from src.database.models.contacts_model import Contact, UserRole
from src.auth.contact_schema import ContactModel
from src.features.contacts.schema.contact_update_schema import ContactUpdateModel


class TestContactsRepository:
    """Test cases for ContactsRepository class."""

    @pytest.mark.asyncio
    async def test_get_contacts_success(self, contacts_repository, mock_session, sample_contacts, mock_execute_result_with_contacts):
        """Test successful retrieval of contacts with pagination."""
        # Arrange
        skip, limit = 0, 10
        mock_session.execute.return_value = mock_execute_result_with_contacts

        # Act
        result = await contacts_repository.get_contacts(skip, limit)

        # Assert
        assert result == sample_contacts
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contacts_empty(self, contacts_repository, mock_session, mock_execute_result):
        """Test retrieval of contacts when no contacts exist."""
        # Arrange
        skip, limit = 0, 10
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.get_contacts(skip, limit)

        # Assert
        assert result == []
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_by_id_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful retrieval of contact by ID."""
        # Arrange
        contact_id = 1
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.get_contact_by_id(contact_id)

        # Assert
        assert result == sample_contact
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_by_id_not_found(self, contacts_repository, mock_session, mock_execute_result):
        """Test retrieval of contact by ID when contact doesn't exist."""
        # Arrange
        contact_id = 999
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.get_contact_by_id(contact_id)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_contact_by_first_name(self, contacts_repository, mock_session, sample_contacts, mock_execute_result_with_contacts):
        """Test search contact by first name."""
        # Arrange
        first_name = "John"
        mock_session.execute.return_value = mock_execute_result_with_contacts

        # Act
        result = await contacts_repository.search_contact(first_name=first_name, last_name=None, email=None)

        # Assert
        assert result == sample_contacts
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_contact_by_last_name(self, contacts_repository, mock_session, sample_contacts, mock_execute_result_with_contacts):
        """Test search contact by last name."""
        # Arrange
        last_name = "Doe"
        mock_session.execute.return_value = mock_execute_result_with_contacts

        # Act
        result = await contacts_repository.search_contact(first_name=None, last_name=last_name, email=None)

        # Assert
        assert result == sample_contacts
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_contact_by_email(self, contacts_repository, mock_session, sample_contacts, mock_execute_result_with_contacts):
        """Test search contact by email."""
        # Arrange
        email = "john.doe@example.com"
        mock_session.execute.return_value = mock_execute_result_with_contacts

        # Act
        result = await contacts_repository.search_contact(first_name=None, last_name=None, email=email)

        # Assert
        assert result == sample_contacts
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_contact_with_all_filters(self, contacts_repository, mock_session, sample_contacts, mock_execute_result_with_contacts):
        """Test search contact with all filters applied."""
        # Arrange
        first_name = "John"
        last_name = "Doe"
        email = "john.doe@example.com"
        mock_session.execute.return_value = mock_execute_result_with_contacts

        # Act
        result = await contacts_repository.search_contact(first_name, last_name, email)

        # Assert
        assert result == sample_contacts
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_by_email_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful retrieval of contact by email."""
        # Arrange
        email = "john.doe@example.com"
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.get_contact_by_email(email)

        # Assert
        assert result == sample_contact
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_by_email_not_found(self, contacts_repository, mock_session, mock_execute_result):
        """Test retrieval of contact by email when contact doesn't exist."""
        # Arrange
        email = "nonexistent@example.com"
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.get_contact_by_email(email)

        # Assert
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_by_reset_password_token_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful retrieval of contact by reset password token."""
        # Arrange
        token = "test_reset_token"
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.get_contact_by_reset_password_token(token)

        # Assert
        assert result == sample_contact
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_by_verification_token_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful retrieval of contact by verification token."""
        # Arrange
        token = "test_verification_token"
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.get_contact_by_verification_token(token)

        # Assert
        assert result == sample_contact
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_contact_success(self, contacts_repository, mock_session, contact_model, sample_contact, mock_execute_result_with_contact):
        """Test successful creation of a new contact."""
        # Arrange
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.create_contact(contact_model)

        # Assert
        assert result == sample_contact
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_contact_success(self, contacts_repository, mock_session, contact_update_model, sample_contact, mock_execute_result_with_contact):
        """Test successful update of an existing contact."""
        # Arrange
        contact_id = 1
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.update_contact(contact_id, contact_update_model)

        # Assert
        assert result == sample_contact
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_contact_not_found(self, contacts_repository, mock_session, contact_update_model, mock_execute_result):
        """Test update of contact when contact doesn't exist."""
        # Arrange
        contact_id = 999
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.update_contact(contact_id, contact_update_model)

        # Assert
        assert result is None
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_contact_partial_fields(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test update of contact with only some fields provided."""
        # Arrange
        contact_id = 1
        update_model = ContactUpdateModel(first_name="Updated")
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.update_contact(contact_id, update_model)

        # Assert
        assert result == sample_contact
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_contact_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful deletion of a contact."""
        # Arrange
        contact_id = 1
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.delete_contact(contact_id)

        # Assert
        assert result == sample_contact
        mock_session.delete.assert_called_once_with(sample_contact)
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_contact_not_found(self, contacts_repository, mock_session, mock_execute_result):
        """Test deletion of contact when contact doesn't exist."""
        # Arrange
        contact_id = 999
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.delete_contact(contact_id)

        # Assert
        assert result is None
        mock_session.delete.assert_not_called()
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_bd_soon_same_month(self, contacts_repository, mock_session, sample_contacts, mock_execute_result_with_contacts):
        """Test birthday search for contacts with birthdays in the same month."""
        # Arrange
        days = 7
        mock_session.execute.return_value = mock_execute_result_with_contacts

        # Act
        result = await contacts_repository.bd_soon(days)

        # Assert
        assert result == sample_contacts
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_bd_soon_next_month(self, contacts_repository, mock_session, sample_contacts, mock_execute_result_with_contacts):
        """Test birthday search for contacts with birthdays in the next month."""
        # Arrange
        days = 30
        mock_session.execute.return_value = mock_execute_result_with_contacts

        # Act
        result = await contacts_repository.bd_soon(days)

        # Assert
        assert result == sample_contacts
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful email verification."""
        # Arrange
        email = "john.doe@example.com"
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        await contacts_repository.verify_email(email)

        # Assert
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_email_contact_not_found(self, contacts_repository, mock_session, mock_execute_result):
        """Test email verification when contact doesn't exist."""
        # Arrange
        email = "nonexistent@example.com"
        mock_session.execute.return_value = mock_execute_result

        # Act
        await contacts_repository.verify_email(email)

        # Assert
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_avatar_url_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful avatar URL update."""
        # Arrange
        contact_id = 1
        avatar_url = "https://new-avatar.com/image.jpg"
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.update_avatar_url(contact_id, avatar_url)

        # Assert
        assert result == sample_contact
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_avatar_url_contact_not_found(self, contacts_repository, mock_session, mock_execute_result):
        """Test avatar URL update when contact doesn't exist."""
        # Arrange
        contact_id = 999
        avatar_url = "https://new-avatar.com/image.jpg"
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.update_avatar_url(contact_id, avatar_url)

        # Assert
        assert result is None
        mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_password_token_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful password reset token setting."""
        # Arrange
        email = "john.doe@example.com"
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.set_password_token(email)

        # Assert
        assert result == sample_contact
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_password_token_contact_not_found(self, contacts_repository, mock_session, mock_execute_result):
        """Test password reset token setting when contact doesn't exist."""
        # Arrange
        email = "nonexistent@example.com"
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.set_password_token(email)

        # Assert
        assert result is None
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_password_success(self, contacts_repository, mock_session, sample_contact, mock_execute_result_with_contact):
        """Test successful password setting."""
        # Arrange
        token = "test_reset_token"
        new_password = "new_hashed_password"
        mock_session.execute.return_value = mock_execute_result_with_contact

        # Act
        result = await contacts_repository.set_password(token, new_password)

        # Assert
        assert result == sample_contact
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_password_contact_not_found(self, contacts_repository, mock_session, mock_execute_result):
        """Test password setting when contact doesn't exist."""
        # Arrange
        token = "invalid_token"
        new_password = "new_hashed_password"
        mock_session.execute.return_value = mock_execute_result

        # Act
        result = await contacts_repository.set_password(token, new_password)

        # Assert
        assert result is None
        mock_session.commit.assert_not_called()
        mock_session.refresh.assert_not_called()


class TestContactsRepositoryIntegration:
    """Integration-style tests for ContactsRepository."""

    @pytest.mark.asyncio
    async def test_create_and_retrieve_contact(self, contacts_repository, mock_session, contact_model, sample_contact):
        """Test creating a contact and then retrieving it."""
        # Arrange
        mock_session.execute.side_effect = [
            MagicMock(scalar_one_or_none=lambda: sample_contact),  # For get_contact_by_id
            MagicMock(scalar_one_or_none=lambda: sample_contact)   # For create_contact
        ]

        # Act
        created_contact = await contacts_repository.create_contact(contact_model)
        retrieved_contact = await contacts_repository.get_contact_by_id(created_contact.id)

        # Assert
        assert created_contact == retrieved_contact
        assert mock_session.add.called
        assert mock_session.commit.called
        assert mock_session.refresh.called

    @pytest.mark.asyncio
    async def test_update_and_verify_contact(self, contacts_repository, mock_session, contact_update_model, sample_contact):
        """Test updating a contact and then verifying their email."""
        # Arrange
        contact_id = 1
        email = "john.doe@example.com"
        mock_session.execute.side_effect = [
            MagicMock(scalar_one_or_none=lambda: sample_contact),  # For update_contact
            MagicMock(scalar_one_or_none=lambda: sample_contact)   # For verify_email
        ]

        # Act
        updated_contact = await contacts_repository.update_contact(contact_id, contact_update_model)
        await contacts_repository.verify_email(email)

        # Assert
        assert updated_contact == sample_contact
        assert mock_session.commit.call_count == 2
        assert mock_session.refresh.call_count == 2

    @pytest.mark.asyncio
    async def test_password_reset_flow(self, contacts_repository, mock_session, sample_contact):
        """Test complete password reset flow."""
        # Arrange
        email = "john.doe@example.com"
        token = "test_reset_token"
        new_password = "new_hashed_password"
        mock_session.execute.side_effect = [
            MagicMock(scalar_one_or_none=lambda: sample_contact),  # For set_password_token
            MagicMock(scalar_one_or_none=lambda: sample_contact),  # For set_password
        ]

        # Act
        token_contact = await contacts_repository.set_password_token(email)
        password_contact = await contacts_repository.set_password(token, new_password)

        # Assert
        assert token_contact == sample_contact
        assert password_contact == sample_contact
        assert mock_session.commit.call_count == 2
        assert mock_session.refresh.call_count == 2 