import os
import sys
import pytest
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi.testclient import TestClient
from src.main import app as search_app

@pytest.fixture
def client():
    """TestClient for the Search Service FastAPI app."""
    return TestClient(search_app)
