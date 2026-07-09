"""
Simulated Annealing - Algoritmo de Recozimento Simulado
Evita ficar preso em ótimos locais
"""
from typing import List, Optional, Dict, Any
import random
import math
import copy

from .base import OptimizationAlgorithm, OptimizationResult
from core.game import Game, GameGenerator
from core.population import Population


class SimulatedAnnealing(OptimizationAlgorithm):
    """
    Algoritmo de Recozimento Simulado para otimização de jogos
    
    Características:
    - Busca global
    - Aceita soluções piores com probabilidade controlada
    - Temperatura decrescente
    """
    
    def __init__(self, scorer, config: Dict[str, Any]):
        super().__init__(scorer, config)
        self.max_iterations = config.get('max_iterations', 1000)
        self.initial_temp = config.get('temperatura_inicial', 1000)
        self.final_temp = config.get('temperatura_final', 1)
        self.cooling_rate = config.get('cooling_rate', 0.95)
        self.current_solution = None
        self.current_score = 0.0
        self.temperature = self.initial_temp
        
    def optimize(self, initial_population: Optional[Population] = None) -> OptimizationResult:
        """Executa a otimização Simulated Annealing"""
        self._start_timer()
        self.current_iteration = 0
        self.best_solution = None
        self.best_score = 0.0
        self.history = []
        self.convergence = []
        self.temperature = self.initial_temp
        
        # Gera população inicial
        if initial_population is None:
            size = self.config.get('populacao', 20)
            initial_population = Population(
                GameGenerator.generate_many(size),
                self.scorer
            )
        
        # Avalia população inicial
        current_population = initial_population.clone()
        self._evaluate_population(current_population)
        current_score = current_population.get_score()
        
        best_population = current_population.clone()
        best_score = current_score
        
        self._record_iteration(current_score)
        
        # Loop principal
        for iteration in range(self.max_iterations):
            # Gera vizinho
            neighbor = self._generate_neighbor(current_population)
            neighbor_score = self._evaluate_population(neighbor)
            
            # Calcula delta
            delta = neighbor_score - current_score
            
            # Decide se aceita
            if delta > 0 or random.random() < math.exp(delta / self.temperature):
                current_population = neighbor
                current_score = neighbor_score
                
                if current_score > best_score:
                    best_population = current_population.clone()
                    best_score = current_score
                    self.best_solution = best_population
            
            # Resfria
            self.temperature *= self.cooling_rate
            
            # Registra iteração
            if iteration % 10 == 0:
                self._record_iteration(current_score)
            
            # Verifica condição de parada
            if self.temperature <= self.final_temp:
                break
            
            # Verifica se atingiu o máximo
            if current_score >= 0.99:
                break
        
        # Prepara resultado
        result = OptimizationResult(
            best_games=best_population.games,
            best_score=best_score,
            iterations=self.current_iteration,
            duration=self._get_elapsed_time(),
            history=self.history,
            algorithm='Simulated Annealing',
            parameters={
                'initial_temp': self.initial_temp,
                'final_temp': self.final_temp,
                'cooling_rate': self.cooling_rate,
                'max_iterations': self.max_iterations
            },
            convergence_data=self.convergence
        )
        
        return result
    
    def _generate_neighbor(self, population: Population) -> Population:
        """Gera um vizinho da população"""
        new_games = []
        
        for game in population.games:
            # Muta com probabilidade baseada na temperatura
            if random.random() < self.temperature / self.initial_temp:
                new_game = copy.deepcopy(game)
                pos = random.randint(0, 14)
                available = [n for n in range(1, 26) if n not in new_game.numbers]
                if available:
                    new_num = random.choice(available)
                    new_game.numbers[pos] = new_num
                    new_game.numbers.sort()
                    new_game._calculate_properties()
                new_games.append(new_game)
            else:
                new_games.append(copy.deepcopy(game))
        
        return Population(new_games, self.scorer)
    
    def step(self) -> bool:
        """Executa um passo do algoritmo"""
        if self.current_iteration >= self.max_iterations:
            return False
        
        if self.current_solution is None:
            size = self.config.get('populacao', 20)
            self.current_solution = Population(
                GameGenerator.generate_many(size),
                self.scorer
            )
            self.current_score = self._evaluate_population(self.current_solution)
            self.temperature = self.initial_temp
        
        # Gera vizinho
        neighbor = self._generate_neighbor(self.current_solution)
        neighbor_score = self._evaluate_population(neighbor)
        
        # Calcula delta
        delta = neighbor_score - self.current_score
        
        # Decide se aceita
        if delta > 0 or random.random() < math.exp(delta / self.temperature):
            self.current_solution = neighbor
            self.current_score = neighbor_score
            
            if self.current_score > self.best_score:
                self.best_solution = self.current_solution.clone()
                self.best_score = self.current_score
        
        # Resfria
        self.temperature *= self.cooling_rate
        self.current_iteration += 1
        
        if self.current_iteration % 10 == 0:
            self._record_iteration(self.current_score)
        
        return self.temperature > self.final_temp
    
    def get_progress(self) -> float:
        """Retorna o progresso da otimização"""
        if self.initial_temp == self.final_temp:
            return 1.0
        progress = 1 - (self.temperature - self.final_temp) / (self.initial_temp - self.final_temp)
        return min(1.0, max(0.0, progress))
