import heapq
import math


def shortest_path(nodes, edges, start, end):
    if start not in nodes:
        raise ValueError(f"Start node {start} does not exist")
    if end not in nodes:
        raise ValueError(f"End node {end} does not exist")
    if start == end:
        return [start], 0

    adjacency = {node_id: [] for node_id in nodes}
    for edge in edges.values():
        adjacency[edge.node_a].append((edge.node_b, edge.distance))
        adjacency[edge.node_b].append((edge.node_a, edge.distance))

    distances = {start: 0}
    previous = {}
    queue = [(0, start)]
    while queue:
        distance, current = heapq.heappop(queue)
        if distance != distances.get(current):
            continue
        if current == end:
            break
        for neighbour, cost in adjacency[current]:
            candidate = distance + cost
            if candidate < distances.get(neighbour, math.inf):
                distances[neighbour] = candidate
                previous[neighbour] = current
                heapq.heappush(queue, (candidate, neighbour))

    if end not in distances:
        return None, None
    path = [end]
    while path[-1] != start:
        path.append(previous[path[-1]])
    path.reverse()
    total = distances[end]
    return path, int(total) if total.is_integer() else total
