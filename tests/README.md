# Integration Tests

This directory contains comprehensive integration tests for the FastAPI application.

## Test Structure

- `conftest.py` - Original test configuration and fixtures for unit tests
- `test_integration_conftest.py` - Integration test configuration and fixtures
- `test_auth_integration.py` - Integration tests for authentication controller
- `test_contacts_integration.py` - Integration tests for contacts controller
- `test_contacts_repository.py` - Unit tests for contacts repository

## Running Tests

### Install Dependencies

First, install the required testing dependencies:

```bash
poetry install
```

### Run All Tests

```bash
pytest
```

### Run Only Integration Tests

```bash
pytest -m integration
```

### Run Only Unit Tests

```bash
pytest -m unit
```

### Run Specific Test Files

```bash
# Run auth integration tests
pytest tests/test_auth_integration.py

# Run contacts integration tests
pytest tests/test_contacts_integration.py

# Run repository unit tests
pytest tests/test_contacts_repository.py
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

## Test Categories

### Auth Controller Integration Tests

Tests for authentication endpoints:
- Login functionality
- Email verification
- Password reset
- Input validation
- Error handling
- Async operations

### Contacts Controller Integration Tests

Tests for contact management endpoints:
- CRUD operations (Create, Read, Update, Delete)
- Search functionality
- Avatar management
- Authentication-dependent endpoints
- Rate limiting
- Input validation
- Error handling
- Async operations

### Repository Unit Tests

Tests for the data access layer:
- Database operations
- Query building
- Data transformation

## Test Fixtures

The integration tests use several fixtures defined in `test_integration_conftest.py`:

- `client` - FastAPI TestClient instance
- `async_client` - Async HTTP client for async tests
- `mock_contacts_service` - Mock contacts service
- `mock_auth_service` - Mock auth service
- `sample_contact_data` - Sample contact data for testing
- `sample_contact` - Sample contact model instance
- And many more...

## Mocking Strategy

The integration tests use mocking to isolate the controller layer from the service and repository layers:

- Services are mocked to return predefined responses
- Authentication dependencies are mocked to simulate different user states
- External services (email, file upload) are mocked
- Database operations are mocked to avoid actual database connections

## Test Coverage

The integration tests cover:

1. **Happy Path Scenarios** - Successful operations
2. **Error Scenarios** - Various error conditions and exceptions
3. **Validation** - Input validation and constraint checking
4. **Authentication** - Authorization and authentication flows
5. **Async Operations** - Both sync and async endpoint testing
6. **Edge Cases** - Boundary conditions and unusual inputs

## Adding New Tests

When adding new tests:

1. Use the existing fixtures when possible
2. Follow the Arrange-Act-Assert pattern
3. Test both success and failure scenarios
4. Include validation tests for new endpoints
5. Add appropriate docstrings explaining what each test does
6. Use descriptive test names that explain the scenario being tested

## Best Practices

- Keep tests independent and isolated
- Use meaningful test data
- Test both positive and negative scenarios
- Mock external dependencies
- Use descriptive test names and docstrings
- Group related tests in classes
- Use appropriate pytest markers for test categorization 