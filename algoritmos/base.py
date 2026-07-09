
"""
Interface base para todos os algoritmos de otimização
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from dataclasses import dataclass
import time
from datetime import datetime

from core.game import Game
from core.population import Population
from core.scorer import GameScorer


@dataclass
class OptimizationResult:
    """Resultado de uma execução de otimização"""
    best_games: List[Game]
    best_score: float
    iterations: int
    duration: float
    history: List[Dict[str, Any]]
    algorithm: str
    parameters: Dict[str, Any]
    convergence_data: List[float]
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'best_games': [g.to_dict() for g in self.best_games],
            'best_score': self.best_score,
            'iterations': self.iterations,
            'duration': self.duration,
            'history': self.history,
            'algorithm': self.algorithm,
            'parameters': self.parameters,
            'convergence_data': self.convergence_data
        }


class OptimizationAlgorithm(ABC):
    """Classe base para algoritmos de otimização"""
    
    def __init__(self, scorer: GameScorer, config: Dict[str, Any]):
        """
        Inicializa o algoritmo
        
        Args:
            scorer: Avaliador de score
            config: Configurações do algoritmo
        """
        self.scorer = scorer
        self.config = config
        self.current_iteration = 0
        self.best_solution = None
        self.best_score = 0.0
        self.history = []
        self.convergence = []
        self.start_time = None
        
    @abstractmethod
    def optimize(self, initial_population: Optional[Population] = None) -> OptimizationResult:
        """
        Executa a otimização
        
        Args:
            initial_population: População inicial (opcional)
            
        Returns:
            Resultado da otimização
        """
        pass
    
    @abstractmethod
    def step(self) -> bool:
        """
        Executa um passo da otimização
        
        Returns:
            True se ainda deve continuar, False se terminou
        """
        pass
    
    def _record_iteration(self, score: float, additional_data: Optional[Dict] = None):
        """Registra uma iteração no histórico"""
        self.current_iteration += 1
        self.convergence.append(score)
        
        record = {
            'iteration': self.current_iteration,
            'score': score,
            'timestamp': datetime.now().isoformat()
        }
        
        if additional_data:
            record.update(additional_data)
        
        self.history.append(record)
        
        if score > self.best_score:
            self.best_score = score
    
    def _start_timer(self):
        """Inicia o cronômetro"""
        self.start_time = time.time()
    
    def _get_elapsed_time(self) -> float:
        """Retorna o tempo decorrido"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def _evaluate_population(self, population: Population) -> float:
        """
        Avalia uma população completa
        
        Atualiza os scores individuais e retorna o score total
        """
        # Calcula score para cada jogo
        for game in population.games:
            game.score = self.scorer.score_game(game, population.games)
        
        # Calcula score total
        metrics = self.scorer.calculate(population.games)
        return metrics.total
    
    def get_progress(self) -> float:
        """
        Retorna o progresso atual (0 a 1)
        
        Deve ser sobrescrito por cada algoritmo
        """
        return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """
        Retorna o status atual da otimização
        
        Returns:
            Dicionário com status atual
        """
        return {
            'iterations': self.current_iteration,
            'best_score': self.best_score,
            'elapsed_time': self._get_elapsed_time(),
            'progress': self.get_progress()
        }
