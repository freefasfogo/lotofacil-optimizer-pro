"""
Testes unitários para o módulo Population
"""
import unittest
from core.game import Game, GameGenerator
from core.population import Population, PopulationFactory
from core.scorer import GameScorer


class TestPopulation(unittest.TestCase):
    """Testes para a classe Population"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.games = GameGenerator.generate_many(20)
        self.config = {
            'pesos': {
                'frequencia': 0.25,
                'sobreposicao': 0.25,
                'pares': 0.10,
                'linhas': 0.15,
                'colunas': 0.15,
                'moldura': 0.10
            }
        }
        self.scorer = GameScorer(self.config)
        self.population = Population(self.games, self.scorer)
    
    def test_population_creation(self):
        """Testa criação de população"""
        self.assertEqual(len(self.population), 20)
        self.assertIsNotNone(self.population.get_frequency())
        self.assertEqual(len(self.population.get_frequency()), 25)
    
    def test_add_game(self):
        """Testa adição de jogo"""
        new_game = GameGenerator.generate_random()
        added = self.population.add_game(new_game)
        self.assertTrue(added)
        self.assertEqual(len(self.population), 21)
        
        # Tentar adicionar jogo duplicado
        duplicate = Game(self.games[0].numbers)
        added = self.population.add_game(duplicate)
        self.assertFalse(added)
        self.assertEqual(len(self.population), 21)
    
    def test_remove_game(self):
        """Testa remoção de jogo"""
        game_to_remove = self.population.games[0]
        removed = self.population.remove_game(game_to_remove)
        self.assertTrue(removed)
        self.assertEqual(len(self.population), 19)
        
        # Tentar remover jogo inexistente
        non_existent = GameGenerator.generate_random()
        removed = self.population.remove_game(non_existent)
        self.assertFalse(removed)
    
    def test_get_score(self):
        """Testa obtenção de score"""
        score = self.population.get_score()
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
    
    def test_get_statistics(self):
        """Testa obtenção de estatísticas"""
        stats = self.population.get_statistics()
        
        self.assertEqual(stats.size, 20)
        self.assertIsInstance(stats.avg_score, float)
        self.assertIsInstance(stats.max_score, float)
        self.assertIsInstance(stats.min_score, float)
        self.assertIsInstance(stats.std_score, float)
        self.assertIsInstance(stats.diversity_score, float)
        self.assertEqual(len(stats.frequency_distribution), 25)
    
    def test_get_best_games(self):
        """Testa obtenção dos melhores jogos"""
        best = self.population.get_best_games(5)
        self.assertEqual(len(best), 5)
        
        # Verifica se estão ordenados
        for i in range(len(best) - 1):
            self.assertGreaterEqual(best[i].score, best[i+1].score)
    
    def test_get_worst_games(self):
        """Testa obtenção dos piores jogos"""
        worst = self.population.get_worst_games(5)
        self.assertEqual(len(worst), 5)
        
        # Verifica se estão ordenados
        for i in range(len(worst) - 1):
            self.assertLessEqual(worst[i].score, worst[i+1].score)
    
    def test_replace_worst(self):
        """Testa substituição dos piores jogos"""
        new_games = GameGenerator.generate_many(5)
        replaced = self.population.replace_worst(new_games, self.scorer)
        self.assertEqual(replaced, 5)
        self.assertEqual(len(self.population), 20)
    
    def test_mutate(self):
        """Testa mutação da população"""
        mutated = self.population.mutate(mutation_rate=0.5)
        self.assertEqual(len(mutated), 20)
        self.assertIsInstance(mutated, Population)
    
    def test_crossover(self):
        """Testa crossover entre populações"""
        other_population = Population(
            GameGenerator.generate_many(20),
            self.scorer
        )
        
        new_population = self.population.crossover(other_population)
        self.assertEqual(len(new_population), 20)
        self.assertIsInstance(new_population, Population)
    
    def test_clone(self):
        """Testa clonagem de população"""
        clone = self.population.clone()
        self.assertEqual(len(clone), 20)
        self.assertIsNot(clone, self.population)  # Objetos diferentes
        
        # Verifica se os jogos são cópias
        for i in range(len(clone)):
            self.assertEqual(clone[i].mask, self.population[i].mask)
            self.assertIsNot(clone[i], self.population[i])


class TestPopulationFactory(unittest.TestCase):
    """Testes para PopulationFactory"""
    
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
            }
        }
        self.scorer = GameScorer(self.config)
    
    def test_create_random(self):
        """Testa criação de população aleatória"""
        population = PopulationFactory.create_random(30, self.scorer)
        self.assertEqual(len(population), 30)
        self.assertIsNotNone(population.get_score())
    
    def test_create_from_games(self):
        """Testa criação a partir de jogos"""
        games = GameGenerator.generate_many(15)
        population = PopulationFactory.create_from_games(games, self.scorer)
        self.assertEqual(len(population), 15)
        
        # Verifica se os jogos são os mesmos
        for i in range(len(population)):
            self.assertEqual(population[i].mask, games[i].mask)
    
    def test_create_balanced(self):
        """Testa criação de população balanceada"""
        population = PopulationFactory.create_balanced(20, self.scorer)
        self.assertEqual(len(population), 20)
        
        # Verifica distribuição balanceada
        freq = population.get_frequency()
        self.assertLessEqual(max(freq) - min(freq), 5)  # Diferença máxima de 5


if __name__ == '__main__':
    unittest.main()
