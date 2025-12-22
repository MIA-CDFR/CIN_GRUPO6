import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import pandas as pd
import gtfs_kit as gk


FEED_METRO = gk.read_feed(f"{module_path}/feeds/gtfs_metro", dist_units="km")
FEED_STCP = gk.read_feed(f"{module_path}/feeds/gtfs_stcp", dist_units="km")


def get_filtered_multimodal_feed(geo_origem, geo_destino, buffer_km=1.0):
    """
    Combina e filtra dois feeds (Metro e STCP) concatenando os DataFrames do Pandas
    e garantindo a unicidade dos IDs com prefixos.
    """
    # 1. Definir a Bounding Box
    lat_min = min(geo_origem.y, geo_destino.y) - (buffer_km / 111.0)
    lat_max = max(geo_origem.y, geo_destino.y) + (buffer_km / 111.0)
    lon_min = min(geo_origem.x, geo_destino.x) - (buffer_km / 111.0)
    lon_max = max(geo_origem.x, geo_destino.x) + (buffer_km / 111.0)

    def prepare_sub_df(feed, prefix):
        # Filtrar paragens geograficamente
        m_stops = (feed.stops.stop_lat >= lat_min) & (feed.stops.stop_lat <= lat_max) & \
                  (feed.stops.stop_lon >= lon_min) & (feed.stops.stop_lon <= lon_max)

        stops_df = feed.stops[m_stops].copy()
        relevant_stops = set(stops_df['stop_id'])

        # Filtrar stop_times e trips que passam nestas paragens
        st_df = feed.stop_times[feed.stop_times['stop_id'].isin(relevant_stops)].copy()
        relevant_trips = set(st_df['trip_id'])

        trips_df = feed.trips[feed.trips['trip_id'].isin(relevant_trips)].copy()
        relevant_routes = set(trips_df['route_id'])

        routes_df = feed.routes[feed.routes['route_id'].isin(relevant_routes)].copy()

        # Aplicar Prefixos para evitar colisões entre Metro e STCP
        # (Fundamental para o grafo não misturar as redes)
        stops_df['stop_id'] = prefix + "_" + stops_df['stop_id'].astype(str)
        st_df['stop_id'] = prefix + "_" + st_df['stop_id'].astype(str)
        st_df['trip_id'] = prefix + "_" + st_df['trip_id'].astype(str)
        trips_df['trip_id'] = prefix + "_" + trips_df['trip_id'].astype(str)
        trips_df['route_id'] = prefix + "_" + trips_df['route_id'].astype(str)
        routes_df['route_id'] = prefix + "_" + routes_df['route_id'].astype(str)
        
        return {
            'stops': stops_df,
            'stop_times': st_df,
            'trips': trips_df,
            'routes': routes_df
        }

    # 2. Obter dicionários de DataFrames filtrados
    data_metro = prepare_sub_df(FEED_METRO, "METRO")
    data_stcp = prepare_sub_df(FEED_STCP, "STCP")

    # 3. Concatenar manualmente as tabelas
    combined_data = {}
    for table in ['stops', 'stop_times', 'trips', 'routes']:
        combined_data[table] = pd.concat([data_metro[table], data_stcp[table]], ignore_index=True)

    # 4. Criar um novo objeto Feed (usando o esqueleto de um dos originais)
    # Nota: Criamos um feed vazio ou clonamos um para manter a estrutura do gtfs-kit
    combined_feed = gk.Feed(
        dist_units=FEED_METRO.dist_units,
        agency=pd.concat([FEED_METRO.agency, FEED_STCP.agency], ignore_index=True),
        stops=combined_data['stops'],
        routes=combined_data['routes'],
        trips=combined_data['trips'],
        stop_times=combined_data['stop_times'],
        calendar=pd.concat([FEED_METRO.calendar, FEED_STCP.calendar], ignore_index=True) if FEED_METRO.calendar is not None else None
    )

    print(f"Fusão concluída: {len(combined_feed.stops)} paragens no corredor intermodal.")

    return combined_feed
