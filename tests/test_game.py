"""
Testes unitários para o módulo Game
"""
import unittest
import random
from core.game import Game, GameGenerator


class TestGame(unittest.TestCase):
    """Testes para a classe Game"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.game_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.game = Game(self.game_numbers)
    
    def test_game_creation(self):
        """Testa criação de jogo"""
        self.assertEqual(len(self.game.numbers), 15)
        self.assertEqual(self.game.soma, 120)
        self.assertEqual(self.game.pares, 7)
        self.assertEqual(self.game.impares, 8)
    
    def test_invalid_game(self):
        """Testa jogo inválido"""
        # Menos de 15 números
        with self.assertRaises(ValueError):
            Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        
        # Números duplicados
        with self.assertRaises(ValueError):
            Game([1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        
        # Números fora do intervalo
        with self.assertRaises(ValueError):
            Game([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
        
        with self.assertRaises(ValueError):
            Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 26])
    
    def test_bitmask(self):
        """Testa cálculo de bitmask"""
        mask = self.game.mask
        self.assertIsInstance(mask, int)
        self.assertGreater(mask, 0)
        
        # Verifica se a máscara está correta
        for i, num in enumerate(self.game.numbers):
            bit = (mask >> (num - 1)) & 1
            self.assertEqual(bit, 1)
    
    def test_overlap(self):
        """Testa cálculo de sobreposição"""
        game1 = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        game2 = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16])
        
        overlap = game1.overlap(game2)
        self.assertEqual(overlap, 14)  # 14 números em comum
        
        game3 = Game([11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
        overlap = game1.overlap(game3)
        self.assertEqual(overlap, 5)  # 5 números em comum (11-15)
    
    def test_lines(self):
        """Testa distribuição por linhas"""
        # Linhas: 1-5, 6-10, 11-15, 16-20, 21-25
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.assertEqual(game.linhas, [5, 5, 5, 0, 0])
        
        game = Game([1, 6, 11, 16, 21, 2, 7, 12, 17, 22, 3, 8, 13, 18, 23])
        self.assertEqual(game.linhas, [3, 3, 3, 3, 3])
    
    def test_columns(self):
        """Testa distribuição por colunas"""
        # Colunas: posição mod 5
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.assertEqual(game.colunas, [3, 3, 3, 3, 3])
        
        game = Game([1, 6, 11, 16, 21, 2, 7, 12, 17, 22, 3, 8, 13, 18, 23])
        self.assertEqual(game.colunas, [5, 5, 5, 0, 0])
    
    def test_border(self):
        """Testa números na moldura"""
        # Números na moldura: 1-5, 6, 10, 11, 15, 16, 20, 21-25
        game = Game([1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24])
        self.assertEqual(game.moldura, 15)  # Todos na moldura
        
        # Números no centro: 7-9, 12-14, 17-19
        game = Game([7, 8, 9, 12, 13, 14, 17, 18, 19, 1, 2, 3, 4, 5, 6])
        self.assertEqual(game.moldura, 6)  # 1-6 na moldura
        self.assertEqual(game.centro, 9)  # 7-9, 12-14, 17-19 no centro
    
    def test_center(self):
        """Testa números no centro"""
        game = Game([7, 8, 9, 12, 13, 14, 17, 18, 19, 1, 2, 3, 4, 5, 6])
        self.assertEqual(game.centro, 9)
        
        game = Game([1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24])
        self.assertEqual(game.centro, 0)  # Nenhum no centro
    
    def test_consecutive(self):
        """Testa números consecutivos"""
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.assertEqual(game.consecutivos, 15)  # Todos consecutivos
        
        game = Game([1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 15, 17, 19, 21])
        self.assertEqual(game.consecutivos, 5)  # 1-5
        
        game = Game([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 2, 4])
        self.assertEqual(game.consecutivos, 2)  # Apenas pares/ímpares consecutivos
    
    def test_game_generator(self):
        """Testa gerador de jogos"""
        # Gera um jogo
        game = GameGenerator.generate_random()
        self.assertIsInstance(game, Game)
        self.assertEqual(len(game.numbers), 15)
        
        # Gera múltiplos jogos
        games = GameGenerator.generate_many(100)
        self.assertEqual(len(games), 100)
        
        # Verifica unicidade
        masks = [g.mask for g in games]
        self.assertEqual(len(set(masks)), 100)
    
    def test_game_hash(self):
        """Testa hash e igualdade de jogos"""
        game1 = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        game2 = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        game3 = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16])
        
        self.assertEqual(game1, game2)
        self.assertNotEqual(game1, game3)
        self.assertEqual(hash(game1), hash(game2))
        self.assertNotEqual(hash(game1), hash(game3))
    
    def test_game_to_dict(self):
        """Testa conversão para dicionário"""
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        data = game.to_dict()
        
        self.assertIn('numbers', data)
        self.assertIn('mask', data)
        self.assertIn('soma', data)
        self.assertIn('pares', data)
        self.assertIn('score', data)
        
        self.assertEqual(data['numbers'], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])


if __name__ == '__main__':
    unittest.main()
