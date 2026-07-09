"""
Tabu Search - Busca Tabu
Busca com memória de movimentos
"""
from typing import List, Optional, Dict, Any, Set, Tuple
import random
import copy
from collections import deque

from .base import OptimizationAlgorithm, OptimizationResult
from core.game import Game, GameGenerator
from core.population import Population


class TabuSearch(OptimizationAlgorithm):
    """
    Algoritmo de Busca Tabu para otimização de jogos
    
    Características:
    - Memória de movimentos recentes
    - Evita ciclos
    - Critérios de aspiração
    - Busca diversificada
    """
    
    def __init__(self, scorer, config: Dict[str, Any]):
        super().__init__(scorer, config)
        self.max_iterations = config.get('max_iterations', 1000)
        self.tabu_tenure = config.get('tabu_tenure', 10)
        self.neighborhood_size = config.get('neighborhood_size', 20)
        self.diversification_frequency = config.get('diversification_frequency', 50)
        
        self.tabu_list = deque(maxlen=self.tabu_tenure)
        self.current_solution = None
        self.current_score = 0.0
        self.best_solution = None
        self.best_score = 0.0
        self.stagnation_counter = 0
        
    def optimize(self, initial_population: Optional[Population] = None) -> OptimizationResult:
        """Executa a otimização Tabu Search"""
        self._start_timer()
        self.current_iteration = 0
        self.best_solution = None
        self.best_score = 0.0
        self.history = []
        self.convergence = []
        self.tabu_list.clear()
        self.stagnation_counter = 0
        
        # Gera solução inicial
        if initial_population is None:
            size = self.config.get('populacao', 20)
            initial_population = Population(
                GameGenerator.generate_many(size),
                self.scorer
            )
        
        self.current_solution = initial_population.clone()
        self._evaluate_population(self.current_solution)
        self.current_score = self.current_solution.get_score()
        
        self.best_solution = self.current_solution.clone()
        self.best_score = self.current_score
        
        self._record_iteration(self.current_score)
        
        # Loop principal
        for iteration in range(self.max_iterations):
            # Gera vizinhança
            neighborhood = self._generate_neighborhood(self.current_solution)
            
            # Avalia vizinhos
            best_neighbor = None
            best_neighbor_score = -float('inf')
            best_neighbor_index = -1
            
            for i, neighbor in enumerate(neighborhood):
                score = self._evaluate_population(neighbor)
                
                # Verifica critérios tabu
                is_tabu = self._is_tabu(neighbor)
                
                # Critério de aspiração
                if is_tabu and score > self.best_score:
                    is_tabu = False
                
                if not is_tabu and score > best_neighbor_score:
                    best_neighbor = neighbor
                    best_neighbor_score = score
                    best_neighbor_index = i
            
            # Se não encontrou vizinho válido, diversifica
            if best_neighbor is None:
                self._diversify()
                continue
            
            # Atualiza solução atual
            self.current_solution = best_neighbor
            self.current_score = best_neighbor_score
            
            # Adiciona movimento à lista tabu
            if best_neighbor_index >= 0:
                self._add_to_tabu(best_neighbor_index)
            
            # Atualiza melhor solução
            if self.current_score > self.best_score:
                self.best_solution = self.current_solution.clone()
                self.best_score = self.current_score
                self.stagnation_counter = 0
            else:
                self.stagnation_counter += 1
            
            # Verifica estagnação
            if self.stagnation_counter >= self.diversification_frequency:
                self._diversify()
                self.stagnation_counter = 0
            
            # Registra
            if iteration % 10 == 0:
                self._record_iteration(self.current_score)
            
            # Verifica se atingiu o máximo
            if self.current_score >= 0.99:
                break
        
        # Prepara resultado
        result = OptimizationResult(
            best_games=self.best_solution.games,
            best_score=self.best_score,
            iterations=self.current_iteration,
            duration=self._get_elapsed_time(),
            history=self.history,
            algorithm='Tabu Search',
            parameters={
                'max_iterations': self.max_iterations,
                'tabu_tenure': self.tabu_tenure,
                'neighborhood_size': self.neighborhood_size,
                'diversification_frequency': self.diversification_frequency
            },
            convergence_data=self.convergence
        )
        
        return result
    
    def _generate_neighborhood(self, population: Population) -> List[Population]:
        """Gera vizinhança da solução atual"""
        neighborhood = []
        
        for _ in range(self.neighborhood_size):
            new_games = []
            
            for game in population.games:
                # Muta aleatoriamente
                new_game = copy.deepcopy(game)
                pos = random.randint(0, 14)
                available = [n for n in range(1, 26) if n not in new_game.numbers]
                if available:
                    new_num = random.choice(available)
                    new_game.numbers[pos] = new_num
                    new_game.numbers.sort()
                    new_game._calculate_properties()
                new_games.append(new_game)
            
            neighborhood.append(Population(new_games, self.scorer))
        
        return neighborhood
    
    def _is_tabu(self, population: Population) -> bool:
        """Verifica se a solução está na lista tabu"""
        for tabu in self.tabu_list:
            # Compara as máscaras dos jogos
            if len(tabu) == len(population.games):
                if all(t.mask == p.mask for t, p in zip(tabu, population.games)):
                    return True
        return False
    
    def _add_to_tabu(self, index: int):
        """Adiciona um movimento à lista tabu"""
        # Armazena o estado atual como tabu
        self.tabu_list.append(self.current_solution.games.copy())
    
    def _diversify(self):
        """Diversifica a busca quando estagnada"""
        # Substitui alguns jogos por aleatórios
        new_games = []
        replace_count = max(1, len(self.current_solution.games) // 4)
        
        for i, game in enumerate(self.current_solution.games):
            if i < replace_count:
                new_games.append(GameGenerator.generate_random())
            else:
                new_games.append(copy.deepcopy(game))
        
        self.current_solution = Population(new_games, self.scorer)
        self._evaluate_population(self.current_solution)
        self.current_score = self.current_solution.get_score()
        
        # Limpa lista tabu
        self.tabu_list.clear()
    
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
            self._evaluate_population(self.current_solution)
            self.current_score = self.current_solution.get_score()
        
        # Gera vizinhança
        neighborhood = self._generate_neighborhood(self.current_solution)
        
        # Encontra melhor vizinho
        best_neighbor = None
        best_neighbor_score = -float('inf')
        
        for neighbor in neighborhood:
            score = self._evaluate_population(neighbor)
            if not self._is_tabu(neighbor) and score > best_neighbor_score:
                best_neighbor = neighbor
                best_neighbor_score = score
        
        if best_neighbor is None:
            self._diversify()
            self.current_iteration += 1
            return True
        
        self.current_solution = best_neighbor
        self.current_score = best_neighbor_score
        
        if self.current_score > self.best_score:
            self.best_solution = self.current_solution.clone()
            self.best_score = self.current_score
        
        self.current_iteration += 1
        self._record_iteration(self.current_score)
        
        return True
    
    def get_progress(self) -> float:
        """Retorna o progresso da otimização"""
        if self.max_iterations == 0:
            return 0.0
        return min(1.0, self.current_iteration / self.max_iterations)
