import heapq

from app.services.solution import Solution, add_solution_with_diversity
from app.utils.route import get_edge_costs


def dijkstra_multi_objective(G, source, destination, start_time_sec):
    """
    Versão Dijkstra do roteador: expande por custo real acumulado.
    Ideal para garantir que encontramos todas as rotas ótimas sem viés de heurística.
    """
    # 1. Inicialização
    # label_set[nó] armazena as soluções não-dominadas encontradas para aquele ponto
    label_set = {node: [] for node in G.nodes}
    final_solutions = []
    count = 0 

    # Solução inicial na origem
    initial_sol = Solution(
        total_time=0, 
        total_co2=0.0, 
        total_walk_km=0.0, 
        arrival_sec=start_time_sec, 
        path=[(source, 'start', start_time_sec)]
    )
    label_set[source] = [initial_sol]

    # Fila de Prioridade: (g_time, g_co2, count, current_node, solution)
    # No Dijkstra, a prioridade é apenas o custo real 'g'
    pq = [(0, 0, count, source, initial_sol)]

    while pq:
        g_time, g_co2, _, u, u_sol = heapq.heappop(pq)

        # --- CHEGADA AO DESTINO ---
        if u == destination:
            final_solutions, _ = add_solution_with_diversity(
                final_solutions, u_sol, max_labels=15, epsilon=60
            )
            continue

        # --- EXPLORAÇÃO DE VIZINHOS ---
        for v in G.neighbors(u):
            # Prevenção de ciclos para evitar loops infinitos
            if any(v == step[0] for step in u_sol.path):
                continue
                
            edge_data = G.get_edge_data(u, v).get(0)
            
            # Cálculo de custos dependentes do tempo (GTFS + Caminhada)
            t_cost, c_cost, w_cost, info = get_edge_costs(edge_data, u_sol.arrival_sec)
            
            if t_cost == float('inf'): continue

            # Custos acumulados para o novo nó v
            v_g_time = u_sol.total_time + t_cost
            v_g_co2 = u_sol.total_co2 + c_cost
            v_g_walk = u_sol.total_walk_km + w_cost
            v_arrival = u_sol.arrival_sec + t_cost

            new_v_sol = Solution(
                v_g_time, v_g_co2, v_g_walk, v_arrival,
                u_sol.path + [(v, info, v_arrival)]
            )

            # --- TESTE DE DOMINÂNCIA LOCAL ---
            # Só adicionamos a 'v' se esta nova rota não for pior que as já existentes em 'v'
            label_set[v], added = add_solution_with_diversity(
                label_set[v], new_v_sol, max_labels=8, epsilon=60
            )

            if added:
                count += 1
                # No Dijkstra, a prioridade é o tempo acumulado real
                heapq.heappush(pq, (v_g_time, v_g_co2, count, v, new_v_sol))

    return final_solutions