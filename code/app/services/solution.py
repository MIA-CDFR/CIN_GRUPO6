import folium
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
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

    def get_full_geometry(self, G_combined, G_walk, stops_df):
        """
        Converte uma solução (path) em uma lista de coordenadas (lat, lon) reais.
        """
        SOURCE_NODE_ID = "USER_START"
        DESTINATION_NODE_ID = "USER_END"

        full_coords = []

        for i in range(len(self.path) - 1):
            u_id, info_u, time_u = self.path[i]
            v_id, info_v, time_v = self.path[i+1]

            if u_id in [SOURCE_NODE_ID, DESTINATION_NODE_ID]:
                continue

            if v_id in [SOURCE_NODE_ID, DESTINATION_NODE_ID]:
                continue

            # Obter dados da aresta no grafo multimodal
            edge_data = G_combined.get_edge_data(u_id, v_id).get(0)

            # Se for um segmento de CAMINHADA (Transferência ou Acesso)
            if edge_data.get('type') == 'walk':
                try:
                    # 1. Pegar os nós correspondentes na rede de ruas
                    u_osm = stops_df.loc[u_id, 'osmnx_node']
                    v_osm = stops_df.loc[v_id, 'osmnx_node']

                    # 2. Obter o caminho mais curto pelas ruas (geometria real)
                    osm_path = nx.shortest_path(G_walk, u_osm, v_osm, weight='length')

                    # 3. Extrair lat/lon de cada nó da rua
                    for node in osm_path:
                        full_coords.append((G_walk.nodes[node]['y'], G_walk.nodes[node]['x']))
                except (nx.NetworkXNoPath, KeyError):
                    # Fallback: se falhar, usa linha reta entre paragens
                    u_lat, u_lon = stops_df.loc[u_id, ['stop_lat', 'stop_lon']]
                    v_lat, v_lon = stops_df.loc[v_id, ['stop_lat', 'stop_lon']]
                    full_coords.extend([(u_lat, u_lon), (v_lat, v_lon)])

            # Se for um segmento de TRANSPORTE (Autocarro ou Metro)
            else:
                u_lat, u_lon = stops_df.loc[u_id, ['stop_lat', 'stop_lon']]
                v_lat, v_lon = stops_df.loc[v_id, ['stop_lat', 'stop_lon']]
                # Nota: Para perfeição, aqui poderias usar o shapes.txt do GTFS. 
                # Como base, usamos a conexão direta entre as paragens.
                full_coords.append((u_lat, u_lon))
                full_coords.append((v_lat, v_lon))

        return full_coords

    def create_route_map(self, G_combined, G_osm, stops_df):
        # 1. Obter a geometria completa
        coords = self.get_full_geometry(G_combined, G_osm, stops_df)

        if not coords:
            return None

        # 2. Criar o mapa centrado no início da rota
        m = folium.Map(location=coords[0], zoom_start=14, tiles="cartodbpositron")

        # 3. Desenhar a linha da rota
        # Usamos cores diferentes para o tipo de transporte se desejar, 
        # mas aqui desenhamos a rota completa como uma linha sólida.
        folium.PolyLine(
            coords, 
            color="#2c3e50", 
            weight=5, 
            opacity=0.8,
            tooltip=f"Tempo: {int(self.total_time/60)} min | CO2: {round(self.total_co2)}g"
        ).add_to(m)

        # 4. Adicionar Marcadores de Início e Fim
        folium.Marker(
            coords[0], 
            popup="Origem", 
            icon=folium.Icon(color='green', icon='play')
        ).add_to(m)

        folium.Marker(
            coords[-1], 
            popup="Destino", 
            icon=folium.Icon(color='red', icon='stop')
        ).add_to(m)

        # 5. Adicionar Marcadores para as paragens intermédias (Transbordos)
        for i in range(1, len(self.path) - 1):
            node_id, info, _ = self.path[i]
            if info == 'transfer' or info == 'walk':
                lat, lon = stops_df.loc[node_id, ['stop_lat', 'stop_lon']]
                folium.CircleMarker(
                    [lat, lon], 
                    radius=4, 
                    color="orange", 
                    fill=True, 
                    popup=f"Transbordo em: {node_id}"
                ).add_to(m)

        return m

def plot_pareto(solutions):
    if not solutions:
        print("Nenhuma solução para plotar.")
        return

    # 1. Extrair dados
    times = np.array([s.total_time / 60 for s in solutions])
    co2 = np.array([s.total_co2 for s in solutions])
    walk = np.array([s.total_walk_km for s in solutions])
    
    # 2. Identificar os índices corretos (Mínimos Absolutos)
    idx_fastest = np.argmin(times)   # O que tem o menor tempo
    idx_greenest = np.argmin(co2)    # O que tem o menor CO2 (Correção aqui!)
    idx_healthiest = np.argmax(walk) # O que exige mais caminhada (opcional)

    # 3. Ordenar apenas para desenhar a linha da fronteira (Trade-off)
    sort_idx = np.argsort(times)
    sorted_times = times[sort_idx]
    sorted_co2 = co2[sort_idx]

    # Configuração do Gráfico
    plt.figure(figsize=(12, 7))
    plt.style.use('seaborn-v0_8-whitegrid')

    # Desenhar a linha e a área de sombra
    plt.plot(sorted_times, sorted_co2, color='#34495e', linestyle='--', alpha=0.5, label='Fronteira de Eficiência')
    plt.fill_between(sorted_times, sorted_co2, max(co2), color='gray', alpha=0.05)

    # Plotar todos os pontos
    scatter = plt.scatter(times, co2, c=walk, s=100, cmap='viridis', edgecolors='white', zorder=3, label='Soluções Pareto')
    cbar = plt.colorbar(scatter)
    cbar.set_label('Caminhada (km)', fontsize=10)

    # --- ANOTAÇÕES CORRETAS ---
    
    # 🚀 Rota Mais Rápida
    plt.annotate(f'🚀 Mais Rápida\n({times[idx_fastest]:.1f} min)', 
                 xy=(times[idx_fastest], co2[idx_fastest]),
                 xytext=(15, 15), textcoords='offset points',
                 bbox=dict(boxstyle='round,pad=0.3', fc='#e8f6f3', ec='#27ae60', alpha=0.8),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3'))

    # 🌿 Rota Mais Ecológica (Ponto de mínimo CO2 real)
    plt.annotate(f'🌿 Mais Ecológica\n({co2[idx_greenest]:.1f}g CO2)', 
                 xy=(times[idx_greenest], co2[idx_greenest]),
                 xytext=(15, -30), textcoords='offset points',
                 bbox=dict(boxstyle='round,pad=0.3', fc='#fef9e7', ec='#f1c40f', alpha=0.8),
                 arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.2'))

    # Títulos e Labels
    plt.title('Fronteira de Pareto: Compromisso Tempo vs. Sustentabilidade', fontsize=15, pad=15)
    plt.xlabel('Tempo de Viagem (Minutos)', fontsize=12)
    plt.ylabel('Emissões de CO2 (Gramas)', fontsize=12)
    plt.legend(loc='upper right')
    
    plt.tight_layout()
    plt.show()

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