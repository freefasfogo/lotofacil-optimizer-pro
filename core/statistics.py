"""
Módulo de estatísticas e análise de dados da Lotofácil
"""
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from collections import Counter
from dataclasses import dataclass

from .game import Game
from .population import Population


@dataclass
class DetailedStatistics:
    """Estatísticas detalhadas de análise"""
    # Frequências
    number_frequencies: List[int]
    frequency_std: float
    frequency_entropy: float
    
    # Distribuições
    pair_distribution: Dict[int, int]
    sum_distribution: Dict[int, int]
    line_distribution: Dict[int, Dict[int, int]]
    column_distribution: Dict[int, Dict[int, int]]
    
    # Análises especiais
    consecutive_analysis: Dict[int, int]
    border_analysis: Dict[int, int]
    center_analysis: Dict[int, int]
    
    # Heatmap
    heatmap_data: List[List[int]]
    
    # Tendências
    trends: Dict[str, Any]
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'number_frequencies': self.number_frequencies,
            'frequency_std': self.frequency_std,
            'frequency_entropy': self.frequency_entropy,
            'pair_distribution': self.pair_distribution,
            'sum_distribution': self.sum_distribution,
            'line_distribution': self.line_distribution,
            'column_distribution': self.column_distribution,
            'consecutive_analysis': self.consecutive_analysis,
            'border_analysis': self.border_analysis,
            'center_analysis': self.center_analysis,
            'heatmap_data': self.heatmap_data,
            'trends': self.trends
        }


class StatisticsAnalyzer:
    """
    Analisador estatístico de jogos da Lotofácil
    
    Fornece análises detalhadas e visualizações de dados
    """
    
    def __init__(self):
        self.data = None
    
    def analyze_population(self, population: Population) -> DetailedStatistics:
        """
        Analisa uma população de jogos
        
        Args:
            population: População a ser analisada
            
        Returns:
            Estatísticas detalhadas
        """
        games = population.games
        if not games:
            return self._empty_statistics()
        
        # Frequências
        freq = self._calculate_frequencies(games)
        
        # Distribuições
        pair_dist = self._calculate_pair_distribution(games)
        sum_dist = self._calculate_sum_distribution(games)
        line_dist = self._calculate_line_distribution(games)
        col_dist = self._calculate_column_distribution(games)
        
        # Análises especiais
        consec_analysis = self._calculate_consecutive_analysis(games)
        border_analysis = self._calculate_border_analysis(games)
        center_analysis = self._calculate_center_analysis(games)
        
        # Heatmap
        heatmap = self._generate_heatmap(games)
        
        # Tendências
        trends = self._calculate_trends(games)
        
        return DetailedStatistics(
            number_frequencies=freq,
            frequency_std=np.std(freq),
            frequency_entropy=self._calculate_entropy(freq),
            pair_distribution=pair_dist,
            sum_distribution=sum_dist,
            line_distribution=line_dist,
            column_distribution=col_dist,
            consecutive_analysis=consec_analysis,
            border_analysis=border_analysis,
            center_analysis=center_analysis,
            heatmap_data=heatmap,
            trends=trends
        )
    
    def _empty_statistics(self) -> DetailedStatistics:
        """Retorna estatísticas vazias"""
        empty = [0] * 25
        return DetailedStatistics(
            number_frequencies=empty,
            frequency_std=0.0,
            frequency_entropy=0.0,
            pair_distribution={},
            sum_distribution={},
            line_distribution={},
            column_distribution={},
            consecutive_analysis={},
            border_analysis={},
            center_analysis={},
            heatmap_data=[[0] * 5 for _ in range(5)],
            trends={}
        )
    
    def _calculate_frequencies(self, games: List[Game]) -> List[int]:
        """Calcula frequência de cada número"""
        freq = [0] * 25
        for game in games:
            for num in game.numbers:
                freq[num - 1] += 1
        return freq
    
    def _calculate_entropy(self, frequencies: List[int]) -> float:
        """Calcula entropia da distribuição de frequências"""
        total = sum(frequencies)
        if total == 0:
            return 0.0
        
        probs = [f / total for f in frequencies if f > 0]
        entropy = -sum(p * np.log2(p) for p in probs)
        return entropy
    
    def _calculate_pair_distribution(self, games: List[Game]) -> Dict[int, int]:
        """Calcula distribuição de pares por jogo"""
        dist = {}
        for game in games:
            pairs = game.pares
            dist[pairs] = dist.get(pairs, 0) + 1
        return dict(sorted(dist.items()))
    
    def _calculate_sum_distribution(self, games: List[Game]) -> Dict[int, int]:
        """Calcula distribuição de somas"""
        dist = {}
        for game in games:
            soma = game.soma
            # Agrupa em intervalos de 10
            bucket = (soma // 10) * 10
            dist[bucket] = dist.get(bucket, 0) + 1
        return dict(sorted(dist.items()))
    
    def _calculate_line_distribution(self, games: List[Game]) -> Dict[int, Dict[int, int]]:
        """Calcula distribuição por linhas"""
        dist = {i: {} for i in range(5)}
        for game in games:
            for line, count in enumerate(game.linhas):
                dist[line][count] = dist[line].get(count, 0) + 1
        return dist
    
    def _calculate_column_distribution(self, games: List[Game]) -> Dict[int, Dict[int, int]]:
        """Calcula distribuição por colunas"""
        dist = {i: {} for i in range(5)}
        for game in games:
            for col, count in enumerate(game.colunas):
                dist[col][count] = dist[col].get(count, 0) + 1
        return dist
    
    def _calculate_consecutive_analysis(self, games: List[Game]) -> Dict[int, int]:
        """Analisa números consecutivos"""
        dist = {}
        for game in games:
            consec = game.consecutivos
            dist[consec] = dist.get(consec, 0) + 1
        return dict(sorted(dist.items()))
    
    def _calculate_border_analysis(self, games: List[Game]) -> Dict[int, int]:
        """Analisa números na moldura"""
        dist = {}
        for game in games:
            border = game.moldura
            dist[border] = dist.get(border, 0) + 1
        return dict(sorted(dist.items()))
    
    def _calculate_center_analysis(self, games: List[Game]) -> Dict[int, int]:
        """Analisa números no centro"""
        dist = {}
        for game in games:
            center = game.centro
            dist[center] = dist.get(center, 0) + 1
        return dict(sorted(dist.items()))
    
    def _generate_heatmap(self, games: List[Game]) -> List[List[int]]:
        """Gera dados para heatmap (matriz 5x5)"""
        heatmap = [[0] * 5 for _ in range(5)]
        for game in games:
            for num in game.numbers:
                row = (num - 1) // 5
                col = (num - 1) % 5
                heatmap[row][col] += 1
        return heatmap
    
    def _calculate_trends(self, games: List[Game]) -> Dict[str, Any]:
        """Calcula tendências nos dados"""
        if not games:
            return {}
        
        # Tendências de soma
        sums = [game.soma for game in games]
        
        # Tendências de pares
        pairs = [game.pares for game in games]
        
        # Tendências de distribuição
        freq = self._calculate_frequencies(games)
        freq_mean = np.mean(freq)
        
        return {
            'avg_sum': np.mean(sums),
            'sum_trend': 'crescente' if sums[-1] > sums[0] else 'decrescente',
            'avg_pairs': np.mean(pairs),
            'pairs_std': np.std(pairs),
            'freq_mean': freq_mean,
            'freq_above_mean': sum(1 for f in freq if f > freq_mean),
            'freq_below_mean': sum(1 for f in freq if f < freq_mean)
        }
    
    def to_dataframe(self, games: List[Game]) -> pd.DataFrame:
        """
        Converte jogos para DataFrame pandas
        
        Útil para análises e exportação
        """
        data = []
        for game in games:
            row = {
                'numbers': str(game.numbers),
                'mask': game.mask,
                'soma': game.soma,
                'pares': game.pares,
                'impares': game.impares,
                'moldura': game.moldura,
                'centro': game.centro,
                'consecutivos': game.consecutivos,
                'score': game.score
            }
            
            # Adiciona colunas para cada número
            for i, num in enumerate(game.numbers, 1):
                row[f'n{i}'] = num
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def find_patterns(self, games: List[Game]) -> Dict[str, Any]:
        """
        Encontra padrões nos jogos
        
        Returns:
            Dicionário com padrões identificados
        """
        patterns = {}
        
        # Frequência de pares
        pair_counts = Counter(g.pares for g in games)
        most_common_pairs = pair_counts.most_common(3)
        patterns['pares_mais_comuns'] = most_common_pairs
        
        # Intervalos de soma
        sum_counts = Counter((g.soma // 10) * 10 for g in games)
        most_common_sums = sum_counts.most_common(3)
        patterns['somas_mais_comuns'] = most_common_sums
        
        # Números que mais aparecem juntos
        pair_freq = {}
        for game in games:
            for i in range(len(game.numbers)):
                for j in range(i + 1, len(game.numbers)):
                    pair = (game.numbers[i], game.numbers[j])
                    pair_freq[pair] = pair_freq.get(pair, 0) + 1
        
        # Top 10 pares
        top_pairs = sorted(pair_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        patterns['pares_mais_frequentes'] = [(f"{a}-{b}", count) for (a, b), count in top_pairs]
        
        return patterns
