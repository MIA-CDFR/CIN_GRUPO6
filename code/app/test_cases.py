# -*- coding: utf-8 -*-
"""
Conjunto de Casos de Teste para Avaliação de Algoritmos de Roteamento Multimodal
Área Metropolitana do Porto

Estrutura: Lista de dicionários com os parâmetros de cada caso de teste
Cada caso inclui origem, destino, hora de partida e metadados para validação
"""

# ============================================================================
# GRUPO 1: CASOS TRIVIAIS / MUITO SIMPLES (Validação Básica)
# ============================================================================

TEST_CASES = [
    {
        "id": "TC-1.1",
        "name": "Distância Muito Curta (Walking Only)",
        "origem": "Livraria Bertrand, Porto",
        "destino": "Torre dos Clérigos, Porto",
        "start_time": "09:00:00",
        "complexity": "trivial",
        "expected_distance_km": 0.3,
        "expected_duration_sec": 180,
        "description": "Apenas caminhada, distância < 500m. Sem opções de transporte.",
        "metrics": {
            "expected_walk_km_min": 0.2,
            "expected_walk_km_max": 0.5,
            "num_solutions_expected": "1",
            "transport_used": "walk_only",
        }
    },
    
    {
        "id": "TC-1.2",
        "name": "Transporte Direto (Single Hop)",
        "origem": "Estação de S. Bento, Porto",
        "destino": "Matosinhos, Porto",
        "start_time": "10:00:00",
        "complexity": "trivial",
        "expected_distance_km": 6.0,
        "expected_duration_sec": 900,
        "description": "Uma única linha de autocarro, sem transferências obrigatórias.",
        "metrics": {
            "num_solutions_expected": "2-3",
            "max_transfers": 0,
            "transport_used": "bus_only",
        }
    },

    # ============================================================================
    # GRUPO 2: CASOS SIMPLES (Baixa Complexidade)
    # ============================================================================

    {
        "id": "TC-2.1",
        "name": "Distância Curta com 1 Transferência (Off-Peak)",
        "origem": "Mercado do Bolhão, Porto",
        "destino": "Ribeira, Porto",
        "start_time": "14:30:00",
        "complexity": "low",
        "expected_distance_km": 2.5,
        "expected_duration_sec": 1200,
        "description": "Distância curta, 1 transferência, horário off-peak.",
        "metrics": {
            "num_solutions_expected": "3-5",
            "max_wait_time_sec": 600,
            "expected_co2_range": (30, 80),
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-2.2",
        "name": "Distância Média com Caminhada (Peak Hour)",
        "origem": "Casa da Música, Porto",
        "destino": "Livraria Lello, Porto",
        "start_time": "08:30:00",
        "complexity": "low",
        "expected_distance_km": 3.5,
        "expected_duration_sec": 1500,
        "description": "Distância média, múltiplas rotas possíveis, hora de pico.",
        "metrics": {
            "num_solutions_expected": "4-8",
            "expected_walk_km_min": 0.5,
            "expected_walk_km_max": 2.0,
            "transport_used": "mixed",
        }
    },

    # ============================================================================
    # GRUPO 3: CASOS MODERADOS (Média Complexidade)
    # ============================================================================

    {
        "id": "TC-3.1",
        "name": "Distância Longa com 2 Transferências",
        "origem": "Estação de Santa Apolónia, Porto",
        "destino": "Francelos, Vila Nova de Gaia",
        "start_time": "11:00:00",
        "complexity": "medium",
        "expected_distance_km": 12.0,
        "expected_duration_sec": 2400,
        "description": "Rota interurbana com 2 transferências. Trade-off tempo vs CO2.",
        "metrics": {
            "num_solutions_expected": "5-10",
            "max_transfers": 2,
            "expected_co2_range": (100, 300),
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-3.2",
        "name": "Origem/Destino em Periferia (Baixa Conectividade)",
        "origem": "Maia, Porto",
        "destino": "Hospital de São João, Porto",
        "start_time": "09:30:00",
        "complexity": "medium",
        "expected_distance_km": 12.0,
        "expected_duration_sec": 2700,
        "description": "Origem periférica com conectividade reduzida. Problema realista.",
        "metrics": {
            "num_solutions_expected": "3-6",
            "expected_walk_km_min": 0.8,
            "connectivity_limited": True,
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-3.3",
        "name": "Caso Híbrido: Tempo vs Sustentabilidade",
        "origem": "Exponor, Matosinhos",
        "destino": "Serralves, Porto",
        "start_time": "13:00:00",
        "complexity": "medium",
        "expected_distance_km": 5.0,
        "expected_duration_sec": 1800,
        "description": "Pequena distância com alternativas claras: rápido (autocarro) vs eco (metro).",
        "metrics": {
            "num_solutions_expected": "4-8",
            "pareto_frontier_spread": "high",
            "eco_vs_fast_time_diff": 300,
            "transport_used": "mixed",
        }
    },

    # ============================================================================
    # GRUPO 4: CASOS COMPLEXOS (Alta Complexidade)
    # ============================================================================

    {
        "id": "TC-4.1",
        "name": "Distância Longa com Múltiplas Alternativas",
        "origem": "Maia, Porto",
        "destino": "Espinho, Aveiro",
        "start_time": "07:00:00",
        "complexity": "high",
        "expected_distance_km": 35.0,
        "expected_duration_sec": 3600,
        "description": "Rota longa dentro da área metropolitana com muitas combinações possíveis.",
        "metrics": {
            "num_solutions_expected": "6-12",
            "max_transfers": 2,
            "expected_co2_range": (200, 600),
            "computation_time_limit_sec": 30,
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-4.2",
        "name": "Rede Complexa com Muitos Hubs",
        "origem": "Campanhã, Porto",
        "destino": "Gaia Centre, Vila Nova de Gaia",
        "start_time": "17:30:00",
        "complexity": "high",
        "expected_distance_km": 8.0,
        "expected_duration_sec": 2400,
        "description": "Hora de pico com muitos nós intermediários. Teste de otimização temporal.",
        "metrics": {
            "num_solutions_expected": "8-15",
            "wait_time_variance": "high",
            "expected_walk_km_min": 0.3,
            "expected_walk_km_max": 3.0,
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-4.3",
        "name": "Caso Extremo: Máxima Dissimilaridade entre Algoritmos",
        "origem": "Parque da Cidade, Porto",
        "destino": "Vilar do Conde, Porto",
        "start_time": "06:00:00",
        "complexity": "high",
        "expected_distance_km": 18.0,
        "expected_duration_sec": 3000,
        "description": "Madrugada com conectividade reduzida. Testa exploração criativa de ACO.",
        "metrics": {
            "num_solutions_expected": "2-4",
            "algorithm_divergence_expected": "high",
            "aco_advantage_expected": True,
            "transport_used": "limited",
        }
    },
    
    {
        "id": "TC-4.4",
        "name": "Transporte de Longa Distância (Via Rápida)",
        "origem": "Campanhã, Porto",
        "destino": "Aveiro (fronteira metropolitana)",
        "start_time": "09:15:00",
        "complexity": "high",
        "expected_distance_km": 40.0,
        "expected_duration_sec": 4200,
        "description": "Utilização de via rápida/comboio. Múltiplas alternativas de transporte.",
        "metrics": {
            "num_solutions_expected": "5-10",
            "max_transfers": 2,
            "transport_used": "mixed_long_distance",
        }
    },
    
    {
        "id": "TC-4.5",
        "name": "Múltiplas Opções de Paragens Próximas",
        "origem": "Bolhão, Porto",
        "destino": "Príncipe Real, Porto",
        "start_time": "10:45:00",
        "complexity": "high",
        "expected_distance_km": 2.5,
        "expected_duration_sec": 900,
        "description": "Origem com múltiplas paragens próximas; testa desambiguação.",
        "metrics": {
            "num_solutions_expected": "10+",
            "high_branching_factor": True,
            "transport_used": "walk_and_transit",
        }
    },

    # ============================================================================
    # GRUPO 5: CASOS ESPECIAIS (Edge Cases e Validação)
    # ============================================================================

    {
        "id": "TC-5.1",
        "name": "Domínio Óbvio (Solução Única)",
        "origem": "Rua Clérigos, Porto",
        "destino": "Torre dos Clérigos, Porto",
        "start_time": "12:00:00",
        "complexity": "special",
        "expected_distance_km": 0.1,
        "expected_duration_sec": 60,
        "description": "Origem e destino muito próximos. Apenas uma solução válida.",
        "metrics": {
            "num_solutions_expected": "1",
            "all_algorithms_same_solution": True,
            "transport_used": "walk_only",
        }
    },
    
    {
        "id": "TC-5.2",
        "name": "Teste de Diversidade Pareto",
        "origem": "Bolhão, Porto",
        "destino": "Gaia Centre, Vila Nova de Gaia",
        "start_time": "10:00:00",
        "complexity": "special",
        "expected_distance_km": 7.0,
        "expected_duration_sec": 1800,
        "description": "Caso onde há múltiplas rotas com trade-offs claros.",
        "metrics": {
            "num_solutions_expected": "8-15",
            "validate_pareto_frontier": True,
            "metric_spread": {
                "time_spread": "min < 20min < max",
                "co2_spread": "min < 100g < max",
                "walk_spread": "min < 2km < max",
            },
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-5.3",
        "name": "Teste de Convergência (A* vs Dijkstra)",
        "origem": "Estação de S. Bento, Porto",
        "destino": "Vila Nova de Gaia, Vila Nova de Gaia",
        "start_time": "15:00:00",
        "complexity": "special",
        "expected_distance_km": 4.0,
        "expected_duration_sec": 1200,
        "description": "Valida que A* e Dijkstra encontram fronteiras Pareto equivalentes.",
        "metrics": {
            "verify_astar_dijkstra_equivalence": True,
            "allowed_solution_difference": 1,
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-5.4",
        "name": "Soluções com CO2 Muito Diferentes",
        "origem": "Livraria Lello, Porto",
        "destino": "Candal, Vila Nova de Gaia",
        "start_time": "14:00:00",
        "complexity": "special",
        "expected_distance_km": 6.0,
        "expected_duration_sec": 1500,
        "description": "Rota onde há clara troca entre transporte rápido (alto CO2) vs lento (baixo CO2).",
        "metrics": {
            "num_solutions_expected": "5-10",
            "verify_co2_spread": True,
            "co2_spread_factor": "> 2x",
            "transport_used": "mixed",
        }
    },
    
    {
        "id": "TC-5.5",
        "name": "Teste de ACO em Ambiente Stochástico",
        "origem": "Clérigos, Porto",
        "destino": "Boavista, Porto",
        "start_time": "16:30:00",
        "complexity": "special",
        "expected_distance_km": 4.5,
        "expected_duration_sec": 1200,
        "description": "Contexto onde ACO pode encontrar soluções diferentes em múltiplas execuções.",
        "metrics": {
            "num_solutions_expected": "5-12",
            "stochastic_variance_expected": True,
            "aco_vs_deterministic_spread": "high",
            "transport_used": "mixed",
        }
    },

    # ============================================================================
    # GRUPO 6: CASOS EXTREMOS (Testes de Robustez)
    # ============================================================================

    {
        "id": "TC-6.1",
        "name": "Origem e Destino no Mesmo Local",
        "origem": "Casa da Música, Porto",
        "destino": "Casa da Música, Porto",
        "start_time": "11:00:00",
        "complexity": "extreme",
        "expected_distance_km": 0.0,
        "expected_duration_sec": 0,
        "description": "Validação de edge case: origem = destino.",
        "metrics": {
            "should_return": "empty_or_single_solution",
            "expected_time": 0,
            "transport_used": "none",
        }
    },
    
    {
        "id": "TC-6.2",
        "name": "Horário Noturno (Baixíssima Conectividade)",
        "origem": "Estação de S. Bento, Porto",
        "destino": "Ribeira, Porto",
        "start_time": "23:30:00",
        "complexity": "extreme",
        "expected_distance_km": 1.5,
        "expected_duration_sec": 1800,
        "description": "Madrugada com serviços de transporte mínimos.",
        "metrics": {
            "num_solutions_expected": "1-2",
            "forced_walking": True,
            "transport_unavailable": True,
            "transport_used": "walk_only",
        }
    },
    
    {
        "id": "TC-6.3",
        "name": "Limite de Tempo de Espera Muito Restritivo",
        "origem": "Príncipe Real, Porto",
        "destino": "Miragaia, Porto",
        "start_time": "23:45:00",
        "complexity": "extreme",
        "expected_distance_km": 1.2,
        "expected_duration_sec": 1200,
        "description": "Muito tarde à noite; transporte público praticamente nenhum.",
        "metrics": {
            "num_solutions_expected": "0-1",
            "only_walking_viable": True,
            "transport_used": "none_or_walk_only",
        }
    },
    
    {
        "id": "TC-6.4",
        "name": "Origem em Localização Isolada",
        "origem": "Serralves, Porto",
        "destino": "Campanhã, Porto",
        "start_time": "05:00:00",
        "complexity": "extreme",
        "expected_distance_km": 15.0,
        "expected_duration_sec": 3600,
        "description": "Origem numa zona periférica/isolada, muito cedo de manhã.",
        "metrics": {
            "num_solutions_expected": "1-3",
            "low_connectivity": True,
            "forced_walking_to_first_stop": True,
            "transport_used": "limited",
        }
    },

    # ============================================================================
    # CASOS ADICIONAIS PARA COBERTURA (Aumentar para 22)
    # ============================================================================

    {
        "id": "TC-7.2",
        "name": "Transferência Rápida (Hub Principal)",
        "origem": "Bolhão, Porto",
        "destino": "São Bento, Porto",
        "start_time": "08:00:00",
        "complexity": "low",
        "expected_distance_km": 1.0,
        "expected_duration_sec": 600,
        "description": "Entre dois hubs principais; transferência directa esperada.",
        "metrics": {
            "num_solutions_expected": "2-3",
            "expected_walk_km_min": 0.1,
            "expected_walk_km_max": 0.5,
            "transport_used": "transit_only",
        }
    },
]


class TestCaseEvaluator:
    """
    Classe para executar e avaliar casos de teste
    """
    
    @staticmethod
    def get_by_complexity(complexity_level: str) -> list:
        """Retorna casos de teste por nível de complexidade"""
        return [tc for tc in TEST_CASES if tc["complexity"] == complexity_level]
    
    @staticmethod
    def get_by_id(test_id: str) -> dict:
        """Retorna um caso de teste específico por ID"""
        for tc in TEST_CASES:
            if tc["id"] == test_id:
                return tc
        return None
    
    @staticmethod
    def get_all_names() -> list:
        """Lista todos os nomes dos casos de teste"""
        return [(tc["id"], tc["name"]) for tc in TEST_CASES]
    
    @staticmethod
    def validate_solution(solution, test_case: dict) -> tuple:
        """
        Valida se uma solução satisfaz os critérios esperados do caso de teste
        
        Retorna: (is_valid: bool, violations: List[str])
        """
        violations = []
        
        # Validar tempo
        if "expected_duration_sec" in test_case:
            expected = test_case["expected_duration_sec"]
            tolerance = max(expected * 0.2, 60)  # ±20% ou 1 minuto mínimo
            if not (expected - tolerance <= solution.total_time <= expected + tolerance):
                violations.append(
                    f"⚠️ Tempo fora do esperado: {solution.total_time}s vs {expected}s ±{tolerance}s"
                )
        
        # Validar CO2 (se range definido)
        if "expected_co2_range" in test_case.get("metrics", {}):
            co2_min, co2_max = test_case["metrics"]["expected_co2_range"]
            if not (co2_min <= solution.total_co2 <= co2_max * 1.2):  # 20% tolerância acima
                violations.append(
                    f"⚠️ CO2 fora do range: {solution.total_co2:.1f}g vs [{co2_min}, {co2_max}]g"
                )
        
        # Validar caminhada (se range definido)
        if "expected_walk_km_min" in test_case.get("metrics", {}):
            walk_min = test_case["metrics"].get("expected_walk_km_min", 0)
            walk_max = test_case["metrics"].get("expected_walk_km_max", 100)
            if not (walk_min - 0.1 <= solution.total_walk_km <= walk_max + 0.5):
                violations.append(
                    f"⚠️ Caminhada fora do range: {solution.total_walk_km:.2f}km vs [{walk_min}, {walk_max}]km"
                )
        
        return len(violations) == 0, violations
    
    @staticmethod
    def check_pareto_frontier(solutions: list) -> bool:
        """
        Verifica se o conjunto de soluções é uma fronteira Pareto válida.
        Retorna True se nenhuma solução domina outra.
        """
        if not solutions:
            return True
        
        for i, sol_a in enumerate(solutions):
            for j, sol_b in enumerate(solutions):
                if i != j:
                    # Verificar se sol_a domina sol_b
                    if (sol_a.total_time <= sol_b.total_time and
                        sol_a.total_co2 <= sol_b.total_co2 and
                        sol_a.total_walk_km >= sol_b.total_walk_km and
                        (sol_a.total_time < sol_b.total_time or
                         sol_a.total_co2 < sol_b.total_co2 or
                         sol_a.total_walk_km > sol_b.total_walk_km)):
                        return False
        return True
    
    @staticmethod
    def print_test_summary():
        """Imprime resumo de todos os casos de teste"""
        print("\n" + "="*100)
        print("CASOS DE TESTE DISPONÍVEIS - ÁREA METROPOLITANA DO PORTO")
        print("="*100 + "\n")
        
        by_complexity = {}
        for tc in TEST_CASES:
            complexity = tc["complexity"]
            if complexity not in by_complexity:
                by_complexity[complexity] = []
            by_complexity[complexity].append(tc)
        
        complexity_order = ["trivial", "low", "medium", "high", "special", "extreme"]
        
        for complexity in complexity_order:
            if complexity not in by_complexity:
                continue
            
            cases = by_complexity[complexity]
            emoji_map = {
                "trivial": "🟢",
                "low": "🟡",
                "medium": "🟠",
                "high": "🔴",
                "special": "🔵",
                "extreme": "⚫"
            }
            emoji = emoji_map.get(complexity, "")
            
            print(f"\n{emoji} [{complexity.upper()}] - {len(cases)} casos\n")
            for tc in cases:
                print(f"  {tc['id']}: {tc['name']}")
                print(f"      Origem: {tc['origem']}")
                print(f"      Destino: {tc['destino']}")
                print(f"      Dist. esperada: {tc['expected_distance_km']}km")
                print(f"      Tempo esperado: {tc['expected_duration_sec']//60}min")
                print(f"      Descrição: {tc['description']}")
                print()
    
    @staticmethod
    def get_statistics():
        """Retorna estatísticas gerais dos casos de teste"""
        stats = {
            "total_cases": len(TEST_CASES),
            "by_complexity": {},
            "avg_distance_km": 0,
            "avg_duration_sec": 0,
            "metropolitan_area": "Porto Metropolitan Area (Porto, Vila Nova de Gaia, Maia, Matosinhos, Espinho, Vilar do Conde)"
        }
        
        total_dist = 0
        total_duration = 0
        
        for complexity in ["trivial", "low", "medium", "high", "special", "extreme"]:
            count = len([tc for tc in TEST_CASES if tc["complexity"] == complexity])
            stats["by_complexity"][complexity] = count
        
        for tc in TEST_CASES:
            total_dist += tc["expected_distance_km"]
            total_duration += tc["expected_duration_sec"]
        
        stats["avg_distance_km"] = total_dist / len(TEST_CASES)
        stats["avg_duration_sec"] = total_duration / len(TEST_CASES)
        
        return stats


if __name__ == "__main__":
    # Script de teste principal
    print("\n🧪 SISTEMA DE TESTES - ROTEAMENTO MULTIMODAL PORTO\n")
    
    TestCaseEvaluator.print_test_summary()
    
    stats = TestCaseEvaluator.get_statistics()
    print("\n" + "="*100)
    print("ESTATÍSTICAS GERAIS")
    print("="*100)
    print(f"Total de casos: {stats['total_cases']}")
    print(f"Distância média: {stats['avg_distance_km']:.1f}km")
    print(f"Duração média: {int(stats['avg_duration_sec']//60)}min")
    print(f"Cobertura geográfica: {stats['metropolitan_area']}")
    print(f"\nDistribuição por complexidade:")
    for complexity, count in stats['by_complexity'].items():
        print(f"  {complexity:10s}: {count:2d} casos")
    print("\n" + "="*100 + "\n")
