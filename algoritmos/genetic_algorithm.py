"""
Genetic Algorithm - Algoritmo Genético
Evolução populacional com seleção, crossover e mutação
"""
from typing import List, Optional, Dict, Any, Tuple
import random
import copy
import math

from .base import OptimizationAlgorithm, OptimizationResult
from core.game import Game, GameGenerator
from core.population import Population


class GeneticAlgorithm(OptimizationAlgorithm):
    """
    Algoritmo Genético para otimização de jogos
    
    Características:
    - Evolução populacional
    - Seleção por torneio
    - Crossover uniforme
    - Mutação adaptativa
    - Elitismo
    """
    
    def __init__(self, scorer, config: Dict[str, Any]):
        super().__init__(scorer, config)
        self.population_size = config.get('populacao', 1000)
        self.generations = config.get('geracoes', 500)
        self.mutation_rate = config.get('taxa_mutacao', 0.1)
        self.crossover_rate = config.get('taxa_crossover', 0.8)
        self.tournament_size = config.get('tournament_size', 3)
        self.elite_size = config.get('elite_size', 2)
        
        self.population = None
        self.generation = 0
        
    def optimize(self, initial_population: Optional[Population] = None) -> OptimizationResult:
        """Executa a otimização Genética"""
        self._start_timer()
        self.current_iteration = 0
        self.best_solution = None
        self.best_score = 0.0
        self.history = []
        self.convergence = []
        self.generation = 0
        
        # Inicializa população
        if initial_population is None:
            self.population = Population(
                GameGenerator.generate_many(self.population_size),
                self.scorer
            )
        else:
            self.population = initial_population.clone()
        
        # Avalia população inicial
        self._evaluate_population(self.population)
        current_score = self.population.get_score()
        self._record_iteration(current_score)
        
        best_population = self.population.clone()
        best_score = current_score
        
        # Loop evolutivo
        for generation in range(self.generations):
            self.generation = generation + 1
            
            # Seleção
            parents = self._selection(self.population)
            
            # Crossover
            offspring = self._crossover(parents)
            
            # Mutação
            offspring = self._mutate(offspring)
            
            # Avalia offspring
            self._evaluate_population(offspring)
            
            # Elitismo - mantém os melhores
            new_population = self._elitism(self.population, offspring)
            
            # Atualiza população
            self.population = new_population
            
            # Atualiza melhor
            new_score = self.population.get_score()
            if new_score > best_score:
                best_population = self.population.clone()
                best_score = new_score
                self.best_solution = best_population
            
            # Registra
            if generation % 10 == 0:
                self._record_iteration(new_score)
            
            # Verifica convergência
            if new_score >= 0.99:
                break
        
        # Prepara resultado
        result = OptimizationResult(
            best_games=best_population.games,
            best_score=best_score,
            iterations=self.generation,
            duration=self._get_elapsed_time(),
            history=self.history,
            algorithm='Genetic Algorithm',
            parameters={
                'population_size': self.population_size,
                'generations': self.generations,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate,
                'tournament_size': self.tournament_size,
                'elite_size': self.elite_size
            },
            convergence_data=self.convergence
        )
        
        return result
    
    def _selection(self, population: Population) -> List[Game]:
        """Seleciona pais por torneio"""
        selected = []
        tournament_size = min(self.tournament_size, len(population))
        
        for _ in range(len(population)):
            # Seleciona candidatos aleatórios
            candidates = random.sample(population.games, tournament_size)
            # Escolhe o melhor
            winner = max(candidates, key=lambda g: g.score)
            selected.append(copy.deepcopy(winner))
        
        return selected
    
    def _crossover(self, parents: List[Game]) -> Population:
        """Realiza crossover entre pais"""
        offspring = []
        
        for i in range(0, len(parents) - 1, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1]
            
            # Crossover uniforme
            if random.random() < self.crossover_rate:
                child1_numbers = []
                child2_numbers = []
                
                for j in range(15):
                    if random.random() < 0.5:
                        child1_numbers.append(parent1.numbers[j])
                        child2_numbers.append(parent2.numbers[j])
                    else:
                        child1_numbers.append(parent2.numbers[j])
                        child2_numbers.append(parent1.numbers[j])
                
                # Remove duplicatas e completa
                child1 = self._repair_game(child1_numbers)
                child2 = self._repair_game(child2_numbers)
                
                offspring.append(child1)
                offspring.append(child2)
            else:
                offspring.append(copy.deepcopy(parent1))
                offspring.append(copy.deepcopy(parent2))
        
        return Population(offspring, self.scorer)
    
    def _repair_game(self, numbers: List[int]) -> Game:
        """Repara um jogo, removendo duplicatas e completando"""
        unique = list(set(numbers))
        
        # Remove números inválidos
        unique = [n for n in unique if 1 <= n <= 25]
        
        # Completa
        while len(unique) < 15:
            available = [n for n in range(1, 26) if n not in unique]
            if available:
                unique.append(random.choice(available))
            else:
                break
        
        return Game(unique[:15])
    
    def _mutate(self, population: Population) -> Population:
        """Aplica mutação na população"""
        new_games = []
        
        for game in population.games:
            if random.random() < self.mutation_rate:
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
                new_games.append(game)
        
        return Population(new_games, self.scorer)
    
    def _elitism(self, old_population: Population, new_population: Population) -> Population:
        """Mantém os melhores indivíduos da geração anterior"""
        # Ordena população antiga
        old_sorted = sorted(old_population.games, key=lambda g: g.score, reverse=True)
        
        # Ordena nova população
        new_sorted = sorted(new_population.games, key=lambda g: g.score, reverse=True)
        
        # Mantém elite
        elite = old_sorted[:self.elite_size]
        
        # Combina com nova população
        combined = elite + new_sorted[:len(new_sorted) - self.elite_size]
        
        return Population(combined, self.scorer)
    
    def step(self) -> bool:
        """Executa um passo do algoritmo"""
        if self.generation >= self.generations:
            return False
        
        if self.population is None:
            self.population = Population(
                GameGenerator.generate_many(self.population_size),
                self.scorer
            )
            self._evaluate_population(self.population)
        
        # Seleção
        parents = self._selection(self.population)
        
        # Crossover
        offspring = self._crossover(parents)
        
        # Mutação
        offspring = self._mutate(offspring)
        
        # Avalia
        self._evaluate_population(offspring)
        
        # Elitismo
        self.population = self._elitism(self.population, offspring)
        
        self.generation += 1
        score = self.population.get_score()
        self._record_iteration(score)
        
        return True
    
    def get_progress(self) -> float:
        """Retorna o progresso da otimização"""
        if self.generations == 0:
            return 0.0
        return min(1.0, self.generation / self.generations)
