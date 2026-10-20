"""Contrato HTTP de MiniTask con persistencia JSON aislada por prueba."""

import json
import os

os.environ.setdefault("JWT_SECRET", "integration-test-secret-not-for-deployment-123")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("TESTING", "1")
os.environ.setdefault("DEV_CREATE_TABLES", "false")

import pytest
from fastapi.testclient import TestClient

from app.api.tasks import get_task_service
from app.core.security import create_access_token
from app.main import app
from app.repositories.json_task_repository import JsonTaskRepository
from app.services.task_service import TaskService

OWNER = "student-one@example.com"
OTHER_OWNER = "student-two@example.com"
TASK_PAYLOAD = {
    "titulo": "Leer capítulo 3",
    "descripcion": "Preparar resumen",
    "fecha_limite": "2026-10-30",
}
EXPECTED_FIELDS = {
    "id",
    "titulo",
    "descripcion",
    "fecha_limite",
    "completada",
    "creada_en",
}


@pytest.fixture
def tasks_file(tmp_path):
    return tmp_path / "tasks.json"


@pytest.fixture
def client(tasks_file):
    service = TaskService(JsonTaskRepository(tasks_file))
    app.dependency_overrides[get_task_service] = lambda: service
    with TestClient(app) as http:
        yield http
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {create_access_token(OWNER)}"}


@pytest.fixture
def other_auth_headers():
    return {"Authorization": f"Bearer {create_access_token(OTHER_OWNER)}"}


def _create(client, headers, payload=None):
    return client.post("/tasks", headers=headers, json=payload or TASK_PAYLOAD)


def test_crud_filters_and_json_persistence(client, auth_headers, tasks_file):
    created_response = _create(client, auth_headers)

    assert created_response.status_code == 201
    created = created_response.json()
    assert set(created) == EXPECTED_FIELDS
    assert created["titulo"] == TASK_PAYLOAD["titulo"]
    assert created["descripcion"] == TASK_PAYLOAD["descripcion"]
    assert created["fecha_limite"] == TASK_PAYLOAD["fecha_limite"]
    assert created["completada"] is False
    assert "propietario" not in created_response.text

    persisted = json.loads(tasks_file.read_text(encoding="utf-8"))
    assert len(persisted) == 1
    assert persisted[0]["id"] == created["id"]
    assert persisted[0]["propietario"] == OWNER

    all_response = client.get("/tasks?status=all", headers=auth_headers)
    pending_response = client.get("/tasks?status=pending", headers=auth_headers)
    completed_response = client.get("/tasks?status=completed", headers=auth_headers)
    assert all_response.status_code == 200
    assert [task["id"] for task in all_response.json()] == [created["id"]]
    assert [task["id"] for task in pending_response.json()] == [created["id"]]
    assert completed_response.json() == []

    update_response = client.patch(
        f"/tasks/{created['id']}",
        headers=auth_headers,
        json={"completada": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["completada"] is True
    assert client.get("/tasks?status=pending", headers=auth_headers).json() == []
    assert [task["id"] for task in client.get(
        "/tasks?status=completed", headers=auth_headers
    ).json()] == [created["id"]]

    delete_response = client.delete(f"/tasks/{created['id']}", headers=auth_headers)
    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert client.get("/tasks", headers=auth_headers).json() == []
    assert json.loads(tasks_file.read_text(encoding="utf-8")) == []


def test_each_user_only_lists_their_own_tasks(
    client, auth_headers, other_auth_headers
):
    owner_task = _create(client, auth_headers).json()
    other_task = _create(
        client,
        other_auth_headers,
        {**TASK_PAYLOAD, "titulo": "Tarea de otra persona"},
    ).json()

    owner_list = client.get("/tasks", headers=auth_headers).json()
    other_list = client.get("/tasks", headers=other_auth_headers).json()
    assert [task["id"] for task in owner_list] == [owner_task["id"]]
    assert [task["id"] for task in other_list] == [other_task["id"]]
    assert all("propietario" not in task for task in owner_list + other_list)


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_foreign_task_is_not_found(
    client, auth_headers, other_auth_headers, method
):
    task_id = _create(client, auth_headers).json()["id"]

    if method == "patch":
        response = client.patch(
            f"/tasks/{task_id}",
            headers=other_auth_headers,
            json={"completada": True},
        )
    else:
        response = client.delete(f"/tasks/{task_id}", headers=other_auth_headers)

    assert response.status_code == 404
    assert response.json() == {"detail": "Tarea no encontrada."}


def test_missing_task_is_not_found(client, auth_headers):
    response = client.patch(
        "/tasks/non-existent-id",
        headers=auth_headers,
        json={"completada": True},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Tarea no encontrada."}


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer invalid-jwt"},
        {"Authorization": "Basic invalid-credentials"},
    ],
)
def test_all_tasks_require_valid_bearer_jwt(client, headers):
    response = client.get("/tasks", headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "No autenticado."}


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({"descripcion": "Descripción"}, "titulo"),
        ({"titulo": "Título"}, "descripcion"),
        ({"titulo": "   ", "descripcion": "Descripción"}, "titulo"),
        ({"titulo": "Título", "descripcion": "\t\n"}, "descripcion"),
        ({"titulo": "x" * 121, "descripcion": "Descripción"}, "titulo"),
        ({"titulo": "Título", "descripcion": "x" * 1001}, "descripcion"),
        ({**TASK_PAYLOAD, "fecha_limite": "30/10/2026"}, "fecha_limite"),
    ],
)
def test_create_rejects_invalid_body(client, auth_headers, payload, invalid_field):
    response = client.post("/tasks", headers=auth_headers, json=payload)

    assert response.status_code == 422
    assert any(
        error["loc"] == ["body", invalid_field]
        for error in response.json()["detail"]
    )


def test_rejects_invalid_filter_and_patch_body(client, auth_headers):
    filter_response = client.get("/tasks?status=archived", headers=auth_headers)
    patch_response = client.patch(
        "/tasks/any-id", headers=auth_headers, json={"completada": "yes"}
    )

    assert filter_response.status_code == 422
    assert any(
        error["loc"] == ["query", "status"]
        for error in filter_response.json()["detail"]
    )
    assert patch_response.status_code == 422
    assert any(
        error["loc"] == ["body", "completada"]
        for error in patch_response.json()["detail"]
    )
