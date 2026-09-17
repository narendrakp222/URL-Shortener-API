import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_shorten_url_success(client: AsyncClient):
    payload = {"url": "https://fastapi.tiangolo.com"}
    response = await client.post("/shorten", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "short_code" in data
    assert "short_url" in data
    assert data["original_url"] == "https://fastapi.tiangolo.com"
    assert data["click_count"] == 0


@pytest.mark.asyncio
async def test_shorten_url_invalid_scheme(client: AsyncClient):
    payload = {"url": "ftp://invalid-scheme.com"}
    response = await client.post("/shorten", json=payload)
    assert response.status_code == 422  # Validation error from Pydantic validator


@pytest.mark.asyncio
async def test_shorten_url_custom_code(client: AsyncClient):
    payload = {
        "url": "https://python.org",
        "custom_code": "py-docs"
    }
    response = await client.post("/shorten", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["short_code"] == "py-docs"

    # Duplicate custom code should fail with 400 Bad Request
    dup_response = await client.post("/shorten", json=payload)
    assert dup_response.status_code == 400
    assert "already in use" in dup_response.json()["detail"]


@pytest.mark.asyncio
async def test_redirect_and_click_counter(client: AsyncClient):
    # Shorten a URL first
    shorten_res = await client.post("/shorten", json={"url": "https://github.com"})
    short_code = shorten_res.json()["short_code"]

    # Perform GET /{short_code}
    redirect_res = await client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_res.status_code == 307
    assert redirect_res.headers["location"] == "https://github.com"

    # Verify click count via /stats/{short_code}
    stats_res = await client.get(f"/stats/{short_code}")
    assert stats_res.status_code == 200
    stats_data = stats_res.json()
    assert stats_data["click_count"] == 1


@pytest.mark.asyncio
async def test_advanced_analytics(client: AsyncClient):
    shorten_res = await client.post("/shorten", json={"url": "https://render.com"})
    short_code = shorten_res.json()["short_code"]

    # Simulate 3 clicks
    for _ in range(3):
        await client.get(f"/{short_code}")

    analytics_res = await client.get(f"/analytics/{short_code}")
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()
    assert analytics_data["total_clicks"] == 3
    assert analytics_data["clicks_today"] == 3
    assert analytics_data["last_7_days_clicks"] == 3
    assert analytics_data["last_30_days_clicks"] == 3


@pytest.mark.asyncio
async def test_list_urls(client: AsyncClient):
    await client.post("/shorten", json={"url": "https://site1.com"})
    await client.post("/shorten", json={"url": "https://site2.com"})

    response = await client.get("/urls")
    assert response.status_code == 200
    urls = response.json()
    assert len(urls) >= 2


@pytest.mark.asyncio
async def test_delete_url(client: AsyncClient):
    shorten_res = await client.post("/shorten", json={"url": "https://to-delete.com"})
    short_code = shorten_res.json()["short_code"]

    delete_res = await client.delete(f"/{short_code}")
    assert delete_res.status_code == 200

    # Ensure get stats returns 404 after deletion
    stats_res = await client.get(f"/stats/{short_code}")
    assert stats_res.status_code == 404
