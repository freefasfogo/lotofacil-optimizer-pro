"""
Pacote do núcleo do sistema
"""
from .game import Game, GameGenerator
from .validator import GameValidator
from .scorer import GameScorer, ScoreMetrics
from .population import Population, PopulationFactory, PopulationStats
from .statistics import StatisticsAnalyzer, DetailedStatistics

__all__ = [
    'Game',
    'GameGenerator',
    'GameValidator',
    'GameScorer',
    'ScoreMetrics',
    'Population',
    'PopulationFactory',
    'PopulationStats',
    'StatisticsAnalyzer',
    'DetailedStatistics'
]
