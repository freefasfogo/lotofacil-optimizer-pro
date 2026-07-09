"""
Testes unitários para os algoritmos de otimização
"""
import unittest
from core.game import GameGenerator
from core.population import Population
from core.scorer import GameScorer
from algorithms.hill_climbing import HillClimbing
from algorithms.simulated_annealing import SimulatedAnnealing
from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.tabu_search import TabuSearch


class TestAlgorithms(unittest.TestCase):
    """Testes para algoritmos de otimização"""
    
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
            'populacao': 20,
            'geracoes': 10,  # Reduzido para testes rápidos
            'max_iterations': 10,
            'temperatura_inicial': 100,
            'temperatura_final': 10,
            'cooling_rate': 0.95,
            'taxa_mutacao': 0.1,
            'taxa_crossover': 0.8
        }
        self.scorer = GameScorer(self.config)
        self.initial_population = Population(
            GameGenerator.generate_many(20),
            self.scorer
        )
    
    def test_hill_climbing(self):
        """Testa algoritmo Hill Climbing"""
        algorithm = HillClimbing(self.scorer, self.config)
        result = algorithm.optimize(self.initial_population)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.best_games), 0)
        self.assertGreaterEqual(result.best_score, 0)
        self.assertLessEqual(result.best_score, 1)
        self.assertGreater(result.iterations, 0)
        self.assertGreater(result.duration, 0)
    
    def test_simulated_annealing(self):
        """Testa algoritmo Simulated Annealing"""
        algorithm = SimulatedAnnealing(self.scorer, self.config)
        result = algorithm.optimize(self.initial_population)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.best_games), 0)
        self.assertGreaterEqual(result.best_score, 0)
        self.assertLessEqual(result.best_score, 1)
        self.assertGreater(result.iterations, 0)
        self.assertGreater(result.duration, 0)
    
    def test_genetic_algorithm(self):
        """Testa algoritmo Genético"""
        algorithm = GeneticAlgorithm(self.scorer, self.config)
        result = algorithm.optimize(self.initial_population)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.best_games), 0)
        self.assertGreaterEqual(result.best_score, 0)
        self.assertLessEqual(result.best_score, 1)
        self.assertGreater(result.iterations, 0)
        self.assertGreater(result.duration, 0)
    
    def test_tabu_search(self):
        """Testa algoritmo Tabu Search"""
        algorithm = TabuSearch(self.scorer, self.config)
        result = algorithm.optimize(self.initial_population)
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result.best_games), 0)
        self.assertGreaterEqual(result.best_score, 0)
        self.assertLessEqual(result.best_score, 1)
        self.assertGreater(result.iterations, 0)
        self.assertGreater(result.duration, 0)
    
    def test_algorithm_interface(self):
        """Testa interface comum dos algoritmos"""
        algorithms = [
            HillClimbing(self.scorer, self.config),
            SimulatedAnnealing(self.scorer, self.config),
            GeneticAlgorithm(self.scorer, self.config),
            TabuSearch(self.scorer, self.config)
        ]
        
        for algo in algorithms:
            # Verifica métodos obrigatórios
            self.assertTrue(hasattr(algo, 'optimize'))
            self.assertTrue(hasattr(algo, 'step'))
            self.assertTrue(hasattr(algo, 'get_progress'))
            self.assertTrue(hasattr(algo, 'get_status'))
            
            # Verifica funcionamento básico
            status = algo.get_status()
            self.assertIn('iterations', status)
            self.assertIn('best_score', status)
            self.assertIn('elapsed_time', status)
            self.assertIn('progress', status)
    
    def test_convergence(self):
        """Testa convergência dos algoritmos"""
        algorithm = GeneticAlgorithm(self.scorer, self.config)
        result = algorithm.optimize(self.initial_population)
        
        # Verifica se o score melhorou
        initial_score = self.initial_population.get_score()
        final_score = result.best_score
        
        self.assertGreaterEqual(final_score, initial_score)
        
        # Verifica histórico
        self.assertGreater(len(result.history), 0)
        self.assertGreater(len(result.convergence_data), 0)


if __name__ == '__main__':
    unittest.main()
