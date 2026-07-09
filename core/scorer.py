"""
Módulo de avaliação de jogos da Lotofácil
Sistema modular de score com métricas independentes
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import math
import numpy as np
from .game import Game


@dataclass
class ScoreMetrics:
    """Container para todas as métricas de score"""
    frequency: float = 0.0
    overlap: float = 0.0
    parity: float = 0.0
    lines: float = 0.0
    columns: float = 0.0
    border: float = 0.0
    center: float = 0.0
    consecutive: float = 1.0  # Novo: penalidade por consecutivos
    total: float = 0.0
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'frequency': self.frequency,
            'overlap': self.overlap,
            'parity': self.parity,
            'lines': self.lines,
            'columns': self.columns,
            'border': self.border,
            'center': self.center,
            'consecutive': self.consecutive,
            'total': self.total
        }


class FrequencyScore:
    """Avalia o equilíbrio da frequência das dezenas"""
    
    def __init__(self, target_frequency: Optional[List[float]] = None):
        self.target_frequency = target_frequency or [1.0] * 25
    
    def calculate(self, games: List[Game]) -> float:
        if not games:
            return 0.0
        
        current_freq = [0] * 25
        for game in games:
            for num in game.numbers:
                current_freq[num - 1] += 1
        
        total = len(games) * 15
        current_freq = [f / total for f in current_freq]
        
        mse = sum((current_freq[i] - self.target_frequency[i]) ** 2 
                  for i in range(25)) / 25
        
        return max(0.0, 1.0 - mse * 10)


class OverlapScore:
    """Avalia a sobreposição entre jogos"""
    
    def __init__(self, max_overlap: int = 8):
        self.max_overlap = max_overlap
    
    def calculate(self, games: List[Game]) -> float:
        if len(games) < 2:
            return 1.0
        
        total_overlap = 0
        pairs = 0
        
        for i in range(len(games)):
            for j in range(i + 1, len(games)):
                overlap = games[i].overlap(games[j])
                total_overlap += overlap
                pairs += 1
        
        if pairs == 0:
            return 1.0
        
        avg_overlap = total_overlap / pairs
        
        if avg_overlap <= self.max_overlap:
            return 1.0
        else:
            return math.exp(-(avg_overlap - self.max_overlap) / 2.0)


class ParityScore:
    """Avalia o equilíbrio entre pares e ímpares"""
    
    def __init__(self, ideal_parity: float = 0.5):
        self.ideal_parity = ideal_parity
    
    def calculate(self, games: List[Game]) -> float:
        if not games:
            return 0.0
        
        avg_pares = sum(game.pares for game in games) / (len(games) * 15)
        distance = abs(avg_pares - self.ideal_parity)
        return max(0.0, 1.0 - distance * 2.0)


class LineScore:
    """Avalia a distribuição por linhas (1-5, 6-10, 11-15, 16-20, 21-25)"""
    
    def __init__(self, ideal_distribution: Optional[List[float]] = None):
        self.ideal_distribution = ideal_distribution or [0.2] * 5
    
    def calculate(self, games: List[Game]) -> float:
        if not games:
            return 0.0
        
        current_dist = [0] * 5
        for game in games:
            for i, count in enumerate(game.linhas):
                current_dist[i] += count
        
        total = sum(current_dist)
        if total == 0:
            return 0.0
        
        current_dist = [c / total for c in current_dist]
        mse = sum((current_dist[i] - self.ideal_distribution[i]) ** 2 
                  for i in range(5)) / 5
        
        return max(0.0, 1.0 - mse * 10)


class ColumnScore:
    """Avalia a distribuição por colunas"""
    
    def __init__(self, ideal_distribution: Optional[List[float]] = None):
        self.ideal_distribution = ideal_distribution or [0.2] * 5
    
    def calculate(self, games: List[Game]) -> float:
        if not games:
            return 0.0
        
        current_dist = [0] * 5
        for game in games:
            for i, count in enumerate(game.colunas):
                current_dist[i] += count
        
        total = sum(current_dist)
        if total == 0:
            return 0.0
        
        current_dist = [c / total for c in current_dist]
        mse = sum((current_dist[i] - self.ideal_distribution[i]) ** 2 
                  for i in range(5)) / 5
        
        return max(0.0, 1.0 - mse * 10)


class BorderScore:
    """Avalia a quantidade de números na moldura"""
    
    def __init__(self, ideal_border: float = 0.4):
        self.ideal_border = ideal_border
    
    def calculate(self, games: List[Game]) -> float:
        if not games:
            return 0.0
        
        avg_border = sum(game.moldura for game in games) / (len(games) * 15)
        distance = abs(avg_border - self.ideal_border)
        return max(0.0, 1.0 - distance * 3.0)


class CenterScore:
    """Avalia a quantidade de números no centro (7-9, 12-14, 17-19)"""
    
    def __init__(self, ideal_center: float = 0.2):
        self.ideal_center = ideal_center
    
    def calculate(self, games: List[Game]) -> float:
        if not games:
            return 0.0
        
        avg_center = sum(game.centro for game in games) / (len(games) * 15)
        distance = abs(avg_center - self.ideal_center)
        return max(0.0, 1.0 - distance * 5.0)


class ConsecutivePenaltyScore:
    """
    Penaliza jogos com muitos números consecutivos
    
    Quanto mais grupos de consecutivos, maior a penalidade
    """
    
    def __init__(self, max_allowed: int = 2):
        """
        Args:
            max_allowed: Número máximo permitido de consecutivos
        """
        self.max_allowed = max_allowed
    
    def calculate(self, games: List[Game]) -> float:
        """
        Calcula o score de penalidade por consecutivos
        
        Retorna 1.0 se não houver penalidade, 0.0 se penalidade máxima
        """
        if not games:
            return 1.0
        
        total_penalty = 0
        
        for game in games:
            # Encontra grupos de consecutivos
            consec_groups = self._find_consecutive_groups(game.numbers)
            
            # Penaliza cada grupo que excede o máximo permitido
            for group in consec_groups:
                if len(group) > self.max_allowed:
                    # Penalidade proporcional ao excesso
                    excess = len(group) - self.max_allowed
                    total_penalty += excess * 0.15  # 15% por número extra consecutivo
        
        # Penalidade máxima de 50%
        max_penalty = len(games) * 3 * 0.15  # Assumindo no máximo 3 grupos por jogo
        penalty_ratio = min(total_penalty / max_penalty if max_penalty > 0 else 0, 0.5)
        
        return max(0.0, 1.0 - penalty_ratio)
    
    def _find_consecutive_groups(self, numbers: List[int]) -> List[List[int]]:
        """
        Encontra grupos de números consecutivos
        
        Exemplo: [1, 2, 3, 5, 6, 8] -> [[1, 2, 3], [5, 6]]
        """
        if not numbers:
            return []
        
        groups = []
        current_group = [numbers[0]]
        
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i - 1] + 1:
                current_group.append(numbers[i])
            else:
                if len(current_group) > 1:
                    groups.append(current_group)
                current_group = [numbers[i]]
        
        if len(current_group) > 1:
            groups.append(current_group)
        
        return groups


class GameScorer:
    """
    Sistema principal de score - combina todas as métricas
    
    Pesos configuráveis:
    - frequencia: Equilíbrio das dezenas
    - sobreposicao: Repetição entre jogos
    - pares: Proporção pares/ímpares
    - linhas: Distribuição por linhas
    - colunas: Distribuição por colunas
    - moldura: Quantidade na moldura
    - consecutivo: Penalidade por consecutivos (NOVO)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o scorer com as configurações
        
        Args:
            config: Dicionário com configurações (pesos e parâmetros)
        """
        self.config = config
        self.weights = config.get('pesos', {})
        
        # Inicializa métricas
        self.frequency_scorer = FrequencyScore()
        self.overlap_scorer = OverlapScore(
            max_overlap=config.get('max_overlap', 8)
        )
        self.parity_scorer = ParityScore()
        self.line_scorer = LineScore()
        self.column_scorer = ColumnScore()
        self.border_scorer = BorderScore()
        self.center_scorer = CenterScore()
        
        # Nova métrica: penalidade por consecutivos
        max_consec = config.get('validacoes', {}).get('max_consecutivos', 2)
        self.consecutive_scorer = ConsecutivePenaltyScore(max_allowed=max_consec)
        
        # Normaliza os pesos
        self._normalize_weights()
    
    def _normalize_weights(self):
        """Normaliza os pesos para somarem 1"""
        total = sum(self.weights.values())
        if total > 0:
            for key in self.weights:
                self.weights[key] /= total
    
    def calculate(self, games: List[Game]) -> ScoreMetrics:
        """
        Calcula todas as métricas para uma população de jogos
        
        Args:
            games: Lista de jogos
            
        Returns:
            ScoreMetrics com todas as métricas calculadas
        """
        metrics = ScoreMetrics()
        
        # Calcula cada métrica
        metrics.frequency = self.frequency_scorer.calculate(games)
        metrics.overlap = self.overlap_scorer.calculate(games)
        metrics.parity = self.parity_scorer.calculate(games)
        metrics.lines = self.line_scorer.calculate(games)
        metrics.columns = self.column_scorer.calculate(games)
        metrics.border = self.border_scorer.calculate(games)
        metrics.center = self.center_scorer.calculate(games)
        metrics.consecutive = self.consecutive_scorer.calculate(games)
        
        # Calcula score total ponderado
        metrics.total = (
            metrics.frequency * self.weights.get('frequencia', 0.25) +
            metrics.overlap * self.weights.get('sobreposicao', 0.25) +
            metrics.parity * self.weights.get('pares', 0.10) +
            metrics.lines * self.weights.get('linhas', 0.15) +
            metrics.columns * self.weights.get('colunas', 0.15) +
            metrics.border * self.weights.get('moldura', 0.05) +
            metrics.consecutive * self.weights.get('consecutivo', 0.05)
        )
        
        return metrics
    
    def score_game(self, game: Game, population: List[Game]) -> float:
        """
        Calcula o score de um jogo individual em relação à população
        
        Útil para algoritmos evolutivos
        """
        if not population:
            return 0.0
        
        temp_population = population + [game]
        metrics = self.calculate(temp_population)
        return metrics.total
    
    def score_individual(self, game: Game) -> float:
        """
        Calcula o score de um jogo individual (sem contexto populacional)
        """
        metrics = self.calculate([game])
        return metrics.total
    
    def calculate_percentage(self, games: List[Game]) -> float:
        """
        Calcula o score em porcentagem (0-100%)
        """
        metrics = self.calculate(games)
        return metrics.total * 100
    
    def score_individual_percentage(self, game: Game) -> float:
        """
        Calcula o score individual em porcentagem
        """
        return self.score_individual(game) * 100
    
    def get_metric_details(self, games: List[Game]) -> Dict[str, float]:
        """
        Retorna detalhes de cada métrica para análise
        """
        metrics = self.calculate(games)
        return {
            'Frequência': metrics.frequency * 100,
            'Sobreposição': metrics.overlap * 100,
            'Pares/Ímpares': metrics.parity * 100,
            'Linhas': metrics.lines * 100,
            'Colunas': metrics.columns * 100,
            'Moldura': metrics.border * 100,
            'Centro': metrics.center * 100,
            'Consecutivos': metrics.consecutive * 100,
            'Total': metrics.total * 100
        }
