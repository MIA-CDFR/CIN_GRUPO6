import numpy as np

from app.services.solution import Solution, add_solution_with_diversity
from app.utils.route import get_edge_costs


def aco_optimized_routing(G, source, destination, start_time_sec, n_ants=30, n_iterations=20):
    # Parâmetros de Controlo
    ALPHA = 1.0     # Importância do Feromónio
    BETA = 3.0      # Importância da Heurística (Maior = Mais focada no destino)
    Q = 100         # Constante de depósito de feromónio
    RHO = 0.1       # Taxa de evaporação

    # Inicialização de Feromónios (Pequeno valor inicial para encorajar exploração)
    pheromone = {edge: 0.1 for edge in G.edges()}
    global_pareto_front = []

    print(f"🚀 Iniciando ACO Agressivo: {n_ants} formigas, {n_iterations} gerações...")

    for iteration in range(n_iterations):
        iteration_solutions = []
        
        for ant_id in range(n_ants):
            current_node = source
            path = [(source, 'start', start_time_sec)]
            visited = {source}
            total_time = 0
            total_co2 = 0.0
            total_walk = 0.0
            current_time = start_time_sec
            
            # Limite de passos para evitar que a formiga se perca
            for step in range(100):
                if current_node == destination:
                    break

                neighbors = list(G.neighbors(current_node))
                valid_neighbors = [n for n in neighbors if n not in visited]

                if not valid_neighbors:
                    break # Formiga em beco sem saída

                # Cálculo de Probabilidades
                probabilities = []
                candidate_data = []
                
                for v in valid_neighbors:
                    edge_data = G[current_node][v].get(0)
                    # Obter custos reais (GTFS + Walk)
                    t_cost, c_cost, w_cost, info = get_edge_costs(edge_data, current_time)

                    if t_cost == float('inf'):
                        probabilities.append(0)
                        candidate_data.append(None)
                        continue

                    # HEURÍSTICA AGRESSIVA (1 / Distância ao Destino)
                    h_v_time, _ = Solution.get_heuristic(v, destination, G)
                    # Adicionamos +1 para evitar divisão por zero e t_cost para penalizar arestas lentas
                    visibility = 1.0 / (t_cost + h_v_time + 1)

                    tau = pheromone.get((current_node, v), 0.1)

                    # Fórmula ACS: tau^alpha * visibility^beta
                    prob = (tau ** ALPHA) * (visibility ** BETA)
                    probabilities.append(prob)
                    candidate_data.append((v, t_cost, c_cost, w_cost, info))

                prob_sum = sum(probabilities)
                if prob_sum == 0: break # Nenhuma opção válida temporalmente

                # Seleção por Roleta
                norm_probs = [p / prob_sum for p in probabilities]
                choice_idx = np.random.choice(len(valid_neighbors), p=norm_probs)
                
                v, t, c, w, info = candidate_data[choice_idx]
                
                # Atualizar estado da formiga
                current_time += t
                total_time += t
                total_co2 += c
                total_walk += w
                current_node = v
                path.append((v, info, current_time))
                visited.add(v)

            if current_node == destination:
                sol = Solution(total_time, total_co2, total_walk, current_time, path)
                iteration_solutions.append(sol)
                # Atualizar a Fronteira de Pareto Global
                global_pareto_front, updated = add_solution_with_diversity(global_pareto_front, sol, max_labels=15, epsilon=60)

        # --- ATUALIZAÇÃO DE FEROMÓNIO ---
        # 1. Evaporação
        for edge in pheromone:
            pheromone[edge] *= (1 - RHO)
        
        # 2. Depósito (Apenas as formigas que chegaram ao destino e são Pareto-ótimas)
        for sol in global_pareto_front:
            # Recompensa inversamente proporcional ao tempo (mais rápido = mais feromónio)
            reward = Q / (sol.total_time / 60.0) 
            for i in range(len(sol.path) - 1):
                u = sol.path[i][0]
                v = sol.path[i+1][0]
                if (u, v) in pheromone:
                    pheromone[(u, v)] += reward
                    
        if iteration % 5 == 0:
            print(f"  Iteração {iteration}: {len(global_pareto_front)} soluções na fronteira.")

    return global_pareto_front