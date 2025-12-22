from shapely.geometry import Point

from app.utils.geo import get_km_distance
from app.utils.time import format_time

class Solution:
    def __init__(self, total_time, total_co2, total_walk_km, arrival_sec, path):
        self.total_time = total_time
        self.total_co2 = total_co2
        self.total_walk_km = total_walk_km
        self.arrival_sec = arrival_sec
        self.path = path

    @staticmethod
    def get_heuristic(u, destino, G):
        """
        Calcula a estimativa admissível (nunca sobrestima) de tempo e CO2.
        Assume a velocidade do Metro (mais rápido) e o seu fator de emissão (mais baixo).
        """
        node_u = G.nodes[u]
        node_d = G.nodes[destino]

        dist_km = get_km_distance(
            Point(node_u['x'], node_u['y']),
            Point(node_d['x'], node_d['y'])
        )

        # Estimativa de Tempo: Distância / Velocidade máxima (ex: 50km/h)
        h_time = (dist_km / 50.0) * 3600 

        # Estimativa de CO2: Distância * Fator mínimo (Metro: 40g/km)
        h_co2 = dist_km * 40.0

        return h_time, h_co2

    def dominates(self, other: 'Solution') -> bool:
        # (Mantém a lógica de dominância que definimos antes)
        better_time = self.total_time <= other.total_time
        better_co2 = self.total_co2 <= other.total_co2
        better_exercise = self.total_walk_km >= other.total_walk_km
        is_better_or_equal = better_time and better_co2 and better_exercise
        is_strictly_better = (self.total_time < other.total_time or 
                             self.total_co2 < other.total_co2 or 
                             self.total_walk_km > other.total_walk_km)
        return is_better_or_equal and is_strictly_better

    def __lt__(self, other):
        """
        Define o comportamento do operador '<'. 
        Útil para o heapq desempatar soluções com o mesmo f_time e f_co2.
        """
        # Se houver empate nos custos principais, priorizamos a que tem MAIS exercício
        if self.total_time == other.total_time and self.total_co2 == other.total_co2:
            return self.total_walk_km > other.total_walk_km
        return self.total_time < other.total_time

    def summarize_solution(self, G_multimodal, start_time_sec: int):
        """Gera um resumo legível e a decomposição do caminho para uma solução."""

        start_time_str = format_time(start_time_sec % 86400) # Hora de partida do dia

        summary = f"\nTempo Total: {format_time(self.total_time)}"
        summary += f"\nCO2 Total: {self.total_co2:.2f} g"
        summary += f"\nHora de Partida: {start_time_str}"
        summary += f"\nHora de Chegada: {format_time(self.arrival_sec % 86400)}"
        summary += "\n--- Detalhes do Percurso ---"

        path_summary = []

        # Processar o caminho para identificar segmentos de viagem
        for i in range(1, len(self.path)):
            u_node, u_trip_info, u_arrival_sec = self.path[i-1]
            v_node, v_trip_info, v_arrival_sec = self.path[i]

            travel_sec = v_arrival_sec - u_arrival_sec

            # Identificar o tipo de movimento
            if v_trip_info == 'start':
                # Ignora o primeiro nó de inicialização
                continue

            elif v_trip_info == 'transfer':
                path_summary.append(f" 🚶 Caminhada: De {G_multimodal.nodes[u_node]['name']} para {G_multimodal.nodes[v_node]['name']} ({format_time(travel_sec)})")

            elif G_multimodal.get_edge_data(u_node, v_node).get(0)['type'] == 'transit':
                # É uma viagem de trânsito (requer cálculo do tempo de espera)
                # Simplificação: Não temos a hora exata de partida neste label, mas podemos inferir
                wait_sec = travel_sec - G_multimodal.get_edge_data(u_node, v_node).get(0)['avg_travel_time'] # Aproximação

                path_summary.append(f" 🚌/🚇 Trânsito (Viagem {v_trip_info}): De {G_multimodal.nodes[u_node]['name']} para {G_multimodal.nodes[v_node]['name']} - (Viagem: {format_time(travel_sec)})")
                # path_summary.append(f"   (Espera: {format_time(wait_sec)}, ")

        return summary + "\n" + "\n".join(path_summary)
    

def add_solution_with_diversity(current_set, new_sol, max_labels, epsilon):
    """
    Garante que a fronteira de Pareto mantém soluções variadas.
    """
    # 1. Dominância Estrita: Se algo já é melhor em TUDO, descarta a nova.
    for existing in current_set:
        if (existing.total_time <= new_sol.total_time and 
            existing.total_co2 <= new_sol.total_co2 and 
            existing.total_walk_km >= new_sol.total_walk_km):
            # Se a nova for igual mas chegar depois, é dominada
            return current_set, False

    # 2. Filtro de Balde (Epsilon): Evita soluções quase idênticas no tempo
    # a menos que tragam uma melhoria real em CO2 ou Exercício.
    for existing in current_set:
        if abs(existing.total_time - new_sol.total_time) < epsilon:
            # Se estão na mesma janela de tempo, só aceitamos a nova se 
            # ela for significativamente melhor nos outros critérios
            if existing.total_co2 <= new_sol.total_co2 * 0.95 and \
               existing.total_walk_km >= new_sol.total_walk_km * 1.05:
                pass # Nova solução é interessante
            else:
                # Se não for substancialmente melhor, consideramos redundante
                if existing.total_co2 <= new_sol.total_co2:
                    return current_set, False

    # 3. Limpeza de soluções dominadas pela NOVA
    updated_set = [new_sol]
    for existing in current_set:
        if not new_sol.dominates(existing):
            updated_set.append(existing)

    # 4. Manter Diversidade se exceder o limite
    if len(updated_set) > max_labels:
        # Preservar os 3 campeões
        best_t = min(updated_set, key=lambda s: s.total_time)
        best_c = min(updated_set, key=lambda s: s.total_co2)
        best_w = max(updated_set, key=lambda s: s.total_walk_km)
        
        winners = {best_t, best_c, best_w}
        others = [s for s in updated_set if s not in winners]
        others.sort(key=lambda s: (s.total_time, s.total_co2))
        
        return list(winners) + others[:(max_labels - len(winners))], True

    return updated_set, True