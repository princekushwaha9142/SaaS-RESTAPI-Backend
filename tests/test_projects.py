import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_create_project(auth_client: AsyncClient):
    resp = await auth_client.post("/projects/", json={"name": "My Project", "description": "Test"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "My Project"
    assert "slug" in resp.json()


async def test_list_projects(auth_client: AsyncClient):
    await auth_client.post("/projects/", json={"name": "List Project"})
    resp = await auth_client.get("/projects/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_get_project(auth_client: AsyncClient):
    create = await auth_client.post("/projects/", json={"name": "Get Project"})
    project_id = create.json()["id"]
    resp = await auth_client.get(f"/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


async def test_update_project(auth_client: AsyncClient):
    create = await auth_client.post("/projects/", json={"name": "Old Name"})
    project_id = create.json()["id"]
    resp = await auth_client.patch(f"/projects/{project_id}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


async def test_delete_project(auth_client: AsyncClient):
    create = await auth_client.post("/projects/", json={"name": "To Delete"})
    project_id = create.json()["id"]
    resp = await auth_client.delete(f"/projects/{project_id}")
    assert resp.status_code == 204
    get = await auth_client.get(f"/projects/{project_id}")
    assert get.status_code == 404


async def test_project_not_found(auth_client: AsyncClient):
    resp = await auth_client.get("/projects/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404