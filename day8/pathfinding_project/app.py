import hmac
import os
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session

from src.map_loader import Edge, MapDataError, Node, load_map, save_map
from src.pathfinder import shortest_path


BASE_DIR = Path(__file__).resolve().parent


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-me"),
        EDITOR_PASSWORD=os.environ.get("EDITOR_PASSWORD", "day8-editor"),
        NODE_FILE=BASE_DIR / "data" / "Node_Info.txt",
        EDGE_FILE=BASE_DIR / "data" / "Graph_Path.txt",
    )
    if test_config:
        app.config.update(test_config)

    def current_map():
        return load_map(app.config["NODE_FILE"], app.config["EDGE_FILE"])

    def require_editor():
        if not session.get("is_editor"):
            return jsonify(error="Editor authentication required"), 401
        return None

    @app.errorhandler(MapDataError)
    def malformed_map(error):
        return jsonify(error=str(error)), 500

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/map")
    def map_data():
        nodes, edges = current_map()
        return jsonify(
            nodes=[node.to_dict() for node in nodes.values()],
            edges=[edge.to_dict() for edge in edges.values()],
            is_editor=bool(session.get("is_editor")),
        )

    @app.get("/api/path")
    def path():
        try:
            start = int(request.args["start"])
            end = int(request.args["end"])
        except (KeyError, ValueError):
            return jsonify(error="start and end must be integer node IDs"), 400
        nodes, edges = current_map()
        try:
            route, distance = shortest_path(nodes, edges, start, end)
        except ValueError as error:
            return jsonify(error=str(error)), 400
        if route is None:
            return jsonify(error=f"No path exists between {start} and {end}"), 404
        return jsonify(path=route, total_distance=distance)

    @app.post("/api/login")
    def login():
        supplied = str((request.get_json(silent=True) or {}).get("password", ""))
        expected = str(app.config["EDITOR_PASSWORD"])
        if not hmac.compare_digest(supplied, expected):
            return jsonify(error="Invalid editor password"), 401
        session.clear()
        session["is_editor"] = True
        return jsonify(message="Editor login successful")

    @app.post("/api/logout")
    def logout():
        session.clear()
        return jsonify(message="Logged out")

    def parse_node(payload, node_id=None):
        try:
            parsed_id = int(payload.get("id", node_id)) if node_id is None else node_id
            node = Node(parsed_id, float(payload["x"]), float(payload["y"]),
                        int(payload["type_id"]), str(payload["name"]).strip())
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Node requires numeric id, x, y, type_id and a name") from error
        if node.type_id not in range(5) or not node.name or any(char.isspace() for char in node.name):
            raise ValueError("TypeID must be 0-4 and name must be non-empty without spaces")
        return node

    def parse_edge(payload, edge_id=None):
        try:
            parsed_id = int(payload.get("id", edge_id)) if edge_id is None else edge_id
            edge = Edge(parsed_id, int(payload["node_a"]), int(payload["node_b"]),
                        float(payload["distance"]))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("Edge requires numeric id, node_a, node_b and distance") from error
        if edge.distance < 0:
            raise ValueError("Distance cannot be negative")
        return edge

    @app.post("/api/nodes")
    def add_node():
        if denied := require_editor(): return denied
        nodes, edges = current_map()
        try: node = parse_node(request.get_json(silent=True) or {})
        except ValueError as error: return jsonify(error=str(error)), 400
        if node.id in nodes: return jsonify(error="Node ID already exists"), 409
        nodes[node.id] = node
        save_map(app.config["NODE_FILE"], app.config["EDGE_FILE"], nodes, edges)
        return jsonify(node.to_dict()), 201

    @app.put("/api/nodes/<int:node_id>")
    def edit_node(node_id):
        if denied := require_editor(): return denied
        nodes, edges = current_map()
        if node_id not in nodes: return jsonify(error="Node not found"), 404
        try: nodes[node_id] = parse_node(request.get_json(silent=True) or {}, node_id)
        except ValueError as error: return jsonify(error=str(error)), 400
        save_map(app.config["NODE_FILE"], app.config["EDGE_FILE"], nodes, edges)
        return jsonify(nodes[node_id].to_dict())

    @app.delete("/api/nodes/<int:node_id>")
    def delete_node(node_id):
        if denied := require_editor(): return denied
        nodes, edges = current_map()
        if node_id not in nodes: return jsonify(error="Node not found"), 404
        del nodes[node_id]
        edges = {key: edge for key, edge in edges.items()
                 if edge.node_a != node_id and edge.node_b != node_id}
        save_map(app.config["NODE_FILE"], app.config["EDGE_FILE"], nodes, edges)
        return "", 204

    @app.post("/api/edges")
    def add_edge():
        if denied := require_editor(): return denied
        nodes, edges = current_map()
        try: edge = parse_edge(request.get_json(silent=True) or {})
        except ValueError as error: return jsonify(error=str(error)), 400
        if edge.id in edges: return jsonify(error="Edge ID already exists"), 409
        if edge.node_a not in nodes or edge.node_b not in nodes:
            return jsonify(error="Both edge nodes must exist"), 400
        edges[edge.id] = edge
        save_map(app.config["NODE_FILE"], app.config["EDGE_FILE"], nodes, edges)
        return jsonify(edge.to_dict()), 201

    @app.put("/api/edges/<int:edge_id>")
    def edit_edge(edge_id):
        if denied := require_editor(): return denied
        nodes, edges = current_map()
        if edge_id not in edges: return jsonify(error="Edge not found"), 404
        try: edge = parse_edge(request.get_json(silent=True) or {}, edge_id)
        except ValueError as error: return jsonify(error=str(error)), 400
        if edge.node_a not in nodes or edge.node_b not in nodes:
            return jsonify(error="Both edge nodes must exist"), 400
        edges[edge_id] = edge
        save_map(app.config["NODE_FILE"], app.config["EDGE_FILE"], nodes, edges)
        return jsonify(edge.to_dict())

    @app.delete("/api/edges/<int:edge_id>")
    def delete_edge(edge_id):
        if denied := require_editor(): return denied
        nodes, edges = current_map()
        if edge_id not in edges: return jsonify(error="Edge not found"), 404
        del edges[edge_id]
        save_map(app.config["NODE_FILE"], app.config["EDGE_FILE"], nodes, edges)
        return "", 204

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
