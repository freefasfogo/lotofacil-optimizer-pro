"""
Testes unitários para o módulo Validator
"""
import unittest
from core.game import Game
from core.validator import GameValidator


class TestValidator(unittest.TestCase):
    """Testes para a classe GameValidator"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.config = {
            'validacoes': {
                'min_pares': 6,
                'max_pares': 9,
                'min_impares': 6,
                'max_impares': 9,
                'min_soma': 100,
                'max_soma': 200,
                'max_consecutivos': 3
            }
        }
        self.validator = GameValidator(self.config)
    
    def test_valid_game(self):
        """Testa validação de jogo válido"""
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        is_valid, errors = self.validator.validate(game)
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_invalid_pares(self):
        """Testa validação de pares inválidos"""
        # Muitos pares
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 17])
        is_valid, errors = self.validator.validate(game)
        self.assertFalse(is_valid)
        self.assertTrue(any('pares' in e.lower() for e in errors))
        
        # Poucos pares
        game = Game([1, 2, 3, 4, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25])
        is_valid, errors = self.validator.validate(game)
        self.assertFalse(is_valid)
        self.assertTrue(any('pares' in e.lower() for e in errors))
    
    def test_invalid_soma(self):
        """Testa validação de soma inválida"""
        # Soma muito baixa
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        # Soma = 120, válida (entre 100 e 200)
        is_valid, errors = self.validator.validate(game)
        self.assertTrue(is_valid)
        
        # Soma muito alta
        game = Game([11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
        is_valid, errors = self.validator.validate(game)
        self.assertFalse(is_valid)
        self.assertTrue(any('soma' in e.lower() for e in errors))
    
    def test_invalid_consecutive(self):
        """Testa validação de consecutivos inválidos"""
        game = Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        is_valid, errors = self.validator.validate(game)
        self.assertFalse(is_valid)
        self.assertTrue(any('consecutivo' in e.lower() for e in errors))
    
    def test_validate_population(self):
        """Testa validação de população"""
        games = [
            Game([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
            Game([1, 2, 3, 4, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25]),
            Game([11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25])
        ]
        
        stats = self.validator.validate_population(games)
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['valid'], 1)  # Apenas o primeiro é válido
        self.assertEqual(stats['invalid'], 2)
        self.assertGreater(stats['validity_rate'], 0)


if __name__ == '__main__':
    unittest.main()
