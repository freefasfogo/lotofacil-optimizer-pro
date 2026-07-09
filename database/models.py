"""
Models para o banco de dados SQLite
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import json


@dataclass
class Game:
    """Modelo para um jogo da Lotofácil"""
    id: Optional[int] = None
    numbers: List[int] = None
    mask: int = 0  # Mudando de bitmask para mask
    score: float = 0.0
    created_at: datetime = None
    
    def __post_init__(self):
        if self.numbers is None:
            self.numbers = []
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'numbers': json.dumps(self.numbers),
            'mask': self.mask,  # Mudando de bitmask para mask
            'score': self.score,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Game':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get('id'),
            numbers=json.loads(data['numbers']),
            mask=data['mask'],  # Mudando de bitmask para mask
            score=data['score'],
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class OptimizationRun:
    """Modelo para uma execução de otimização"""
    id: Optional[int] = None
    algorithm: str = ""
    generation: int = 0
    best_score: float = 0.0
    population_size: int = 0
    duration: float = 0.0
    config: dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = {}
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'algorithm': self.algorithm,
            'generation': self.generation,
            'best_score': self.best_score,
            'population_size': self.population_size,
            'duration': self.duration,
            'config': json.dumps(self.config),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'OptimizationRun':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get('id'),
            algorithm=data['algorithm'],
            generation=data['generation'],
            best_score=data['best_score'],
            population_size=data['population_size'],
            duration=data['duration'],
            config=json.loads(data['config']),
            created_at=datetime.fromisoformat(data['created_at'])
        )


@dataclass
class GameHistory:
    """Modelo para histórico de jogos"""
    id: Optional[int] = None
    game_id: int = 0
    run_id: int = 0
    numbers: List[int] = None
    score: float = 0.0
    metrics: dict = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.numbers is None:
            self.numbers = []
        if self.metrics is None:
            self.metrics = {}
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'run_id': self.run_id,
            'numbers': json.dumps(self.numbers),
            'score': self.score,
            'metrics': json.dumps(self.metrics),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GameHistory':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data.get('id'),
            game_id=data['game_id'],
            run_id=data['run_id'],
            numbers=json.loads(data['numbers']),
            score=data['score'],
            metrics=json.loads(data['metrics']),
            created_at=datetime.fromisoformat(data['created_at'])
        )
