"""
Testes unitários para o módulo Scorer
"""
import unittest
from core.game import Game, GameGenerator
from core.scorer import (
    GameScorer, FrequencyScore, OverlapScore, 
    ParityScore, LineScore, ColumnScore, 
    BorderScore, CenterScore
)


class TestScorerMetrics(unittest.TestCase):
    """Testes para métricas individuais"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.games = GameGenerator.generate_many(20)
    
    def test_frequency_score(self):
        """Testa FrequencyScore"""
        scorer = FrequencyScore()
        score = scorer.calculate(self.games)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
        
        # Distribuição perfeitamente equilibrada
        perfect_games = []
        for i in range(20):
            numbers = list(range(1, 16))
            perfect_games.append(Game(numbers))
        
        score = scorer.calculate(perfect_games)
        # Deve ser próximo de 1
        self.assertGreater(score, 0.9)
    
    def test_overlap_score(self):
        """Testa OverlapScore"""
        scorer = OverlapScore(max_overlap=8)
        score = scorer.calculate(self.games)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
        
        # Jogos com muita sobreposição
        overlapping_games = [
            Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
            Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16])
        ]
        score = scorer.calculate(overlapping_games)
        self.assertLess(score, 1.0)  # Penalizado
    
    def test_parity_score(self):
        """Testa ParityScore"""
        scorer = ParityScore(ideal_parity=0.5)
        
        # Perfeitamente balanceado
        balanced_game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        # 7 pares, 8 ímpares => próximo de 0.5
        score = scorer.calculate([balanced_game])
        self.assertGreater(score, 0.8)
        
        # Desbalanceado
        unbalanced_game = Game([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 2, 4])
        # 2 pares, 13 ímpares => longe de 0.5
        score = scorer.calculate([unbalanced_game])
        self.assertLess(score, 0.5)
    
    def test_line_score(self):
        """Testa LineScore"""
        scorer = LineScore()
        
        # Distribuição perfeita
        perfect_games = []
        for i in range(5):
            numbers = list(range(i*5 + 1, i*5 + 16))
            perfect_games.append(Game(numbers))
        
        score = scorer.calculate(perfect_games)
        self.assertGreater(score, 0.8)
        
        # Distribuição desigual
        bad_games = []
        for i in range(5):
            numbers = list(range(1, 16))
            bad_games.append(Game(numbers))
        
        score = scorer.calculate(bad_games)
        self.assertLess(score, 0.5)
    
    def test_column_score(self):
        """Testa ColumnScore"""
        scorer = ColumnScore()
        
        # Distribuição perfeita
        perfect_games = []
        for i in range(5):
            numbers = [i+1, i+6, i+11, i+16, i+21, i+2, i+7, i+12, i+17, i+22, 
                      i+3, i+8, i+13, i+18, i+23]
            perfect_games.append(Game(numbers))
        
        score = scorer.calculate(perfect_games)
        self.assertGreater(score, 0.8)
    
    def test_border_score(self):
        """Testa BorderScore"""
        scorer = BorderScore(ideal_border=0.4)
        
        # Perfeito (40% na moldura)
        border_game = Game([1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24])
        # 15 números na moldura => 100%
        score = scorer.calculate([border_game])
        self.assertLess(score, 0.5)  # Longe do ideal
        
        # Mais balanceado
        balanced_game = Game([1, 2, 3, 4, 5, 7, 8, 9, 12, 13, 14, 17, 18, 19, 24])
        # 6 números na moldura => 40%
        score = scorer.calculate([balanced_game])
        self.assertGreater(score, 0.8)
    
    def test_center_score(self):
        """Testa CenterScore"""
        scorer = CenterScore(ideal_center=0.2)
        
        # Perfeito (20% no centro)
        center_game = Game([7, 8, 9, 12, 13, 14, 17, 18, 19, 1, 2, 3, 4, 5, 6])
        # 9 números no centro => 60%
        score = scorer.calculate([center_game])
        self.assertLess(score, 0.5)  # Longe do ideal


class TestGameScorer(unittest.TestCase):
    """Testes para GameScorer"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.config = {
            'pesos': {
                'frequencia': 0.25,
                'sobreposicao': 0.25,
                'pares': 0.10,
                'linhas': 0.15,
                'colunas': 0.15,
                'moldura': 0.10
            },
            'max_overlap': 8
        }
        self.scorer = GameScorer(self.config)
        self.games = GameGenerator.generate_many(20)
    
    def test_calculate_metrics(self):
        """Testa cálculo de métricas completas"""
        metrics = self.scorer.calculate(self.games)
        
        self.assertIsNotNone(metrics.frequency)
        self.assertIsNotNone(metrics.overlap)
        self.assertIsNotNone(metrics.parity)
        self.assertIsNotNone(metrics.lines)
        self.assertIsNotNone(metrics.columns)
        self.assertIsNotNone(metrics.border)
        self.assertIsNotNone(metrics.center)
        self.assertIsNotNone(metrics.total)
        
        self.assertGreaterEqual(metrics.total, 0)
        self.assertLessEqual(metrics.total, 1)
    
    def test_score_individual(self):
        """Testa score de jogo individual"""
        game = self.games[0]
        score = self.scorer.score_individual(game)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_score_game_in_population(self):
        """Testa score de jogo em população"""
        game = self.games[0]
        score = self.scorer.score_game(game, self.games[1:])
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_weight_normalization(self):
        """Testa normalização de pesos"""
        # Pesos devem somar 1
        total_weight = sum(self.scorer.weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
