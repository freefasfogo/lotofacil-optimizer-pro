"""
Hill Climbing - Algoritmo de subida de encosta
Melhoria incremental com vizinhança local
"""
from typing import List, Optional, Dict, Any
import random
import copy

from .base import OptimizationAlgorithm, OptimizationResult
from core.game import Game, GameGenerator
from core.population import Population


class HillClimbing(OptimizationAlgorithm):
    """
    Algoritmo Hill Climbing para otimização de jogos
    
    Características:
    - Busca local
    - Melhoria incremental
    - Aceita apenas melhorias
    - Várias reinicializações para evitar ótimos locais
    """
    
    def __init__(self, scorer, config: Dict[str, Any]):
        super().__init__(scorer, config)
        self.max_iterations = config.get('max_iterations', 1000)
        self.restarts = config.get('restarts', 5)
        self.neighborhood_size = config.get('neighborhood_size', 10)
        self.current_solution = None
        self.current_score = 0.0
        
    def optimize(self, initial_population: Optional[Population] = None) -> OptimizationResult:
        """Executa a otimização Hill Climbing"""
        self._start_timer()
        self.current_iteration = 0
        self.best_solution = None
        self.best_score = 0.0
        self.history = []
        self.convergence = []
        
        # Gera população inicial se não fornecida
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
        
        # Executa várias reinicializações
        for restart in range(self.restarts):
            if restart > 0:
                # Nova população aleatória
                size = self.config.get('populacao', 20)
                current_population = Population(
                    GameGenerator.generate_many(size),
                    self.scorer
                )
                self._evaluate_population(current_population)
                current_score = current_population.get_score()
            
            # Hill Climbing
            for iteration in range(self.max_iterations):
                # Gera vizinhança
                neighbor = self._generate_neighbor(current_population)
                neighbor_score = self._evaluate_population(neighbor)
                
                # Aceita se melhor
                if neighbor_score > current_score:
                    current_population = neighbor
                    current_score = neighbor_score
                    
                    if current_score > best_score:
                        best_population = current_population.clone()
                        best_score = current_score
                        self.best_solution = best_population
                    
                    self._record_iteration(current_score)
                
                # Verifica se atingiu o máximo
                if current_score >= 0.99:
                    break
            
            self._record_iteration(current_score)
        
        # Prepara resultado
        result = OptimizationResult(
            best_games=best_population.games,
            best_score=best_score,
            iterations=self.current_iteration,
            duration=self._get_elapsed_time(),
            history=self.history,
            algorithm='Hill Climbing',
            parameters={
                'max_iterations': self.max_iterations,
                'restarts': self.restarts,
                'neighborhood_size': self.neighborhood_size
            },
            convergence_data=self.convergence
        )
        
        return result
    
    def _generate_neighbor(self, population: Population) -> Population:
        """Gera um vizinho da população atual"""
        new_games = []
        
        for game in population.games:
            # Muta algumas posições aleatórias
            new_game = copy.deepcopy(game)
            num_mutations = random.randint(1, 3)
            
            for _ in range(num_mutations):
                pos = random.randint(0, 14)
                available = [n for n in range(1, 26) if n not in new_game.numbers]
                if available:
                    new_num = random.choice(available)
                    new_game.numbers[pos] = new_num
                    new_game.numbers.sort()
                    new_game._calculate_properties()
            
            new_games.append(new_game)
        
        return Population(new_games, self.scorer)
    
    def step(self) -> bool:
        """Executa um passo do algoritmo"""
        if self.current_iteration >= self.max_iterations:
            return False
        
        if self.current_solution is None:
            # Inicializa com solução aleatória
            size = self.config.get('populacao', 20)
            self.current_solution = Population(
                GameGenerator.generate_many(size),
                self.scorer
            )
            self.current_score = self._evaluate_population(self.current_solution)
        
        # Gera vizinho
        neighbor = self._generate_neighbor(self.current_solution)
        neighbor_score = self._evaluate_population(neighbor)
        
        if neighbor_score > self.current_score:
            self.current_solution = neighbor
            self.current_score = neighbor_score
            self._record_iteration(self.current_score)
        
        self.current_iteration += 1
        return True
    
    def get_progress(self) -> float:
        """Retorna o progresso da otimização"""
        if self.max_iterations == 0:
            return 0.0
        return min(1.0, self.current_iteration / self.max_iterations)
