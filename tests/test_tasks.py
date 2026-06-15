import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def _make_project(client: AsyncClient) -> str:
    resp = await client.post("/projects/", json={"name": "Task Project"})
    return resp.json()["id"]


async def test_create_task(auth_client: AsyncClient):
    project_id = await _make_project(auth_client)
    resp = await auth_client.post(f"/projects/{project_id}/tasks", json={
        "title": "First Task", "priority": "high", "tag_names": ["backend", "urgent"],
    })
    assert resp.status_code == 201
    assert resp.json()["title"] == "First Task"
    assert len(resp.json()["tags"]) == 2


async def test_list_tasks(auth_client: AsyncClient):
    project_id = await _make_project(auth_client)
    for i in range(3):
        await auth_client.post(f"/projects/{project_id}/tasks", json={"title": f"Task {i}"})
    resp = await auth_client.get(f"/projects/{project_id}/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) >= 3


async def test_filter_by_status(auth_client: AsyncClient):
    project_id = await _make_project(auth_client)
    await auth_client.post(f"/projects/{project_id}/tasks", json={"title": "Done", "status": "done"})
    await auth_client.post(f"/projects/{project_id}/tasks", json={"title": "Todo", "status": "todo"})
    resp = await auth_client.get(f"/projects/{project_id}/tasks?status=done")
    assert all(t["status"] == "done" for t in resp.json())


async def test_search_tasks(auth_client: AsyncClient):
    project_id = await _make_project(auth_client)
    await auth_client.post(f"/projects/{project_id}/tasks", json={"title": "Fix login bug"})
    await auth_client.post(f"/projects/{project_id}/tasks", json={"title": "Write docs"})
    resp = await auth_client.get(f"/projects/{project_id}/tasks?search=login")
    assert any("login" in t["title"].lower() for t in resp.json())


async def test_update_task(auth_client: AsyncClient):
    project_id = await _make_project(auth_client)
    create = await auth_client.post(f"/projects/{project_id}/tasks", json={"title": "Update me"})
    task_id = create.json()["id"]
    resp = await auth_client.patch(f"/tasks/{task_id}", json={"status": "in_progress"})
    assert resp.json()["status"] == "in_progress"


async def test_delete_task(auth_client: AsyncClient):
    project_id = await _make_project(auth_client)
    create = await auth_client.post(f"/projects/{project_id}/tasks", json={"title": "Delete me"})
    task_id = create.json()["id"]
    await auth_client.delete(f"/tasks/{task_id}")
    resp = await auth_client.get(f"/tasks/{task_id}")
    assert resp.status_code == 404


async def test_comments(auth_client: AsyncClient):
    project_id = await _make_project(auth_client)
    create = await auth_client.post(f"/projects/{project_id}/tasks", json={"title": "Commented"})
    task_id = create.json()["id"]
    await auth_client.post(f"/tasks/{task_id}/comments", json={"body": "First comment"})
    await auth_client.post(f"/tasks/{task_id}/comments", json={"body": "Second comment"})
    resp = await auth_client.get(f"/tasks/{task_id}/comments")
    assert len(resp.json()) == 2