"""
Framework de Avaliação Comparativa dos Algoritmos

Executa casos de teste e compara desempenho dos 3 algoritmos:
- A* Multi-Objetivo
- Dijkstra Multi-Label
- ACO (Ant Colony Optimization)
"""

import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

import time
import json
from dataclasses import dataclass, asdict
from typing import List, Dict
from app.services.graph import GraphRoute
from app.services.algoritms.a_star import optimized_multi_objective_routing
from app.services.algoritms.dijkstra import dijkstra_multi_objective
from app.services.algoritms.aco import aco_optimized_routing
from app.utils.time import time_to_seconds
from app.test_cases import TestCaseEvaluator


@dataclass
class AlgorithmMetrics:
    """Métricas de desempenho de um algoritmo"""
    algorithm_name: str
    execution_time_sec: float
    num_solutions: int
    frontier_size: int
    best_time_sec: float
    best_co2_g: float
    best_walk_km: float
    avg_time_sec: float
    avg_co2_g: float
    avg_walk_km: float
    solutions: List = None  # Lista de objetos Solution


@dataclass
class TestCaseResult:
    """Resultado da execução de um caso de teste"""
    test_case_name: str
    test_case_complexity: str
    origin: str
    destination: str
    start_time: str
    astar_metrics: AlgorithmMetrics
    dijkstra_metrics: AlgorithmMetrics
    aco_metrics: AlgorithmMetrics
    validation_passed: bool
    notes: str = ""


class ComparativeEvaluator:
    """
    Framework para avaliação comparativa dos algoritmos
    """

    def __init__(self):
        self.results: List[TestCaseResult] = []

    def run_single_test(self, test_case: Dict, verbose: bool = True) -> TestCaseResult:
        """
        Executa um único caso de teste com os 3 algoritmos
        
        Returns: TestCaseResult com métricas de todos os algoritmos
        """

        print(f"\n{'='*80}")
        print(f"Executando: {test_case['name']}")
        print(f"{'='*80}")
        print(f"Origem: {test_case['origem']}")
        print(f"Destino: {test_case['destino']}")
        print(f"Hora: {test_case['start_time']}")
        print(f"Complexidade: {test_case['complexity']}\n")

        try:
            # 1. Construir grafo
            print("[1/4] Construindo grafo multimodal...")
            graph = GraphRoute(
                origem=test_case["origem"],
                destino=test_case["destino"]
            )
            start_sec = time_to_seconds(test_case["start_time"])
            print("✓ Grafo construído\n")

            # 2. Executar A*
            print("[2/4] Executando A* Multi-Objetivo...")
            astar_metrics = self._run_algorithm(
                algorithm_func=optimized_multi_objective_routing,
                graph=graph.G,
                source=graph.origem_node_id,
                destination=graph.destino_node_id,
                start_time=start_sec,
                name="A* Multi-Objetivo"
            )

            # 3. Executar Dijkstra
            print("[3/4] Executando Dijkstra Multi-Label...")
            dijkstra_metrics = self._run_algorithm(
                algorithm_func=dijkstra_multi_objective,
                graph=graph.G,
                source=graph.origem_node_id,
                destination=graph.destino_node_id,
                start_time=start_sec,
                name="Dijkstra Multi-Label"
            )

            # 4. Executar ACO
            print("[4/4] Executando ACO...")
            aco_metrics = self._run_algorithm(
                algorithm_func=aco_optimized_routing,
                graph=graph.G,
                source=graph.origem_node_id,
                destination=graph.destino_node_id,
                start_time=start_sec,
                name="ACO"
            )

            # Validação
            validation_passed = self._validate_results(
                test_case, astar_metrics, dijkstra_metrics, aco_metrics
            )

            # Criar resultado
            result = TestCaseResult(
                test_case_name=test_case["name"],
                test_case_complexity=test_case["complexity"],
                origin=test_case["origem"],
                destination=test_case["destino"],
                start_time=test_case["start_time"],
                astar_metrics=astar_metrics,
                dijkstra_metrics=dijkstra_metrics,
                aco_metrics=aco_metrics,
                validation_passed=validation_passed
            )

            self.results.append(result)
            return result

        except Exception as e:
            print(f"\n❌ ERRO ao executar caso de teste: {str(e)}")
            return None

    def _run_algorithm(self, algorithm_func, graph, source, destination, 
                      start_time, name: str) -> AlgorithmMetrics:
        """
        Executa um algoritmo e coleta métricas
        """
        start_time_exec = time.time()

        try:
            solutions = algorithm_func(graph, source, destination, start_time)
            elapsed = time.time() - start_time_exec

            if not solutions:
                print(f"  ⚠️  {name}: Sem soluções encontradas")
                return AlgorithmMetrics(
                    algorithm_name=name,
                    execution_time_sec=elapsed,
                    num_solutions=0,
                    frontier_size=0,
                    best_time_sec=float('inf'),
                    best_co2_g=float('inf'),
                    best_walk_km=0.0,
                    avg_time_sec=0.0,
                    avg_co2_g=0.0,
                    avg_walk_km=0.0,
                    solutions=[]
                )

            # Calcular estatísticas
            times = [s.total_time for s in solutions]
            co2s = [s.total_co2 for s in solutions]
            walks = [s.total_walk_km for s in solutions]

            metrics = AlgorithmMetrics(
                algorithm_name=name,
                execution_time_sec=elapsed,
                num_solutions=len(solutions),
                frontier_size=len(solutions),
                best_time_sec=min(times),
                best_co2_g=min(co2s),
                best_walk_km=max(walks),
                avg_time_sec=sum(times) / len(times),
                avg_co2_g=sum(co2s) / len(co2s),
                avg_walk_km=sum(walks) / len(walks),
                solutions=solutions
            )

            print(f"  ✓ {name}:")
            print(f"    - Soluções: {len(solutions)}")
            print(f"    - Tempo exec: {elapsed:.2f}s")
            print(f"    - Melhor tempo: {min(times)/60:.1f} min")
            print(f"    - Melhor CO2: {min(co2s):.1f}g")
            print(f"    - Máx caminhada: {max(walks):.2f}km\n")

            return metrics

        except Exception as e:
            print(f"  ❌ ERRO em {name}: {str(e)}\n")
            return None

    def _validate_results(self, test_case, astar, dijkstra, aco) -> bool:
        """
        Valida que as soluções cumprem os critérios esperados
        """
        # Simplificado: validar que há soluções
        if astar.num_solutions == 0 and dijkstra.num_solutions == 0 and aco.num_solutions == 0:
            return False
        
        return True

    def print_comparison_table(self):
        """
        Imprime tabela comparativa de todos os resultados
        """
        if not self.results:
            print("Nenhum resultado para comparar.")
            return

        print("\n" + "="*120)
        print("TABELA COMPARATIVA - RESUMO DE TODOS OS CASOS")
        print("="*120 + "\n")

        print(f"{'Caso':<40} {'Complexidade':<12} {'A*':<18} {'Dijkstra':<18} {'ACO':<18}")
        print(f"{'':40} {'':12} {'Soluções|Tempo':<18} {'Soluções|Tempo':<18} {'Soluções|Tempo':<18}")
        print("-"*120)

        for result in self.results:
            print(f"{result.test_case_name[:40]:<40} {result.test_case_complexity:<12} ", end="")

            # A*
            if result.astar_metrics:
                print(f"{result.astar_metrics.num_solutions}|{result.astar_metrics.execution_time_sec:.1f}s", end="".ljust(18))
            else:
                print("ERROR".ljust(18), end="")

            # Dijkstra
            if result.dijkstra_metrics:
                print(f"{result.dijkstra_metrics.num_solutions}|{result.dijkstra_metrics.execution_time_sec:.1f}s", end="".ljust(18))
            else:
                print("ERROR".ljust(18), end="")

            # ACO
            if result.aco_metrics:
                print(f"{result.aco_metrics.num_solutions}|{result.aco_metrics.execution_time_sec:.1f}s", end="".ljust(18))
            else:
                print("ERROR".ljust(18), end="")

            print()

        print("\n" + "="*120)

    def export_results_json(self, filename: str = "evaluation_results.json"):
        """
        Exporta resultados em JSON para análise posterior
        """
        results_dict = []

        for result in self.results:
            result_data = {
                "test_case_name": result.test_case_name,
                "complexity": result.test_case_complexity,
                "origin": result.origin,
                "destination": result.destination,
                "start_time": result.start_time,
                "astar": asdict(result.astar_metrics) if result.astar_metrics else None,
                "dijkstra": asdict(result.dijkstra_metrics) if result.dijkstra_metrics else None,
                "aco": asdict(result.aco_metrics) if result.aco_metrics else None,
            }
            results_dict.append(result_data)

        with open(filename, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)

        print(f"\n✓ Resultados exportados para {filename}")

    def print_detailed_analysis(self):
        """
        Análise detalhada de cada resultado
        """
        print("\n" + "="*120)
        print("ANÁLISE DETALHADA POR CASO DE TESTE")
        print("="*120 + "\n")

        for result in self.results:
            print(f"\n{result.test_case_name}")
            print(f"Complexidade: {result.test_case_complexity.upper()}")
            print(f"Rota: {result.origin} → {result.destination}")
            print(f"Hora: {result.start_time}\n")

            # A*
            if result.astar_metrics:
                self._print_algorithm_details(result.astar_metrics)

            # Dijkstra
            if result.dijkstra_metrics:
                self._print_algorithm_details(result.dijkstra_metrics)

            # ACO
            if result.aco_metrics:
                self._print_algorithm_details(result.aco_metrics)

            print("-"*120 + "\n")
    
    def _print_algorithm_details(self, metrics: AlgorithmMetrics):
        """Imprime detalhes de um algoritmo"""
        print(f"{metrics.algorithm_name}:")
        print(f"  Tempo de execução: {metrics.execution_time_sec:.2f}s")
        print(f"  Soluções encontradas: {metrics.num_solutions}")
        print(f"  Melhor tempo: {metrics.best_time_sec/60:.1f} min")
        print(f"  Melhor CO2: {metrics.best_co2_g:.1f}g")
        print(f"  Máxima caminhada: {metrics.best_walk_km:.2f}km")
        print(f"  Tempo médio: {metrics.avg_time_sec/60:.1f} min")
        print(f"  CO2 médio: {metrics.avg_co2_g:.1f}g")
        print(f"  Caminhada média: {metrics.avg_walk_km:.2f}km\n")


if __name__ == "__main__":
    # Script de teste
    evaluator = ComparativeEvaluator()

    for complexity in ["trivial", "low", "medium", "high", "special", "extreme"]:
        print(f"Selecionando casos de teste {complexity}...")
        test_cases_to_run = TestCaseEvaluator.get_by_complexity(complexity)

        print(f"Executando {len(test_cases_to_run)} casos de teste {complexity}...\n")

        for test_case in test_cases_to_run:
            result = evaluator.run_single_test(test_case)

    # Gerar relatórios
    evaluator.print_comparison_table()
    evaluator.print_detailed_analysis()
    evaluator.export_results_json()
