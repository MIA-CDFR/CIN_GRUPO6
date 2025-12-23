import math
import networkx as nx
import osmnx as ox

from scipy.spatial import cKDTree
from shapely.geometry import Point

from app.utils.co2 import get_co2
from app.utils.time import time_to_seconds
from app.utils.geo import get_geocode_by_address, get_m_distance, get_km_distance
from app.utils.feed import get_filtered_multimodal_feed


class GraphRoute:

    def __init__(
        self,
        origem: str,
        destino: str,
    ):
        self.origem=origem
        self.destino=destino
        self.geo_origem=get_geocode_by_address(origem)
        self.geo_destino=get_geocode_by_address(destino)
        self.gtfs_feed=get_filtered_multimodal_feed(self.geo_origem, self.geo_destino)

        self.build_street_graph()
        self.build_graph()
        self.add_user_points_to_graph()
        self.add_osmnx_transfer_edges()

    def build_graph(self):
        metadata = {
            "crs": "epsg:4326",
        }

        G_transport = nx.MultiDiGraph(**metadata)
        for _, row in self.gtfs_feed.stops.iterrows():
            G_transport.add_node(
                row['stop_id'], 
                y=row['stop_lat'],
                x=row['stop_lon'],
                name=row['stop_name'],
                modo=row['stop_id'].split("_")[0],
            )

        st = self.gtfs_feed.stop_times[['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence']]
        st = st.merge(self.gtfs_feed.trips[['trip_id', 'route_id']], on='trip_id')

        st['arrival_sec'] = st['arrival_time'].apply(time_to_seconds)
        st['departure_sec'] = st['departure_time'].apply(time_to_seconds)

        st = st.sort_values(['trip_id', 'stop_sequence'])

        segments = st.copy()
        segments['next_stop_id'] = segments.groupby('trip_id')['stop_id'].shift(-1)
        segments['next_arrival_sec'] = segments.groupby('trip_id')['arrival_sec'].shift(-1)
        segments['next_stop_sequence'] = segments.groupby('trip_id')['stop_sequence'].shift(-1)

        segments = segments.dropna(subset=['next_stop_id'])
        segments['travel_time_sec'] = segments['next_arrival_sec'] - segments['departure_sec']
        segments = segments[segments['travel_time_sec'] >= 0]

        for (u, v), group in segments.groupby(['stop_id', 'next_stop_id']):

            # --- Cálculo de Distância e CO2 (Propriedades do Segmento) ---
            data_u, data_v = G_transport.nodes[u], G_transport.nodes[v]
            distance_m = get_m_distance(
                Point(data_u['x'], data_u['y']),
                Point(data_v['x'], data_v['y'])
            )

            group.sort_values(by="departure_sec", ascending=True, inplace=True)

            connections = []
            for _, row in group.iterrows():
                co2_cost_g = (distance_m/1000) * get_co2(row['stop_id'].split("_")[0])

                connections.append({
                    'departure_sec': row['departure_sec'], 
                    'travel_time_sec': row['travel_time_sec'],
                    'trip_id': row['trip_id'],
                    'route_id': row['route_id'],
                    'co2_cost_g': co2_cost_g,
                    'distance_m': distance_m
                })

            # Adiciona a aresta ao grafo
            G_transport.add_edge(u, v, 
                        type='transit', 
                        connections=connections,
                        avg_travel_time=group['travel_time_sec'].mean())

        self.G = G_transport

    def build_street_graph(self):
        dist_m = get_m_distance(self.geo_origem, self.geo_destino)

        G_walk=ox.graph_from_point((self.geo_origem.y, self.geo_origem.x), dist=dist_m,  network_type="walk")
        G_walk=ox.add_edge_speeds(G_walk)
        G_walk=ox.add_edge_travel_times(G_walk)

        self.G_walk=G_walk

    def add_user_points_to_graph(self, max_walk_meters: int = 1000):
        """
        Adiciona nós arbitrários (Origem e Destino do Utilizador) ao grafo e liga-os
        por arestas de caminhada às paragens GTFS mais próximas.
        """
        WALK_SPEED_KPH = 5.0
        SOURCE_NODE_ID = "USER_START"
        DESTINATION_NODE_ID = "USER_END"

        # Certifique-se de que os nós não existem antes de adicionar
        self.G.add_node(
            SOURCE_NODE_ID,
            y=self.geo_origem.y,
            x=self.geo_origem.x,
            name="Ponto de Partida",
            osmnx_node=ox.nearest_nodes(self.G_walk, self.geo_origem.x, self.geo_origem.y),
        )
        self.G.add_node(
            DESTINATION_NODE_ID,
            y=self.geo_destino.y,
            x=self.geo_destino.x,
            name="Ponto de Chegada",
            osmnx_node=ox.nearest_nodes(self.G_walk, self.geo_destino.x, self.geo_destino.y),
        )

        user_points = [
            (SOURCE_NODE_ID, (self.geo_origem.y, self.geo_origem.x)),
            (DESTINATION_NODE_ID, (self.geo_destino.y, self.geo_destino.x))
        ]

        # 2. Ligar cada ponto do utilizador às paragens mais próximas
        for user_id, user_coords in user_points:
            user_lat, user_lon = user_coords

            # Iterar apenas sobre os nós de paragem GTFS
            for stop_id, data in self.G.nodes(data=True):
                if stop_id in [SOURCE_NODE_ID, DESTINATION_NODE_ID]:
                    continue

                stop_lat, stop_lon = data['y'], data['x']

                distance_m = get_m_distance(Point(user_lon, user_lat), Point(stop_lon, stop_lat))

                if distance_m <= max_walk_meters:
                    walk_time_sec = math.ceil((distance_m / 1000) / WALK_SPEED_KPH * 3600)

                    # Para a Origem (SOURCE_NODE_ID -> Paragem): Permite acesso ao sistema
                    if user_id == SOURCE_NODE_ID:
                        self.G.add_edge(user_id, stop_id, 
                                type='walk', 
                                travel_time=walk_time_sec, 
                                distance_km=(distance_m / 1000),
                                co2_cost_g=0,
                                # Atributo para rastrear o exercício
                                walk_distance_km=(distance_m / 1000)) 

                    # Para o Destino (Paragem -> DESTINATION_NODE_ID): Permite sair do sistema
                    elif user_id == DESTINATION_NODE_ID:
                        self.G.add_edge(stop_id, user_id, 
                                type='walk', 
                                travel_time=walk_time_sec, 
                                distance_km=(distance_m / 1000),
                                co2_cost_g=0,
                                # Atributo para rastrear o exercício
                                walk_distance_km=(distance_m / 1000))

        self.origem_node_id = SOURCE_NODE_ID
        self.destino_node_id = DESTINATION_NODE_ID

    def add_osmnx_transfer_edges(self, max_dist_m=250, walk_speed_ms=1.1):
        """
        Cria arestas de transferência intermodal usando distâncias reais de ruas (OSMnx).

        Args:
            max_dist_m: Distância máxima de caminhada permitida em metros.
            walk_speed_ms: Velocidade média de caminhada (1.1 m/s ~ 4 km/h).
        """
        # 1. Preparar dados para a cKDTree (Busca rápida de vizinhança)
        # Filtramos apenas paragens que foram mapeadas com sucesso para a rede OSM
        stops_df = self.gtfs_feed.stops
        stops_df['osmnx_node'] = ox.nearest_nodes(self.G_walk, stops_df['stop_lon'], stops_df['stop_lat'])
        stops_df = stops_df.set_index('stop_id')

        self.stops_df = stops_df.copy()

        valid_stops = stops_df.dropna(subset=['osmnx_node', 'stop_lat', 'stop_lon'])
        node_coords = valid_stops[['stop_lat', 'stop_lon']].values
        node_ids = valid_stops.index.tolist()
        osm_mapping = valid_stops['osmnx_node'].to_dict()

        tree = cKDTree(node_coords)
        
        # Raio aproximado em graus para a busca inicial (mais eficiente que calcular tudo)
        radius_deg = (max_dist_m + 100) / 111000.0 
        pairs = tree.query_pairs(radius_deg)
        
        edges_added = 0
        print(f"Analisando {len(pairs)} pares candidatos para transferência real...")

        for i, j in pairs:
            u, v = node_ids[i], node_ids[j]
            
            # Filtro de Operador: Só transferimos entre redes diferentes (ex: STCP -> METRO)
            if u.split('_')[0] == v.split('_')[0]:
                continue

            # 2. Obter os nós correspondentes na rede de ruas
            u_osm = osm_mapping[u]
            v_osm = osm_mapping[v]

            try:
                # 3. Calcular a distância real de caminhada via NetworkX/OSMnx
                # Usamos o peso 'length' que a OSMnx guarda em cada aresta
                real_dist = nx.shortest_path_length(self.G_walk, u_osm, v_osm, weight='length')

                if real_dist <= max_dist_m:
                    # 4. Cálculo do Custo de Tempo
                    # Tempo de caminhada + Penalização fixa (3 min) para transbordo
                    walk_time_sec = (real_dist / walk_speed_ms) + 180

                    # Adicionar arestas bidirecionais ao grafo multimodal
                    edge_params = {
                        'type': 'walk',
                        'travel_time': walk_time_sec,
                        'distance_km': real_dist / 1000.0,
                        'co2_cost_g': 0.0,
                        'is_transfer': True
                    }
                    
                    self.G.add_edge(u, v, **edge_params)
                    self.G.add_edge(v, u, **edge_params)
                    edges_added += 1

            except (nx.NetworkXNoPath, nx.NodeNotFound):
                # Caso não exista caminho a pé (ex: barreiras físicas ou ilhas de rede)
                continue

        self.stops_df = stops_df

    def add_intermodal_transfer_edges(self, max_dist_meters=10, transfer_penalty_sec=300):
        """
        Cria ligações a pé entre nós de redes diferentes (Ex: METRO <-> STCP).
        Usa uma cKDTree para busca espacial ultra-rápida.
        """
        nodes_data = list(self.G.nodes(data=True))
        # Extrair coordenadas e IDs, filtrando apenas nós que têm lat/lon
        node_coords = []
        node_ids = []

        for node_id, data in nodes_data:
            if 'y' in data and 'x' in data:
                node_coords.append([data['y'], data['x']])
                node_ids.append(node_id)

        if not node_coords:
            return

        # Criar a árvore para busca espacial
        tree = cKDTree(node_coords)

        # Converter metros para graus aproximados (1 grau ~ 111km)
        radius_deg = max_dist_meters / 111000.0

        # Encontrar todos os pares de nós dentro do raio
        pairs = tree.query_pairs(radius_deg)

        edges_added = 0
        for i, j in pairs:
            u, v = node_ids[i], node_ids[j]

            # 1. FILTRO DE OPERADOR (Crucial para Performance)
            # Só criamos a aresta se os prefixos forem diferentes (ex: METRO_ vs STCP_)
            prefix_u = u.split('_')[0]
            prefix_v = v.split('_')[0]

            if prefix_u == prefix_v:
                continue # Ignora transferências entre o mesmo operador (já existem via rota)

            # 2. CÁLCULO DE DISTÂNCIA REAL
            lat1, lon1 = node_coords[i]
            lat2, lon2 = node_coords[j]
            dist_km =  get_km_distance(Point(lon1, lat1), Point(lon2, lat2))

            if dist_km <= (max_dist_meters / 1000.0):
                # 3. CÁLCULO DO TEMPO (Caminhada + Penalização)
                # Velocidade média de caminhada: 4 km/h
                walk_time = math.ceil((dist_km / 4.0) * 3600)

                # Adicionamos uma penalização fixa (ex: 3 min) para evitar transbordos triviais
                # que o utilizador não faria na vida real.
                total_transfer_time = walk_time + transfer_penalty_sec

                # 4. ADICIONAR ARESTAS (Bidirecionais)
                self.G.add_edge(u, v, 
                        type='walk', 
                        travel_time=total_transfer_time, 
                        co2_cost_g=0.0, 
                        distance_km=dist_km,
                        is_transfer=True)

                self.G.add_edge(v, u, 
                        type='walk', 
                        travel_time=total_transfer_time, 
                        co2_cost_g=0.0, 
                        distance_km=dist_km,
                        is_transfer=True)

                edges_added += 1
