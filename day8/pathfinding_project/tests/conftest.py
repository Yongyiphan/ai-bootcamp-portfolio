import shutil

import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    source = __import__("pathlib").Path(__file__).parents[1] / "data"
    node_file = tmp_path / "Node_Info.txt"
    edge_file = tmp_path / "Graph_Path.txt"
    shutil.copy(source / "Node_Info.txt", node_file)
    shutil.copy(source / "Graph_Path.txt", edge_file)
    return create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "EDITOR_PASSWORD": "correct-password",
        "NODE_FILE": node_file,
        "EDGE_FILE": edge_file,
    })


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def editor_client(client):
    response = client.post("/api/login", json={"password": "correct-password"})
    assert response.status_code == 200
    return client
