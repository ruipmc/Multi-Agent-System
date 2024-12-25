# Grafo inicial de rotas
route_graph = {
    "supply_base": [("shelter1", 10), ("shelter2", 15), ("affected_area1", 20), ("affected_area2", 25)],
    "shelter1": [("affected_area1", 5), ("affected_area3", 10)],
    "shelter2": [("affected_area2", 10), ("affected_area4", 10)],
    "affected_area1": [("supply_base", 20), ("shelter1", 5), ("affected_area3", 15)],
    "affected_area2": [("supply_base", 25), ("shelter2", 10), ("affected_area4", 20)],
    "affected_area3": [("affected_area1", 15), ("affected_area5", 10)],
    "affected_area4": [("affected_area2", 20), ("affected_area5", 10)],
    "affected_area5": [("affected_area3", 10), ("affected_area4", 10)],
}
