import heapq

from app.services.solution import Solution, add_solution_with_diversity
from app.utils.route import get_edge_costs


def optimized_multi_objective_routing(G, source, destination, start_time_sec):
    """
    Algoritmo A* Multi-Objetivo (Tempo, CO2, Exercício).
    Garante a diversidade de soluções na fronteira de Pareto.
    """
    # 1. Configurações de Diversidade
    MAX_LABELS_PER_NODE = 10  # Permite manter várias opções em cada paragem
    TIME_WINDOW_EPSILON = 120 # (2 min) Agrupa soluções muito parecidas para ganhar velocidade

    # 2. Inicialização
    # label_set[nó] = lista de objetos Solution
    label_set = {node: [] for node in G.nodes}
    final_solutions = []
    count = 0 

    # Heurística Admissível (Peso 1.0 para não matar a diversidade)
    h_time, h_co2 = Solution.get_heuristic(source, destination, G)

    initial_sol = Solution(
        total_time=0, 
        total_co2=0.0, 
        total_walk_km=0.0, 
        arrival_sec=start_time_sec, 
        path=[(source, 'start', start_time_sec)]
    )
    label_set[source] = [initial_sol]

    # PQ: (f_time, f_co2, count, current_node, solution)
    pq = [(h_time, h_co2, count, source, initial_sol)]

    while pq:
        f_time, f_co2, _, u, u_sol = heapq.heappop(pq)

        # --- PODAGEM GLOBAL RELAXADA ---
        # Só descartamos se for MUITO pior que a melhor solução já encontrada
        if final_solutions:
            best_t_found = min(s.total_time for s in final_solutions)
            if f_time > best_t_found * 1.5: # Permite soluções até 50% mais lentas
                continue

        # --- CHEGADA AO DESTINO ---
        if u == destination:
            final_solutions, _ = add_solution_with_diversity(
                final_solutions, u_sol, max_labels=15, epsilon=TIME_WINDOW_EPSILON
            )
            continue

        # --- EXPLORAÇÃO ---
        for v in G.neighbors(u):
            # BLOQUEIO DE CICLOS (Evita loops infinitos em transferências)
            if any(v == step[0] for step in u_sol.path):
                continue

            edge_data = G.get_edge_data(u, v).get(0)
            t_cost, c_cost, w_cost, trip_info = get_edge_costs(edge_data, u_sol.arrival_sec)
            
            if t_cost == float('inf'): continue

            # Acumuladores
            v_g_time = u_sol.total_time + t_cost
            v_g_co2 = u_sol.total_co2 + c_cost
            v_g_walk = u_sol.total_walk_km + w_cost
            v_arrival = u_sol.arrival_sec + t_cost

            # Heurística para o próximo nó
            h_v_t, h_v_c = Solution.get_heuristic(v, destination, G)
            v_f_time = v_g_time + h_v_t
            v_f_co2 = v_g_co2 + h_v_c

            # Criar nova solução
            v_sol = Solution(
                v_g_time, v_g_co2, v_g_walk, v_arrival, 
                u_sol.path + [(v, trip_info, v_arrival)]
            )

            # --- GESTÃO DE LABELS COM DIVERSIDADE ---
            label_set[v], added = add_solution_with_diversity(
                label_set[v], v_sol, max_labels=MAX_LABELS_PER_NODE, epsilon=TIME_WINDOW_EPSILON
            )

            if added:
                count += 1
                heapq.heappush(pq, (v_f_time, v_f_co2, count, v, v_sol))

    return final_solutions
