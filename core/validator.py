"""
Módulo de validação de jogos da Lotofácil
"""
from typing import List, Dict, Any, Optional
from .game import Game


class GameValidator:
    """Validador de jogos da Lotofácil"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o validador com as configurações
        
        Args:
            config: Dicionário com as configurações de validação
        """
        self.config = config
        self.validations = config.get('validacoes', {})
    
    def validate(self, game: Game) -> Tuple[bool, List[str]]:
        """
        Valida um jogo completo
        
        Returns:
            Tuple (válido, lista de erros)
        """
        errors = []
        
        # Validações básicas
        if len(game.numbers) != 15:
            errors.append(f"Jogo deve ter 15 dezenas, tem {len(game.numbers)}")
        
        if len(set(game.numbers)) != len(game.numbers):
            errors.append("Dezenas duplicadas não são permitidas")
        
        if not all(1 <= n <= 25 for n in game.numbers):
            errors.append("Dezenas devem estar entre 1 e 25")
        
        # Validações configuráveis
        if self.validations:
            errors.extend(self._validate_pares_impares(game))
            errors.extend(self._validate_soma(game))
            errors.extend(self._validate_consecutivos(game))
        
        return len(errors) == 0, errors
    
    def _validate_pares_impares(self, game: Game) -> List[str]:
        """Valida a proporção de pares e ímpares"""
        errors = []
        
        min_pares = self.validations.get('min_pares', 6)
        max_pares = self.validations.get('max_pares', 9)
        
        if game.pares < min_pares or game.pares > max_pares:
            errors.append(
                f"Quantidade de pares ({game.pares}) fora do intervalo "
                f"[{min_pares}, {max_pares}]"
            )
        
        return errors
    
    def _validate_soma(self, game: Game) -> List[str]:
        """Valida a soma das dezenas"""
        errors = []
        
        min_soma = self.validations.get('min_soma', 100)
        max_soma = self.validations.get('max_soma', 200)
        
        if game.soma < min_soma or game.soma > max_soma:
            errors.append(
                f"Soma ({game.soma}) fora do intervalo "
                f"[{min_soma}, {max_soma}]"
            )
        
        return errors
    
    def _validate_consecutivos(self, game: Game) -> List[str]:
        """Valida a quantidade de números consecutivos"""
        errors = []
        
        max_consec = self.validations.get('max_consecutivos', 3)
        
        if game.consecutivos > max_consec:
            errors.append(
                f"Números consecutivos ({game.consecutivos}) "
                f"excede o máximo permitido ({max_consec})"
            )
        
        return errors
    
    def validate_population(self, games: List[Game]) -> Dict[str, Any]:
        """
        Valida uma população de jogos
        
        Returns:
            Dicionário com estatísticas de validação
        """
        valid_count = 0
        errors_by_type = {}
        
        for game in games:
            is_valid, errors = self.validate(game)
            if is_valid:
                valid_count += 1
            else:
                for error in errors:
                    error_type = error.split(' ')[0] if error else 'unknown'
                    errors_by_type[error_type] = errors_by_type.get(error_type, 0) + 1
        
        return {
            'total': len(games),
            'valid': valid_count,
            'invalid': len(games) - valid_count,
            'errors_by_type': errors_by_type,
            'validity_rate': valid_count / len(games) if games else 0
        }
