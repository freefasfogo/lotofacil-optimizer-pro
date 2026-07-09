"""
Pacote da interface gráfica
"""
from .main_window import MainWindow
from .widgets import (
    ProgressWidget,
    GameDisplayWidget,
    StatisticsWidget,
    FrequencyChartWidget,
    BestGamesWidget
)

__all__ = [
    'MainWindow',
    'ProgressWidget',
    'GameDisplayWidget',
    'StatisticsWidget',
    'FrequencyChartWidget',
    'BestGamesWidget'
]
