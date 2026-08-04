from dataclasses import asdict, dataclass
from pathlib import Path
import os
import tempfile


class MapDataError(ValueError):
    """Raised when map data is malformed or inconsistent."""


@dataclass(frozen=True)
class Node:
    id: int
    x: float
    y: float
    type_id: int
    name: str

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class Edge:
    id: int
    node_a: int
    node_b: int
    distance: float

    def to_dict(self):
        return asdict(self)


def _data_lines(path):
    for line_number, raw_line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if line and not line.startswith("#"):
            yield line_number, line


def load_nodes(path):
    nodes = {}
    for line_number, line in _data_lines(path):
        parts = line.split(maxsplit=4)
        if len(parts) != 5:
            raise MapDataError(f"{path}:{line_number}: expected 5 fields")
        try:
            node = Node(int(parts[0]), float(parts[1]), float(parts[2]), int(parts[3]), parts[4])
        except ValueError as exc:
            raise MapDataError(f"{path}:{line_number}: invalid numeric field") from exc
        if node.id in nodes:
            raise MapDataError(f"{path}:{line_number}: duplicate node ID {node.id}")
        if node.type_id not in range(5):
            raise MapDataError(f"{path}:{line_number}: TypeID must be 0-4")
        nodes[node.id] = node
    return nodes


def load_edges(path, nodes):
    edges = {}
    for line_number, line in _data_lines(path):
        parts = line.split()
        if len(parts) != 4:
            raise MapDataError(f"{path}:{line_number}: expected 4 fields")
        try:
            edge = Edge(int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3]))
        except ValueError as exc:
            raise MapDataError(f"{path}:{line_number}: invalid numeric field") from exc
        if edge.id in edges:
            raise MapDataError(f"{path}:{line_number}: duplicate edge ID {edge.id}")
        if edge.node_a not in nodes or edge.node_b not in nodes:
            raise MapDataError(f"{path}:{line_number}: edge refers to an unknown node")
        if edge.distance < 0:
            raise MapDataError(f"{path}:{line_number}: distance cannot be negative")
        edges[edge.id] = edge
    return edges


def load_map(node_path, edge_path):
    nodes = load_nodes(node_path)
    return nodes, load_edges(edge_path, nodes)


def _atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", text=True)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary, path)
    except Exception:
        Path(temporary).unlink(missing_ok=True)
        raise


def save_map(node_path, edge_path, nodes, edges):
    node_header = "# NodeID  X  Y  TypeID  Name\n"
    node_body = "".join(
        f"{node.id} {node.x:g} {node.y:g} {node.type_id} {node.name}\n"
        for node in sorted(nodes.values(), key=lambda item: item.id)
    )
    edge_header = "# EdgeID  NodeA  NodeB  Distance\n"
    edge_body = "".join(
        f"{edge.id} {edge.node_a} {edge.node_b} {edge.distance:g}\n"
        for edge in sorted(edges.values(), key=lambda item: item.id)
    )
    _atomic_write(node_path, node_header + node_body)
    _atomic_write(edge_path, edge_header + edge_body)
