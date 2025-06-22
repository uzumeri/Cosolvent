import pytest


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
    monkeypatch.setattr("core.search.refine_query", lambda q: q)
    monkeypatch.setattr("core.search.embed_text", lambda t: [0.1, 0.2, 0.3])
    # Patch Pinecone query
    monkeypatch.setattr("database.crud.search_service_crud.query_vectors", lambda vec, filt, k: dummy_matches)

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
    monkeypatch.setattr("core.search.refine_query", lambda q: q)
    monkeypatch.setattr("core.search.embed_text", lambda t: [0.4, 0.5, 0.6])
    monkeypatch.setattr("database.crud.search_service_crud.query_vectors", lambda vec, filt, k: dummy_matches)

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