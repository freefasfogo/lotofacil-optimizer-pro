"""
Módulo de gerenciamento de população de jogos
"""
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import copy
import random
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from .game import Game, GameGenerator
from .scorer import GameScorer, ScoreMetrics


@dataclass
class PopulationStats:
    """Estatísticas de uma população"""
    size: int
    avg_score: float
    max_score: float
    min_score: float
    std_score: float
    diversity_score: float
    frequency_distribution: List[int]
    
    def to_dict(self) -> dict:
        return {
            'size': self.size,
            'avg_score': self.avg_score,
            'max_score': self.max_score,
            'min_score': self.min_score,
            'std_score': self.std_score,
            'diversity_score': self.diversity_score,
            'frequency_distribution': self.frequency_distribution
        }


class Population:
    """
    Classe para gerenciar uma população de jogos da Lotofácil
    
    Responsável por:
    - Manter conjunto de jogos
    - Calcular frequência das dezenas
    - Calcular score geral
    - Comparação entre jogos
    - Cache de resultados
    """
    
    def __init__(self, games: Optional[List[Game]] = None, 
                 scorer: Optional[GameScorer] = None):
        """
        Inicializa a população
        
        Args:
            games: Lista inicial de jogos
            scorer: Avaliador de score (cria um se não fornecido)
        """
        self.games = games or []
        self.scorer = scorer
        self._cache = {}
        self._frequency_cache = None
        self._stats_cache = None
        self._metrics_cache = None
        
        # Inicializa cache se houver jogos
        if self.games:
            self._update_cache()
    
    def add_game(self, game: Game) -> bool:
        """
        Adiciona um jogo à população
        
        Returns:
            True se adicionado, False se já existe
        """
        if game.mask in self._get_masks():
            return False
        
        self.games.append(game)
        self._invalidate_cache()
        return True
    
    def add_games(self, games: List[Game]) -> int:
        """
        Adiciona múltiplos jogos
        
        Returns:
            Número de jogos adicionados
        """
        added = 0
        existing_masks = self._get_masks()
        
        for game in games:
            if game.mask not in existing_masks:
                self.games.append(game)
                existing_masks.add(game.mask)
                added += 1
        
        if added > 0:
            self._invalidate_cache()
        
        return added
    
    def remove_game(self, game: Game) -> bool:
        """Remove um jogo da população"""
        for i, g in enumerate(self.games):
            if g.mask == game.mask:
                self.games.pop(i)
                self._invalidate_cache()
                return True
        return False
    
    def remove_game_by_index(self, index: int) -> Optional[Game]:
        """Remove um jogo pelo índice"""
        if 0 <= index < len(self.games):
            game = self.games.pop(index)
            self._invalidate_cache()
            return game
        return None
    
    def get_game(self, index: int) -> Optional[Game]:
        """Retorna um jogo pelo índice"""
        if 0 <= index < len(self.games):
            return self.games[index]
        return None
    
    def _get_masks(self) -> Set[int]:
        """Retorna o conjunto de masks dos jogos"""
        return {game.mask for game in self.games}
    
    def _invalidate_cache(self):
        """Invalida o cache"""
        self._cache = {}
        self._frequency_cache = None
        self._stats_cache = None
        self._metrics_cache = None
    
    def _update_cache(self):
        """Atualiza o cache"""
        if not self.games:
            return
        
        # Calcula frequências
        self._frequency_cache = [0] * 25
        for game in self.games:
            for num in game.numbers:
                self._frequency_cache[num - 1] += 1
        
        # Calcula métricas se tiver scorer
        if self.scorer:
            self._metrics_cache = self.scorer.calculate(self.games)
    
    def get_frequency(self) -> List[int]:
        """Retorna a frequência das dezenas"""
        if self._frequency_cache is None:
            self._update_cache()
        return self._frequency_cache
    
    def get_score(self) -> float:
        """Retorna o score total da população"""
        if self._metrics_cache is None:
            self._update_cache()
        
        if self._metrics_cache:
            return self._metrics_cache.total
        return 0.0
    
    def get_metrics(self) -> Optional[ScoreMetrics]:
        """Retorna todas as métricas da população"""
        if self._metrics_cache is None:
            self._update_cache()
        return self._metrics_cache
    
    def get_statistics(self) -> PopulationStats:
        """Retorna estatísticas detalhadas da população"""
        if self._stats_cache is not None:
            return self._stats_cache
        
        if not self.games:
            return PopulationStats(
                size=0,
                avg_score=0.0,
                max_score=0.0,
                min_score=0.0,
                std_score=0.0,
                diversity_score=0.0,
                frequency_distribution=[0] * 25
            )
        
        # Calcula scores individuais
        scores = [game.score for game in self.games]
        
        # Calcula diversidade
        diversity = self._calculate_diversity()
        
        stats = PopulationStats(
            size=len(self.games),
            avg_score=np.mean(scores),
            max_score=np.max(scores),
            min_score=np.min(scores),
            std_score=np.std(scores),
            diversity_score=diversity,
            frequency_distribution=self.get_frequency()
        )
        
        self._stats_cache = stats
        return stats
    
    def _calculate_diversity(self) -> float:
        """
        Calcula a diversidade da população
        
        Quanto mais diversos os jogos, maior o score
        """
        if len(self.games) < 2:
            return 1.0
        
        # Calcula sobreposição média
        total_overlap = 0
        pairs = 0
        
        for i in range(len(self.games)):
            for j in range(i + 1, len(self.games)):
                overlap = self.games[i].overlap(self.games[j])
                total_overlap += overlap
                pairs += 1
        
        if pairs == 0:
            return 1.0
        
        avg_overlap = total_overlap / pairs
        
        # Diversidade: 1 - (avg_overlap / 15)
        # Quanto menor a sobreposição, maior a diversidade
        return max(0.0, 1.0 - (avg_overlap / 15))
    
    def get_best_games(self, n: int = 10) -> List[Game]:
        """Retorna os n melhores jogos"""
        sorted_games = sorted(self.games, key=lambda g: g.score, reverse=True)
        return sorted_games[:n]
    
    def get_worst_games(self, n: int = 10) -> List[Game]:
        """Retorna os n piores jogos"""
        sorted_games = sorted(self.games, key=lambda g: g.score)
        return sorted_games[:n]
    
    def replace_worst(self, new_games: List[Game], scorer: Optional[GameScorer] = None) -> int:
        """
        Substitui os piores jogos por novos
        
        Args:
            new_games: Lista de novos jogos
            scorer: Avaliador para calcular scores dos novos jogos
            
        Returns:
            Número de jogos substituídos
        """
        if not new_games:
            return 0
        
        # Ordena os jogos atuais por score (piores primeiro)
        self.games.sort(key=lambda g: g.score)
        
        # Calcula scores dos novos jogos
        if scorer:
            scorer = scorer or self.scorer
            temp_pop = self.games.copy()
            for game in new_games:
                game.score = scorer.score_game(game, temp_pop)
                temp_pop.append(game)
        
        # Substitui os piores
        replace_count = min(len(new_games), len(self.games))
        for i in range(replace_count):
            self.games[i] = new_games[i]
        
        self._invalidate_cache()
        return replace_count
    
    def mutate(self, mutation_rate: float = 0.1, preserve_valid: bool = True) -> 'Population':
        """
        Aplica mutação em toda a população
        
        Args:
            mutation_rate: Taxa de mutação
            preserve_valid: Se deve preservar jogos válidos
            
        Returns:
            Nova população mutada
        """
        new_games = []
        
        for game in self.games:
            if random.random() < mutation_rate:
                # Cria uma cópia e muta
                new_game = copy.deepcopy(game)
                self._mutate_game(new_game)
                
                # Verifica validade
                if not preserve_valid or self._is_valid(new_game):
                    new_games.append(new_game)
                else:
                    new_games.append(game)
            else:
                new_games.append(game)
        
        return Population(new_games, self.scorer)
    
    def _mutate_game(self, game: Game):
        """Muta um jogo individual"""
        # Escolhe uma posição aleatória para trocar
        pos = random.randint(0, 14)
        
        # Gera um novo número não presente no jogo
        available = [n for n in range(1, 26) if n not in game.numbers]
        if available:
            new_num = random.choice(available)
            old_num = game.numbers[pos]
            game.numbers[pos] = new_num
            game.numbers.sort()
            game._calculate_properties()
    
    def _is_valid(self, game: Game) -> bool:
        """Verifica se um jogo é válido"""
        # Validação básica
        if len(game.numbers) != 15:
            return False
        if len(set(game.numbers)) != 15:
            return False
        if not all(1 <= n <= 25 for n in game.numbers):
            return False
        return True
    
    def crossover(self, other: 'Population') -> 'Population':
        """
        Realiza crossover entre duas populações
        
        Args:
            other: Outra população
            
        Returns:
            Nova população resultante do crossover
        """
        if len(self.games) != len(other.games):
            raise ValueError("Populações devem ter o mesmo tamanho")
        
        new_games = []
        
        for i in range(len(self.games)):
            # Crossover uniforme entre os dois jogos
            parent1 = self.games[i]
            parent2 = other.games[i]
            
            # 50% de chance de herdar cada gene
            numbers = []
            for j in range(15):
                if random.random() < 0.5:
                    numbers.append(parent1.numbers[j])
                else:
                    numbers.append(parent2.numbers[j])
            
            # Remove duplicatas e completa
            numbers = list(set(numbers))
            while len(numbers) < 15:
                available = [n for n in range(1, 26) if n not in numbers]
                numbers.append(random.choice(available))
            
            new_game = Game(numbers[:15])
            new_games.append(new_game)
        
        return Population(new_games, self.scorer)
    
    def clone(self) -> 'Population':
        """Cria uma cópia da população"""
        return Population([copy.deepcopy(g) for g in self.games], self.scorer)
    
    def __len__(self) -> int:
        return len(self.games)
    
    def __iter__(self):
        return iter(self.games)
    
    def __getitem__(self, index):
        return self.games[index]
    
    def __contains__(self, game: Game) -> bool:
        return game.mask in self._get_masks()


class PopulationFactory:
    """Fábrica para criar populações"""
    
    @staticmethod
    def create_random(size: int, scorer: Optional[GameScorer] = None) -> Population:
        """
        Cria uma população aleatória
        
        Args:
            size: Tamanho da população
            scorer: Avaliador de score
            
        Returns:
            População gerada
        """
        games = GameGenerator.generate_many(size)
        pop = Population(games, scorer)
        
        # Calcula scores se tiver scorer
        if scorer:
            for game in pop.games:
                game.score = scorer.score_individual(game)
        
        return pop
    
    @staticmethod
    def create_from_games(games: List[Game], scorer: Optional[GameScorer] = None) -> Population:
        """Cria uma população a partir de uma lista de jogos"""
        pop = Population(games, scorer)
        if scorer:
            for game in pop.games:
                game.score = scorer.score_individual(game)
        return pop
    
    @staticmethod
    def create_balanced(size: int, scorer: Optional[GameScorer] = None) -> Population:
        """
        Cria uma população balanceada (distribuição uniforme)
        
        Tenta garantir uma distribuição equilibrada das dezenas
        """
        games = []
        seen = set()
        attempts = 0
        max_attempts = size * 20
        
        while len(games) < size and attempts < max_attempts:
            attempts += 1
            game = GameGenerator.generate_random()
            
            if game.mask not in seen:
                # Verifica balanceamento
                freq = [0] * 25
                for g in games:
                    for num in g.numbers:
                        freq[num - 1] += 1
                
                # Calcula desvio padrão da frequência se tiver jogos
                if games:
                    mean = sum(freq) / 25
                    std = np.std(freq)
                    # Aceita se não estiver muito desbalanceado
                    if std <= 3.0:
                        games.append(game)
                        seen.add(game.mask)
                else:
                    games.append(game)
                    seen.add(game.mask)
        
        pop = Population(games, scorer)
        if scorer:
            for game in pop.games:
                game.score = scorer.score_individual(game)
        
        return pop
