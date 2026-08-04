import pytest

from src.map_loader import Edge, MapDataError, Node, load_map
from src.pathfinder import shortest_path


def graph():
    nodes = {index: Node(index, index, index, 0, f"Node_{index}") for index in range(5)}
    edges = {
        0: Edge(0, 0, 1, 5), 1: Edge(1, 1, 2, 5),
        2: Edge(2, 0, 2, 20), 3: Edge(3, 2, 3, 1),
    }
    return nodes, edges


def test_normal_shortest_path_uses_edge_distance():
    nodes, edges = graph()
    assert shortest_path(nodes, edges, 0, 2) == ([0, 1, 2], 10)


def test_start_equals_end():
    nodes, edges = graph()
    assert shortest_path(nodes, edges, 2, 2) == ([2], 0)


@pytest.mark.parametrize("start,end,message", [(99, 1, "Start"), (0, 99, "End")])
def test_invalid_nodes(start, end, message):
    nodes, edges = graph()
    with pytest.raises(ValueError, match=message):
        shortest_path(nodes, edges, start, end)


def test_unreachable_destination():
    nodes, edges = graph()
    assert shortest_path(nodes, edges, 0, 4) == (None, None)


def test_multiple_paths_selects_lowest_cost():
    nodes, edges = graph()
    assert shortest_path(nodes, edges, 0, 3) == ([0, 1, 2, 3], 11)


def test_loader_ignores_comments_and_blank_lines(tmp_path):
    nodes_file = tmp_path / "nodes.txt"
    edges_file = tmp_path / "edges.txt"
    nodes_file.write_text("# comment\n\n0 1 2 0 School_A\n1 3 4 1 Shop_A\n", encoding="utf-8")
    edges_file.write_text("# comment\n0 0 1 12\n", encoding="utf-8")
    nodes, edges = load_map(nodes_file, edges_file)
    assert set(nodes) == {0, 1}
    assert edges[0].distance == 12


def test_loader_rejects_unknown_edge_node(tmp_path):
    nodes_file = tmp_path / "nodes.txt"
    edges_file = tmp_path / "edges.txt"
    nodes_file.write_text("0 1 2 0 School_A\n", encoding="utf-8")
    edges_file.write_text("0 0 99 12\n", encoding="utf-8")
    with pytest.raises(MapDataError, match="unknown node"):
        load_map(nodes_file, edges_file)


def test_loader_rejects_duplicate_node_id(tmp_path):
    nodes_file = tmp_path / "nodes.txt"
    edges_file = tmp_path / "edges.txt"
    nodes_file.write_text("0 1 2 0 A\n0 3 4 1 B\n", encoding="utf-8")
    edges_file.write_text("", encoding="utf-8")
    with pytest.raises(MapDataError, match="duplicate node"):
        load_map(nodes_file, edges_file)
