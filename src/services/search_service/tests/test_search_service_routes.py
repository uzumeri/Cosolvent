import pytest
import asyncio
import json
from unittest.mock import AsyncMock
import httpx
import types

from src.schemas.search_service_schema import AssetReadyForIndexing


def dummy_embedding(length=1536):
    """Generates a dummy embedding vector of a given length."""
    return [0.1] * length


def test_health(client):
    response = client.get("/api/search/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_basic(client, monkeypatch):
    # Dummy matches returned by Pinecone
    dummy_matches = [
        {"id": "asset1", "score": 0.9, "metadata": {"user_id": "user1"}},
        {"id": "asset2", "score": 0.8, "metadata": {}},
    ]
    # Patch query refinement and embedding
    monkeypatch.setattr("src.core.search.refine_query", lambda q: q)
    monkeypatch.setattr("src.core.search.embed_text", lambda t: dummy_embedding())
    # Patch Pinecone query
    monkeypatch.setattr("src.core.search.query_vectors", lambda vec, filt, k: dummy_matches)

    payload = {"query": "test query"}
    response = client.post("/api/search/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    first = data["results"][0]
    assert first["asset_id"] == "asset1"
    assert pytest.approx(first["score"], 0.1) == 0.9


def test_search_with_filters(client, monkeypatch):
    dummy_matches = [
        {"id": "assetX", "score": 0.5, "metadata": {"user_id": "user2", "created_at": "2025-06-18T00:00:00"}}
    ]
    monkeypatch.setattr("src.core.search.refine_query", lambda q: q)
    monkeypatch.setattr("src.core.search.embed_text", lambda t: dummy_embedding())
    monkeypatch.setattr("src.core.search.query_vectors", lambda vec, filt, k: dummy_matches)

    payload = {
        "query": "another",
        "user_id": "user2",
        "date_from": "2025-06-01T00:00:00",
        "date_to": "2025-06-30T23:59:59",
        "top_k": 5
    }
    response = client.post("/api/search/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["metadata"]["user_id"] == "user2"


@pytest.mark.asyncio
async def test_asset_ready_includes_profile(monkeypatch):
    # Dummy profile returned by Profile Service
    dummy_profile = {
        "type": "company",
        "company_name": "Foo Farms",
        "primary_contact": "Jane Doe",
        "head_office": "123 Main St",
        "region": "Midwest",
        "founded_year": 1999,
        "employees": 10,
        "description": "A leading farm company.",
        "type_of_operation": "Grain",
        "products": [{"name": "Wheat", "category": "Grain", "variety": "Hard Red", "quantity": 100, "unit": "tons"}],
        "certifications": ["Organic"],
        "export_markets": ["EU"],
        "key_people": ["Jane Doe"],
        "awards": ["Best Farm 2020"],
        "social_media": {"twitter": "@foofarms"}
    }
    class MockResponse:
        def __init__(self, status, data):
            self._status = status
            self._data = data
        def raise_for_status(self):
            pass
        def json(self):
            return self._data
    async def fake_get(self, url, **kwargs):
        return MockResponse(200, dummy_profile)
    monkeypatch.setattr(httpx.AsyncClient, "get", fake_get)

    recorded = {}
    async def fake_upsert_vector(asset_id, vector, metadata):
        recorded["asset_id"] = asset_id
        recorded["metadata"] = metadata
        recorded["vector"] = vector
    monkeypatch.setattr("src.core.rabbitmq.upsert_vector", fake_upsert_vector)

    # Patch openai.Embedding.create to avoid real API call
    class DummyEmbedding:
        data = [types.SimpleNamespace(embedding=dummy_embedding())]
    import openai
    monkeypatch.setattr(openai.Embedding, "create", lambda **kwargs: DummyEmbedding())

    # Import and call the handler
    from src.core.rabbitmq import on_message
    event = AssetReadyForIndexing(asset_id="A1", user_id="U1", description="Desc")
    class DummyMsg:
        body = event.json().encode()
        def process(self):
            class _Ctx:
                async def __aenter__(self):
                    return self
                async def __aexit__(self, exc_type, exc, tb):
                    pass
            return _Ctx()
    msg = DummyMsg()
    await on_message(msg)
    # Check that profile data is in the indexed context
    assert "Foo Farms" in recorded["metadata"]["context"]
    assert recorded["asset_id"] == "A1"
    assert len(recorded["vector"]) == 1536