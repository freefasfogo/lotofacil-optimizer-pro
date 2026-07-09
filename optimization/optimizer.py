"""
Orquestrador de otimização - Gerencia todos os algoritmos
"""
from typing import List, Optional, Dict, Any, Type
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime
import sys
import os

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithms.base import OptimizationAlgorithm, OptimizationResult
from algorithms.hill_climbing import HillClimbing
from algorithms.simulated_annealing import SimulatedAnnealing
from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.tabu_search import TabuSearch

from core.population import Population
from core.scorer import GameScorer
from database.database import Database
from database.models import OptimizationRun, GameHistory


class OptimizationOrchestrator:
    """
    Orquestrador de otimização
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scorer = GameScorer(config)
        self.db = Database()
        self.results = []
        self.algorithm_classes = {
            'hill_climbing': HillClimbing,
            'simulated_annealing': SimulatedAnnealing,
            'genetic': GeneticAlgorithm,
            'tabu_search': TabuSearch
        }
    
    def optimize(self, 
                 algorithm_name: str,
                 initial_population: Optional[Population] = None,
                 parallel: bool = False,
                 runs: int = 1) -> List[OptimizationResult]:
        
        if algorithm_name not in self.algorithm_classes:
            raise ValueError(f"Algoritmo {algorithm_name} não encontrado")
        
        algorithm_class = self.algorithm_classes[algorithm_name]
        
        if parallel and runs > 1:
            return self._run_parallel(algorithm_class, initial_population, runs)
        else:
            return [self._run_single(algorithm_class, initial_population)]
    
    def _run_single(self, 
                    algorithm_class: Type[OptimizationAlgorithm],
                    initial_population: Optional[Population]) -> OptimizationResult:
        """Executa uma única otimização"""
        algorithm = algorithm_class(self.scorer, self.config)
        result = algorithm.optimize(initial_population)
        
        # Salva no banco
        self._save_result(result)
        self.results.append(result)
        
        return result
    
    def _run_parallel(self,
                      algorithm_class: Type[OptimizationAlgorithm],
                      initial_population: Optional[Population],
                      runs: int) -> List[OptimizationResult]:
        """Executa otimizações em paralelo"""
        results = []
        
        with ThreadPoolExecutor() as executor:
            futures = []
            
            for i in range(runs):
                pop = initial_population
                if pop is None:
                    from core.game import GameGenerator
                    size = self.config.get('populacao', 20)
                    pop = Population(
                        GameGenerator.generate_many(size),
                        self.scorer
                    )
                
                future = executor.submit(
                    self._run_single,
                    algorithm_class,
                    pop.clone() if pop else None
                )
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Erro na execução paralela: {e}")
        
        return results
    
    def _save_result(self, result: OptimizationResult):
        """Salva o resultado no banco de dados"""
        try:
            # Salva execução
            run = OptimizationRun(
                algorithm=result.algorithm,
                generation=result.iterations,
                best_score=result.best_score,
                population_size=len(result.best_games),
                duration=result.duration,
                config=self.config
            )
            run_id = self.db.save_optimization_run(run)
            
            # Salva os jogos
            for game in result.best_games:
                try:
                    # Salva jogo
                    game_id = self.db.save_game(game)
                    
                    # Salva histórico
                    history = GameHistory(
                        game_id=game_id,
                        run_id=run_id,
                        numbers=game.numbers,
                        score=game.score,
                        metrics=game.to_dict()
                    )
                    self.db.save_game_history(history)
                except Exception as e:
                    print(f"Erro ao salvar jogo: {e}")
                    
        except Exception as e:
            print(f"Erro ao salvar resultado: {e}")
    
    def compare_algorithms(self, 
                           algorithms: List[str],
                           runs_per_algorithm: int = 3) -> Dict[str, Any]:
        """Compara diferentes algoritmos"""
        results = {}
        
        for algo in algorithms:
            algo_results = []
            for _ in range(runs_per_algorithm):
                result = self.optimize(algo, parallel=False)
                if result:
                    algo_results.append(result[0])
            
            if algo_results:
                scores = [r.best_score for r in algo_results]
                times = [r.duration for r in algo_results]
                
                results[algo] = {
                    'avg_score': sum(scores) / len(scores),
                    'max_score': max(scores),
                    'min_score': min(scores),
                    'std_score': self._std(scores),
                    'avg_time': sum(times) / len(times),
                    'iterations': [r.iterations for r in algo_results],
                    'results': algo_results
                }
        
        return results
    
    def _std(self, values: List[float]) -> float:
        """Calcula desvio padrão"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def get_best_result(self) -> Optional[OptimizationResult]:
        """Retorna o melhor resultado de todas as execuções"""
        if not self.results:
            return None
        
        return max(self.results, key=lambda r: r.best_score)
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Retorna resumo de todos os resultados"""
        if not self.results:
            return {}
        
        return {
            'total_runs': len(self.results),
            'best_score': max(r.best_score for r in self.results),
            'worst_score': min(r.best_score for r in self.results),
            'avg_score': sum(r.best_score for r in self.results) / len(self.results),
            'total_time': sum(r.duration for r in self.results),
            'algorithms_used': list(set(r.algorithm for r in self.results))
        }
    
    def export_results(self, filename: str = "optimization_results.json"):
        """Exporta resultados para JSON"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'config': self.config,
            'summary': self.get_results_summary(),
            'results': [r.to_dict() for r in self.results]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
