import os
import sys
import pytest

# Add src directory to path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from main import app as search_app

@pytest.fixture
def client():
    """TestClient for the Search Service FastAPI app."""
    return TestClient(search_app)