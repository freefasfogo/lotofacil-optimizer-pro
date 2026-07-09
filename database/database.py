"""
Módulo de gerenciamento do banco de dados SQLite
"""
import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from .models import Game, OptimizationRun, GameHistory


class Database:
    """Gerenciador do banco de dados"""
    
    def __init__(self, db_path: str = "data/lotofacil.db"):
        self.db_path = db_path
        self._ensure_directories()
        self._init_database()
    
    def _ensure_directories(self):
        """Garante que os diretórios necessários existam"""
        Path("data").mkdir(exist_ok=True)
    
    def _init_database(self):
        """Inicializa as tabelas do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabela de jogos - usando mask
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numbers TEXT NOT NULL,
                    mask INTEGER NOT NULL,
                    score REAL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Tabela de execuções de otimização
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS optimization_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    algorithm TEXT NOT NULL,
                    generation INTEGER NOT NULL,
                    best_score REAL NOT NULL,
                    population_size INTEGER NOT NULL,
                    duration REAL NOT NULL,
                    config TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Tabela de histórico de jogos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id INTEGER NOT NULL,
                    run_id INTEGER NOT NULL,
                    numbers TEXT NOT NULL,
                    score REAL NOT NULL,
                    metrics TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (game_id) REFERENCES games(id),
                    FOREIGN KEY (run_id) REFERENCES optimization_runs(id)
                )
            """)
            
            # Índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_games_created_at 
                ON games(created_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_run_id 
                ON game_history(run_id)
            """)
            
            conn.commit()
    
    def save_game(self, game) -> int:
        """Salva um jogo no banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (numbers, mask, score, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                json.dumps(game.numbers),
                game.mask,
                float(game.score),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
    
    def save_optimization_run(self, run: OptimizationRun) -> int:
        """Salva uma execução de otimização"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO optimization_runs 
                (algorithm, generation, best_score, population_size, 
                 duration, config, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                run.algorithm,
                run.generation,
                float(run.best_score),
                run.population_size,
                float(run.duration),
                json.dumps(run.config),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
    
    def save_game_history(self, history: GameHistory) -> int:
        """Salva um histórico de jogo"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO game_history 
                (game_id, run_id, numbers, score, metrics, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                history.game_id,
                history.run_id,
                json.dumps(history.numbers),
                float(history.score),
                json.dumps(history.metrics),
                datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid
    
    def get_best_games(self, limit: int = 10) -> List:
        """Retorna os melhores jogos"""
        from .models import Game
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM games 
                ORDER BY score DESC 
                LIMIT ?
            """, (limit,))
            
            games = []
            for row in cursor.fetchall():
                game = Game(
                    id=row['id'],
                    numbers=json.loads(row['numbers']),
                    mask=row['mask'],
                    score=row['score'],
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                games.append(game)
            
            return games
    
    def get_optimization_history(self, limit: int = 20) -> List[OptimizationRun]:
        """Retorna o histórico de otimizações"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM optimization_runs 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            runs = []
            for row in cursor.fetchall():
                run = OptimizationRun(
                    id=row['id'],
                    algorithm=row['algorithm'],
                    generation=row['generation'],
                    best_score=row['best_score'],
                    population_size=row['population_size'],
                    duration=row['duration'],
                    config=json.loads(row['config']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                runs.append(run)
            
            return runs
    
    def get_games_by_run(self, run_id: int) -> List[GameHistory]:
        """Retorna os jogos de uma execução específica"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM game_history 
                WHERE run_id = ?
                ORDER BY score DESC
            """, (run_id,))
            
            histories = []
            for row in cursor.fetchall():
                history = GameHistory(
                    id=row['id'],
                    game_id=row['game_id'],
                    run_id=row['run_id'],
                    numbers=json.loads(row['numbers']),
                    score=row['score'],
                    metrics=json.loads(row['metrics']),
                    created_at=datetime.fromisoformat(row['created_at'])
                )
                histories.append(history)
            
            return histories
    
    def clear_all(self):
        """Limpa todos os dados do banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM game_history")
            cursor.execute("DELETE FROM optimization_runs")
            cursor.execute("DELETE FROM games")
            conn.commit()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do banco"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM games")
            total_games = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(score) FROM games")
            avg_score = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT MAX(score) FROM games")
            best_score = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM optimization_runs")
            total_runs = cursor.fetchone()[0]
            
            return {
                'total_games': total_games,
                'avg_score': avg_score,
                'best_score': best_score,
                'total_runs': total_runs
            }
