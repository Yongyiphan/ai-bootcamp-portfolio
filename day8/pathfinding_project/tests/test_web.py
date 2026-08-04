def test_public_can_view_map_and_find_path(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/map").status_code == 200
    response = client.get("/api/path?start=0&end=2")
    assert response.status_code == 200
    assert response.get_json() == {"path": [0, 1, 2], "total_distance": 230}


def test_invalid_and_unreachable_path_responses(client, app):
    invalid = client.get("/api/path?start=999&end=2")
    assert invalid.status_code == 400
    node_file = app.config["NODE_FILE"]
    with node_file.open("a", encoding="utf-8") as handle:
        handle.write("99 100 100 4 Isolated_Node\n")
    unreachable = client.get("/api/path?start=0&end=99")
    assert unreachable.status_code == 404


def test_failed_login(client):
    assert client.post("/api/login", json={"password": "wrong"}).status_code == 401


def test_every_edit_method_rejects_public_user(client):
    requests = [
        client.post("/api/nodes", json={}), client.put("/api/nodes/0", json={}),
        client.delete("/api/nodes/0"), client.post("/api/edges", json={}),
        client.put("/api/edges/0", json={}), client.delete("/api/edges/0"),
    ]
    assert all(response.status_code == 401 for response in requests)


def test_editor_can_add_update_and_delete_node(editor_client):
    created = editor_client.post("/api/nodes", json={
        "id": 99, "x": 50, "y": 50, "type_id": 4, "name": "Test_Park"
    })
    assert created.status_code == 201
    updated = editor_client.put("/api/nodes/99", json={
        "x": 51, "y": 52, "type_id": 1, "name": "Test_Shop"
    })
    assert updated.status_code == 200
    assert updated.get_json()["name"] == "Test_Shop"
    assert editor_client.delete("/api/nodes/99").status_code == 204


def test_editor_can_add_update_and_delete_edge(editor_client):
    created = editor_client.post("/api/edges", json={
        "id": 99, "node_a": 0, "node_b": 2, "distance": 50
    })
    assert created.status_code == 201
    updated = editor_client.put("/api/edges/99", json={
        "node_a": 0, "node_b": 3, "distance": 60
    })
    assert updated.status_code == 200
    assert updated.get_json()["distance"] == 60
    assert editor_client.delete("/api/edges/99").status_code == 204


def test_logout_removes_editor_access(editor_client):
    assert editor_client.post("/api/logout").status_code == 200
    assert editor_client.post("/api/nodes", json={}).status_code == 401
