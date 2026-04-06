from fastapi.testclient import TestClient

from genai_template.api.main import app

client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_without_llm() -> None:
    response = client.post(
        "/run",
        json={"message": "hello", "use_llm": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["processed"] is True


def test_run_with_llm() -> None:
    response = client.post(
        "/run",
        json={"message": "hello", "use_llm": True},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["processed"] is True
    assert data["result"] is not None
