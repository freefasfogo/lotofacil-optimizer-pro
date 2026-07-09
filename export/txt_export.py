"""
Módulo de exportação para TXT
"""
from typing import List
from datetime import datetime
from pathlib import Path

from core.game import Game


class TXTExporter:
    """
    Exportador para TXT simples
    
    Gera arquivo texto com:
    - Cabeçalho
    - Lista de jogos
    - Estatísticas básicas
    """
    
    def export(self, games: List[Game], filename: str):
        """
        Exporta jogos para arquivo TXT
        
        Args:
            games: Lista de jogos
            filename: Nome do arquivo
        """
        with open(filename, 'w', encoding='utf-8') as f:
            # Cabeçalho
            f.write("=" * 70 + "\n")
            f.write("LOTOFÁCIL OPTIMIZER PRO\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Total de Jogos: {len(games)}\n\n")
            
            # Jogos
            f.write("-" * 70 + "\n")
            f.write("JOGOS GERADOS\n")
            f.write("-" * 70 + "\n\n")
            
            for i, game in enumerate(games, 1):
                numbers_str = " ".join(f"{n:02d}" for n in game.numbers)
                f.write(f"Jogo {i:3d}: {numbers_str}")
                f.write(f"  | Soma: {game.soma:3d}")
                f.write(f"  | Pares: {game.pares:2d}")
                f.write(f"  | Ímpares: {game.impares:2d}")
                f.write(f"  | Score: {game.score:.4f}\n")
            
            # Estatísticas básicas
            f.write("\n" + "-" * 70 + "\n")
            f.write("ESTATÍSTICAS BÁSICAS\n")
            f.write("-" * 70 + "\n\n")
            
            if games:
                scores = [g.score for g in games]
                f.write(f"Score Médio: {sum(scores) / len(scores):.4f}\n")
                f.write(f"Melhor Score: {max(scores):.4f}\n")
                f.write(f"Pior Score: {min(scores):.4f}\n")
                f.write(f"Desvio Padrão: {self._std(scores):.4f}\n\n")
            
            # Frequência das dezenas
            f.write("-" * 70 + "\n")
            f.write("FREQUÊNCIA DAS DEZENAS\n")
            f.write("-" * 70 + "\n\n")
            
            freq = [0] * 25
            for game in games:
                for num in game.numbers:
                    freq[num - 1] += 1
            
            total = len(games) * 15
            for i, count in enumerate(freq, 1):
                f.write(f"Dezena {i:2d}: {count:3d}  ({count/total*100:5.2f}%)\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("FIM DO RELATÓRIO\n")
            f.write("=" * 70 + "\n")
    
    def _std(self, values: List[float]) -> float:
        """Calcula desvio padrão"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
