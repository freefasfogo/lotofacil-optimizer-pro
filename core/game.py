"""
Módulo para representação do jogo da Lotofácil
"""
from typing import List, Set, Tuple
from dataclasses import dataclass
import random


@dataclass
class Game:
    """Representação de um jogo da Lotofácil"""
    numbers: List[int]
    
    def __post_init__(self):
        """Inicializa todas as propriedades do jogo"""
        self.numbers = sorted(self.numbers)
        self._validate()
        self._calculate_properties()
    
    def _validate(self):
        """Valida o jogo"""
        if len(self.numbers) != 15:
            raise ValueError("Jogo deve ter exatamente 15 dezenas")
        
        if len(set(self.numbers)) != 15:
            raise ValueError("Dezenas devem ser únicas")
        
        if not all(1 <= n <= 25 for n in self.numbers):
            raise ValueError("Dezenas devem estar entre 1 e 25")
    
    def _calculate_properties(self):
        """Calcula todas as propriedades do jogo"""
        self.mask = self._calculate_mask()
        self.soma = sum(self.numbers)
        self.pares = sum(1 for n in self.numbers if n % 2 == 0)
        self.impares = 15 - self.pares
        self.linhas = self._calculate_lines()
        self.colunas = self._calculate_columns()
        self.moldura = self._calculate_border()
        self.centro = self._calculate_center()
        self.consecutivos = self._calculate_consecutive()
        self.score = 0.0
    
    def _calculate_mask(self) -> int:
        """Calcula o bitmask do jogo"""
        mask = 0
        for num in self.numbers:
            mask |= (1 << (num - 1))
        return mask
    
    def _calculate_lines(self) -> List[int]:
        """Calcula distribuição por linhas (1-5, 6-10, 11-15, 16-20, 21-25)"""
        lines = [0] * 5
        for num in self.numbers:
            line = (num - 1) // 5
            lines[line] += 1
        return lines
    
    def _calculate_columns(self) -> List[int]:
        """Calcula distribuição por colunas"""
        cols = [0] * 5
        for num in self.numbers:
            col = (num - 1) % 5
            cols[col] += 1
        return cols
    
    def _calculate_border(self) -> int:
        """Calcula quantidade de números na moldura"""
        border_numbers = {1, 2, 3, 4, 5, 6, 10, 11, 15, 16, 20, 21, 22, 23, 24, 25}
        return sum(1 for n in self.numbers if n in border_numbers)
    
    def _calculate_center(self) -> int:
        """Calcula quantidade de números no centro (7-9, 12-14, 17-19)"""
        center_numbers = {7, 8, 9, 12, 13, 14, 17, 18, 19}
        return sum(1 for n in self.numbers if n in center_numbers)
    
    def _calculate_consecutive(self) -> int:
        """Calcula o maior número de consecutivos"""
        max_consec = 1
        current_consec = 1
        
        for i in range(1, len(self.numbers)):
            if self.numbers[i] == self.numbers[i-1] + 1:
                current_consec += 1
                max_consec = max(max_consec, current_consec)
            else:
                current_consec = 1
        
        return max_consec
    
    def overlap(self, other: 'Game') -> int:
        """Calcula a sobreposição entre dois jogos usando bitmask"""
        return (self.mask & other.mask).bit_count()
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'numbers': self.numbers,
            'mask': self.mask,
            'soma': self.soma,
            'pares': self.pares,
            'impares': self.impares,
            'linhas': self.linhas,
            'colunas': self.colunas,
            'moldura': self.moldura,
            'centro': self.centro,
            'consecutivos': self.consecutivos,
            'score': self.score
        }
    
    def __hash__(self):
        return hash(self.mask)
    
    def __eq__(self, other):
        if not isinstance(other, Game):
            return False
        return self.mask == other.mask


class GameGenerator:
    """Gerador de jogos da Lotofácil"""
    
    @staticmethod
    def generate_random() -> Game:
        """Gera um jogo aleatório válido"""
        numbers = random.sample(range(1, 26), 15)
        return Game(numbers)
    
    @staticmethod
    def generate_from_mask(mask: int) -> Game:
        """Gera um jogo a partir de um bitmask"""
        numbers = []
        for i in range(25):
            if mask & (1 << i):
                numbers.append(i + 1)
        return Game(numbers)
    
    @staticmethod
    def generate_many(count: int) -> List[Game]:
        """Gera múltiplos jogos aleatórios"""
        games = []
        seen = set()
        attempts = 0
        max_attempts = count * 20
        
        while len(games) < count and attempts < max_attempts:
            attempts += 1
            game = GameGenerator.generate_random()
            if game.mask not in seen:
                seen.add(game.mask)
                games.append(game)
        
        return games
