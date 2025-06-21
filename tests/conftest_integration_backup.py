"""
Integration test configuration and fixtures.
This module provides fixtures and configuration for integration tests
using FastAPI TestClient and mocked services.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app
from src.database import get_db
from src.database.models.contacts_model import Contact, UserRole
from src.auth.contact_schema import ContactModel
from src.features.contacts.schema.contact_create_schema import ContactCreateModel
from src.features.contacts.schema.contact_update_schema import ContactUpdateModel
from src.features.auth.schema.login_schema import LoginModel
from src.features.auth.schema.password_set_schema import PasswordSetModel


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = AsyncMock()
    return session


@pytest.fixture
def override_get_db(mock_db_session):
    """Override the database dependency for testing."""
    async def _override_get_db():
        yield mock_db_session
    
    return _override_get_db


@pytest.fixture
def sample_contact_data():
    """Sample contact data for testing."""
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "role": UserRole.USER,
        "birth_day": "1990-01-01",
        "avatar": "https://example.com/avatar.jpg",
        "data": {"key": "value"}
    }


@pytest.fixture
def sample_contact_create_data():
    """Sample contact creation data for testing."""
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567890",
        "password": "testpassword123",
        "birth_day": "1995-05-15",
        "data": {"key": "value"}
    }


@pytest.fixture
def sample_contact_update_data():
    """Sample contact update data for testing."""
    return {
        "first_name": "Updated",
        "last_name": "Name",
        "phone": "+9876543210",
        "birth_day": "1995-05-15",
        "data": {"updated": "data"}
    }


@pytest.fixture
def sample_login_data():
    """Sample login data for testing."""
    return {
        "email": "john.doe@example.com",
        "password": "testpassword123"
    }


@pytest.fixture
def sample_password_set_data():
    """Sample password set data for testing."""
    return {
        "password": "newpassword123"
    }


@pytest.fixture
def sample_contact(sample_contact_data):
    """Sample Contact model instance."""
    contact = Contact(
        id=1,
        first_name=sample_contact_data["first_name"],
        last_name=sample_contact_data["last_name"],
        email=sample_contact_data["email"],
        phone=sample_contact_data["phone"],
        role=sample_contact_data["role"],
        birth_day=date.fromisoformat(sample_contact_data["birth_day"]),
        avatar=sample_contact_data["avatar"],
        data=sample_contact_data["data"],
        password="hashed_password",
        verified=True,
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
            first_name=contact_data["first_name"],
            last_name=contact_data["last_name"],
            email=contact_data["email"],
            phone=contact_data["phone"],
            role=contact_data["role"],
            birth_day=date.fromisoformat(contact_data["birth_day"]),
            avatar=contact_data["avatar"],
            data=contact_data["data"],
            password="hashed_password",
            verified=True,
            verification_token=f"token_{i}",
            password_reset_token=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        contacts.append(contact)
    return contacts


@pytest.fixture
def mock_contacts_repository():
    """Mock contacts repository for testing."""
    with patch('src.features.contacts.contacts_service.ContactsRepository') as mock:
        yield mock


@pytest.fixture
def mock_auth_service():
    """Mock auth service for testing."""
    with patch('src.features.auth.auth_controller.AuthService') as mock:
        yield mock


@pytest.fixture
def mock_contacts_service():
    """Mock contacts service for testing."""
    with patch('src.features.contacts.contacts_controller.ContactsService') as mock:
        yield mock


@pytest.fixture
def mock_upload_file_service():
    """Mock upload file service for testing."""
    with patch('src.features.contacts.contacts_controller.UploadFileService') as mock:
        yield mock


@pytest.fixture
def mock_email_service():
    """Mock email service for testing."""
    with patch('src.features.contacts.contacts_service.send_email') as mock:
        yield mock


@pytest.fixture
def mock_hash():
    """Mock hash service for testing."""
    with patch('src.features.contacts.contacts_service.Hash') as mock:
        yield mock


@pytest.fixture
def mock_gravatar():
    """Mock gravatar service for testing."""
    with patch('src.features.contacts.contacts_service.Gravatar') as mock:
        yield mock


@pytest.fixture
def mock_current_user(sample_contact):
    """Mock current user dependency for testing."""
    with patch('src.features.contacts.contacts_controller.get_current_user', new=AsyncMock(return_value=sample_contact)) as mock:
        yield mock


@pytest.fixture
def mock_current_admin_user(sample_contact):
    """Mock current admin user dependency for testing."""
    with patch('src.features.contacts.contacts_controller.get_current_admin_user', new=AsyncMock(return_value=sample_contact)) as mock:
        yield mock


@pytest.fixture
def mock_current_cached_user(sample_contact):
    """Mock current cached user dependency for testing."""
    with patch('src.features.contacts.contacts_controller.get_current_cached_user', new=AsyncMock(return_value=sample_contact)) as mock:
        yield mock


@pytest.fixture
def patch_rate_limiter():
    """Patch the rate limiter to avoid 429 errors in tests."""
    with patch('src.features.contacts.contacts_controller.limiter', new=MagicMock()):
        yield


@pytest.fixture
def client(patch_rate_limiter, mock_current_user, mock_current_admin_user, mock_current_cached_user):
    """Create a test client with overridden database and auth dependencies, and patched rate limiter."""
    mock_session = AsyncMock()
    async def _override_get_db():
        yield mock_session
    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(patch_rate_limiter, mock_current_user, mock_current_admin_user, mock_current_cached_user):
    """Create an async test client with overridden database and auth dependencies, and patched rate limiter."""
    mock_session = AsyncMock()
    async def _override_get_db():
        yield mock_session
    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear() 