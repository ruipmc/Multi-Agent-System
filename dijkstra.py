import heapq

# Função de Dijkstra para calcular a rota mais curta
def dijkstra(graph, start, goal):
    queue = [(0, start, [])]
    visited = set()
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]
        if node == goal:
            return (cost, path)
        for (next_node, weight) in graph.get(node, []):
            if next_node not in visited:
                heapq.heappush(queue, (cost + weight, next_node, path))
    return float("inf"), []


