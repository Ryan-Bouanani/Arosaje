import pytest
import uuid

@pytest.fixture
def api_url() -> str:
    return "http://localhost:8000"

@pytest.fixture
def test_user_email() -> str:
    unique_id = str(uuid.uuid4())[:8]
    return f"test.user.{unique_id}@test.com"

@pytest.fixture
def test_password() -> str:
    return "motdepasse123" 