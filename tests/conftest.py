import pytest
import asyncio
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.auth.contacts_repository import ContactsRepository
from src.database.models.contacts_model import Contact, UserRole
from src.auth.contact_schema import ContactModel
from src.features.contacts.schema.contact_update_schema import ContactUpdateModel


@pytest.fixture
def mock_session():
    """Mock database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def contacts_repository(mock_session):
    """ContactsRepository instance with mocked session."""
    return ContactsRepository(mock_session)


@pytest.fixture
def sample_contact_data():
    """Sample contact data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "role": UserRole.USER,
        "birth_day": date(1990, 1, 1),
        "avatar": "https://example.com/avatar.jpg",
        "data": {"key": "value"}
    }


@pytest.fixture
def sample_contact(sample_contact_data):
    """Sample Contact model instance."""
    contact = Contact(
        id=1,
        **sample_contact_data,
        password="hashed_password",
        verified=False,
        verification_token="test_verification_token",
        password_reset_token=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    return contact


@pytest.fixture
def sample_contacts(sample_contact_data):
    """List of sample contacts for testing."""
    contacts = []
    for i in range(3):
        contact_data = sample_contact_data.copy()
        contact_data["email"] = f"user{i}@example.com"
        contact_data["first_name"] = f"User{i}"
        
        contact = Contact(
            id=i + 1,
            **contact_data,
            password="hashed_password",
            verified=False,
            verification_token=f"token_{i}",
            password_reset_token=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        contacts.append(contact)
    return contacts


@pytest.fixture
def contact_model(sample_contact_data):
    """ContactModel instance for testing."""
    return ContactModel(**sample_contact_data)


@pytest.fixture
def contact_update_model():
    """ContactUpdateModel instance for testing."""
    return ContactUpdateModel(
        first_name="Updated",
        last_name="Name",
        phone="+9876543210",
        birth_day=date(1995, 5, 15),
        data={"updated": "data"}
    )


@pytest.fixture
def mock_execute_result():
    """Mock result from database execute."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = []
    result.scalar_one_or_none.return_value = None
    return result


@pytest.fixture
def mock_execute_result_with_contact(sample_contact):
    """Mock result from database execute with a contact."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = [sample_contact]
    result.scalar_one_or_none.return_value = sample_contact
    return result


@pytest.fixture
def mock_execute_result_with_contacts(sample_contacts):
    """Mock result from database execute with multiple contacts."""
    result = MagicMock()
    result.scalars.return_value.all.return_value = sample_contacts
    result.scalar_one_or_none.return_value = sample_contacts[0]
    return result 