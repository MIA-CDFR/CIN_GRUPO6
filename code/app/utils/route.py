def find_next_departure_cost(current_time_sec: int, connections: list):
    """
    Procura a próxima viagem disponível numa aresta de trânsito.
    Retorna: (tempo_total_ate_chegada, tempo_de_viagem, custo_co2, trip_id)
    """
    # Nota: Se 'connections' estiver ordenado por departure_sec, 
    # podemos usar bisect para ser ainda mais rápido.
    for conn in connections:
        if conn['departure_sec'] >= current_time_sec:
            wait_time = conn['departure_sec'] - current_time_sec
            travel_time = conn['travel_time_sec']
            total_time_on_edge = wait_time + travel_time
            
            return total_time_on_edge, travel_time, conn['co2_cost_g'], conn['trip_id']
            
    return float('inf'), 0, 0.0, None

def get_edge_costs(data, current_time_sec):
    """
    Calcula os custos de atravessar a aresta (u, v) no momento 'current_time_sec'.
    
    Retorna:
    - time_cost (segundos): Tempo total incluindo espera.
    - co2_cost (gramas): Emissão de CO2.
    - walk_km (quilómetros): Distância percorrida a pé para o objetivo de exercício.
    - trip_info (string): Identificador da viagem ou tipo 'walk'.
    """
    
    # CENÁRIO 1: Aresta de Caminhada (Transferência ou Acesso)
    if data['type'] == 'walk':
        time_cost = data['travel_time']
        
        # SE for uma transferência entre paragens, podemos adicionar um 
        # "custo psicológico" de 2 minutos para evitar transferências excessivas
        if data.get('is_transfer', False):
            time_cost += 120 # + 2 minutos virtuais

        return time_cost, 0.0, data.get('walk_distance_km', 0.0), 'transfer'
    
    # CENÁRIO 2: Aresta de Trânsito (Metro ou Autocarro)
    elif data['type'] == 'transit':
        connections = data['connections']
        
        total_time, travel_time, co2_cost, trip_id = find_next_departure_cost(
            current_time_sec, connections
        )
        
        if total_time == float('inf'):
            return float('inf'), float('inf'), 0.0, 'unavailable'
        
        # No trânsito, a distância percorrida a pé é ZERO
        walk_km = 0.0
        return total_time, co2_cost, walk_km, trip_id
    
    return float('inf'), float('inf'), 0.0, 'error'