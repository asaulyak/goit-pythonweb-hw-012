import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, date
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from main import app
from src.database import get_db
from src.auth.contacts_repository import ContactsRepository
from src.database.models.contacts_model import Contact, UserRole
from src.auth.contact_schema import ContactModel
from src.features.contacts.schema.contact_update_schema import ContactUpdateModel
from src.features.auth.schema.login_schema import LoginModel
from src.features.auth.schema.password_set_schema import PasswordSetModel
from src.auth.hash import get_current_user, get_current_admin_user, get_current_cached_user


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session():
    """Mock database session for testing."""
    session = AsyncMock(spec=AsyncSession)
    
    # Create a mock result object
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_result.scalar_one_or_none.return_value = None
    
    # Configure the execute method to return the mock result
    session.execute = AsyncMock(return_value=mock_result)
    
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
def sample_contact_create_data():
    """Sample contact creation data for testing."""
    return {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "+1234567890",
        "password": "testpassword123",
        "role": UserRole.USER,
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
        birth_day=date.fromisoformat(sample_contact_data["birth_day"]) if isinstance(sample_contact_data["birth_day"], str) else sample_contact_data["birth_day"],
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
            birth_day=date.fromisoformat(contact_data["birth_day"]) if isinstance(contact_data["birth_day"], str) else contact_data["birth_day"],
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


# Integration test fixtures
@pytest.fixture
def mock_contacts_repository():
    """Mock contacts repository for testing."""
    with patch('src.features.contacts.contacts_service.ContactsRepository') as mock:
        yield mock


@pytest.fixture
def mock_auth_service():
    """Mock auth service for testing."""
    with patch('src.features.auth.auth_controller.AuthService') as mock:
        instance = mock.return_value
        instance.login = AsyncMock()
        instance.verify_email = AsyncMock()
        instance.set_password = AsyncMock()
        yield mock


@pytest.fixture
def mock_contacts_service():
    """Mock contacts service for testing."""
    with patch('src.features.contacts.contacts_controller.ContactsService') as mock_class:
        # Create a mock instance
        mock_instance = MagicMock()
        mock_instance.get_contacts = AsyncMock()
        mock_instance.search = AsyncMock()
        mock_instance.create_contact = AsyncMock()
        mock_instance.get_contact_by_id = AsyncMock()
        mock_instance.update_contact = AsyncMock()
        mock_instance.delete_contact = AsyncMock()
        mock_instance.reset_password = AsyncMock()
        mock_instance.soon_celebrate = AsyncMock()
        mock_instance.update_avatar_url = AsyncMock()
        
        # Make the class return the mock instance
        mock_class.return_value = mock_instance
        yield mock_class


@pytest.fixture
def mock_upload_file_service():
    """Mock upload file service for testing."""
    with patch('src.features.contacts.contacts_controller.UploadFileService') as mock_class:
        # Create a mock instance
        mock_instance = MagicMock()
        mock_instance.upload_file = AsyncMock(return_value="https://fake-avatar-url.com/avatar.jpg")
        
        # Make the class return the mock instance
        mock_class.return_value = mock_instance
        
        yield mock_class


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
    mock = AsyncMock(return_value=sample_contact)
    with patch('src.auth.hash.get_current_user', new=mock) as mock_func:
        yield mock_func


@pytest.fixture
def mock_current_admin_user(sample_contact):
    """Mock current admin user dependency for testing."""
    mock = AsyncMock(return_value=sample_contact)
    with patch('src.auth.hash.get_current_admin_user', new=mock) as mock_func:
        yield mock_func


@pytest.fixture
def mock_current_cached_user(sample_contact):
    """Mock current cached user dependency for testing."""
    mock = AsyncMock(return_value=sample_contact)
    with patch('src.auth.hash.get_current_cached_user', new=mock) as mock_func:
        yield mock_func


@pytest.fixture
def patch_rate_limiter():
    """Patch the rate limiter to avoid 429 errors in tests."""
    # Create a mock decorator that does nothing
    def mock_limit(limit_str):
        def decorator(func):
            return func
        return decorator
    
    with patch('src.features.contacts.contacts_controller.limiter.limit', new=mock_limit):
        yield


@pytest.fixture
def client(patch_rate_limiter, sample_contact):
    """Create a test client with overridden database and auth dependencies, and patched rate limiter."""
    mock_session = AsyncMock()
    async def _override_get_db():
        yield mock_session
    
    async def _override_get_current_user():
        return sample_contact
    
    async def _override_get_current_admin_user():
        return sample_contact
    
    async def _override_get_current_cached_user():
        return sample_contact
    
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    app.dependency_overrides[get_current_admin_user] = _override_get_current_admin_user
    app.dependency_overrides[get_current_cached_user] = _override_get_current_cached_user
    
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(patch_rate_limiter, sample_contact):
    """Create an async test client with overridden database and auth dependencies, and patched rate limiter."""
    mock_session = AsyncMock()
    async def _override_get_db():
        yield mock_session
    
    async def _override_get_current_user():
        return sample_contact
    
    async def _override_get_current_admin_user():
        return sample_contact
    
    async def _override_get_current_cached_user():
        return sample_contact
    
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    app.dependency_overrides[get_current_admin_user] = _override_get_current_admin_user
    app.dependency_overrides[get_current_cached_user] = _override_get_current_cached_user
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
def client_unauthorized(patch_rate_limiter):
    """Create a test client without auth dependency overrides for testing unauthorized scenarios."""
    mock_session = AsyncMock()
    async def _override_get_db():
        yield mock_session
    
    app.dependency_overrides[get_db] = _override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_contacts_repository_for_auth():
    """Mock contacts repository for auth service testing."""
    with patch('src.features.auth.auth_service.ContactsRepository') as mock_class:
        # Create a mock instance
        mock_instance = MagicMock()
        
        # Mock get_contact_by_email to return a real contact object
        mock_contact = MagicMock()
        mock_contact.email = "test@example.com"
        # Use a properly hashed password that can be verified
        from src.auth.hash import Hash
        mock_contact.password = Hash().get_password_hash("testpassword123")
        mock_contact.verified = True
        
        mock_instance.get_contact_by_email = AsyncMock(return_value=mock_contact)
        mock_instance.get_contact_by_verification_token = AsyncMock(return_value=mock_contact)
        mock_instance.verify_email = AsyncMock()
        mock_instance.set_password = AsyncMock()
        
        # Make the class return the mock instance
        mock_class.return_value = mock_instance
        
        yield mock_class 