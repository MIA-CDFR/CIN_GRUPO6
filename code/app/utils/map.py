import folium
import networkx as nx

def create_comparison_map_detailed(solutions, G_combined, G_osm, stops_df):
    if not solutions:
        return None

    # Configuração de Estilos por Modo
    # Metro: Vermelho/Sólido | Autocarro: Azul/Sólido | Caminhada: Cinza/Tracejado
    mode_styles = {
        'metro': {'color': '#e74c3c', 'dash': None, 'weight': 6, 'label': 'Metro'},
        'bus':   {'color': '#3498db', 'dash': None, 'weight': 6, 'label': 'Autocarro'},
        'walk':  {'color': '#7f8c8d', 'dash': '10, 10', 'weight': 4, 'label': 'Caminhada'}
    }

    # Selecionar as 3 categorias para camadas (como antes)
    best_routes = {
        "Mais Rápida": min(solutions, key=lambda s: s.total_time),
        "Mais Ecológica": min(solutions, key=lambda s: s.total_co2),
        "Mais Saudável": max(solutions, key=lambda s: s.total_walk_km)
    }

    m = folium.Map(location=[41.1579, -8.6291], zoom_start=13, tiles="cartodbpositron")

    for name, sol in best_routes.items():
        group = folium.FeatureGroup(name=name)
        path = sol.path # Lista de (node, info, time)

        for i in range(len(path) - 1):
            u_id, info_u, arrival_time = path[i]
            v_id, info_v, _ = path[i+1]
            
            edge_data = G_combined.get_edge_data(u_id, v_id).get(0)

            # 1. Determinar o Modo
            edge_type = edge_data.get('type', 'walk')
            if edge_type == 'transit':
                # Diferenciar Metro de Autocarro pelo ID da paragem
                mode = 'metro' if 'METRO' in str(u_id).upper() else 'bus'
            else:
                mode = 'walk'

            style = mode_styles[mode]

            # 2. Obter Geometria do Segmento
            if mode == 'walk':
                # Usa a rede de ruas para caminhada
                try:
                    if u_id == 'USER_START':
                        u_osm = G_combined.nodes[u_id]['osmnx_node']
                    else:
                        u_osm = stops_df.loc[u_id, 'osmnx_node']

                    if v_id == 'USER_END':
                        v_osm = G_combined.nodes[v_id]['osmnx_node']
                    else:
                        v_osm = stops_df.loc[v_id, 'osmnx_node']

                    osm_path = nx.shortest_path(G_osm, u_osm, v_osm, weight='length')
                    segment_coords = [(G_osm.nodes[n]['y'], G_osm.nodes[n]['x']) for n in osm_path]
                except:
                    try:
                        # Fallback linha reta
                        u_lat, u_lon = stops_df.loc[u_id, ['stop_lat', 'stop_lon']]
                        v_lat, v_lon = stops_df.loc[v_id, ['stop_lat', 'stop_lon']]
                        segment_coords = [(u_lat, u_lon), (v_lat, v_lon)]
                    except:
                        segment_coords = [(G_combined.nodes[u_id]['y'], G_combined.nodes[u_id]['x']), (G_combined.nodes[v_id]['y'], G_combined.nodes[v_id]['x'])]
            else:
                # Linha direta entre paragens para transporte público
                u_lat, u_lon = stops_df.loc[u_id, ['stop_lat', 'stop_lon']]
                v_lat, v_lon = stops_df.loc[v_id, ['stop_lat', 'stop_lon']]
                segment_coords = [(u_lat, u_lon), (v_lat, v_lon)]

            # 3. Desenhar o Segmento no Mapa
            folium.PolyLine(
                segment_coords,
                color=style['color'],
                weight=style['weight'],
                dash_array=style['dash'],
                opacity=0.8,
                tooltip=f"Modo: {style['label']}"
            ).add_to(group)

            # Marcadores especiais para Origem e Destino
            if u_id == 'USER_START':
                folium.Marker(
                    (G_combined.nodes[u_id]['y'], G_combined.nodes[u_id]['x']), popup="Início", 
                    icon=folium.Icon(color="lightgray", icon='play', prefix='fa')
                ).add_to(group)
            elif v_id == 'USER_END':
                folium.Marker(
                    (G_combined.nodes[v_id]['y'], G_combined.nodes[v_id]['x']), popup="Fim", 
                    icon=folium.Icon(color="green", icon='flag', prefix='fa')
                ).add_to(group)

            # 4. Adicionar Marcadores de Paragem (Apenas para Metro e Autocarro)
            if mode != 'walk':
                for sid in [u_id, v_id]:
                    if sid in stops_df.index:
                        s_data = stops_df.loc[sid]
                        is_metro = 'METRO' in str(sid).upper()
                        popup_text = f"<b>{s_data['stop_name']}</b><br>Modo: {'Metro' if is_metro else 'Autocarro'}<br>Chegada: {arrival_time}"
                        folium.CircleMarker(
                            [s_data['stop_lat'], s_data['stop_lon']],
                            radius=3, color=style['color'], fill=True, fill_color='white',
                            popup=folium.Popup(popup_text, max_width=200)
                        ).add_to(group)

        group.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m