from app.services.graph import GraphRoute
from app.services.algoritms.a_star import optimized_multi_objective_routing
from app.services.algoritms.dijkstra import dijkstra_multi_objective
from app.services.algoritms.aco import aco_optimized_routing
from app.utils.time import time_to_seconds

# Carregar grafo
# Rotas: Casa da Musica → Casino da Póvoa de Varzim, 4490-403
graph = GraphRoute(
    origem="Casa da Musica",
    destino="Casino da Póvoa de Varzim, 4490-403",
)

START_TIME = '08:00:00'

# Executar A*
a_star_pareto_solutions = optimized_multi_objective_routing(
    graph.G, graph.origem_node_id, graph.destino_node_id, time_to_seconds(START_TIME)
)

# Ver resultados
for i, sol in enumerate(a_star_pareto_solutions, 1):
    print(f"Rota {i}: {sol.total_time//60}min | {sol.total_co2:.0f}g CO₂ | {sol.total_walk_km:.1f}km caminhada")

# Executar Dijkstra
dijkstra_pareto_solutions = dijkstra_multi_objective(
    graph.G, graph.origem_node_id, graph.destino_node_id, time_to_seconds(START_TIME)
)

# Ver resultados
for i, sol in enumerate(dijkstra_pareto_solutions, 1):
    print(f"Rota {i}: {sol.total_time//60}min | {sol.total_co2:.0f}g CO₂ | {sol.total_walk_km:.1f}km caminhada")

# Executar ACO
aco_pareto_solutions = aco_optimized_routing(
    graph.G, graph.origem_node_id, graph.destino_node_id, time_to_seconds(START_TIME)
)

# Ver resultados
for i, sol in enumerate(aco_pareto_solutions, 1):
    print(f"Rota {i}: {sol.total_time//60}min | {sol.total_co2:.0f}g CO₂ | {sol.total_walk_km:.1f}km caminhada")