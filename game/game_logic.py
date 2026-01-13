"""
Logica del gioco Morra Cinese
"""

import random
from typing import Tuple, Optional
from enum import Enum

class Move(Enum):
    """Enum per le mosse del gioco."""
    ROCK = 'rock'
    PAPER = 'paper'
    SCISSORS = 'scissors'
    
    @classmethod
    def from_gesture(cls, gesture: str) -> Optional['Move']:
        """Converte un gesto in una mossa."""
        gesture_map = {
            'rock': cls.ROCK,
            'paper': cls.PAPER,
            'scissors': cls.SCISSORS
        }
        return gesture_map.get(gesture)
    
    def get_italian_name(self) -> str:
        """Restituisce il nome italiano della mossa."""
        names = {
            Move.ROCK: 'Sasso',
            Move.PAPER: 'Carta',
            Move.SCISSORS: 'Forbice'
        }
        return names.get(self, '')
    
    def get_emoji(self) -> str:
        """Restituisce l'emoji della mossa."""
        symbols = {
            Move.ROCK: 'SASSO',
            Move.PAPER: 'CARTA',
            Move.SCISSORS: 'FORBICE'
        }
        return symbols.get(self, '')


class RoundResult(Enum):
    """Enum per i risultati di un round."""
    PLAYER_WIN = 'player'
    CPU_WIN = 'cpu'
    DRAW = 'draw'


class GameLogic:
    """
    Classe che gestisce la logica del gioco Morra Cinese.
    Modalità sopravvivenza: i round continuano finché l'utente non perde.
    """
    
    # Matrice delle vittorie: chiave = (mossa_giocatore, mossa_cpu)
    WIN_MATRIX = {
        (Move.ROCK, Move.SCISSORS): RoundResult.PLAYER_WIN,
        (Move.SCISSORS, Move.PAPER): RoundResult.PLAYER_WIN,
        (Move.PAPER, Move.ROCK): RoundResult.PLAYER_WIN,
        (Move.SCISSORS, Move.ROCK): RoundResult.CPU_WIN,
        (Move.PAPER, Move.SCISSORS): RoundResult.CPU_WIN,
        (Move.ROCK, Move.PAPER): RoundResult.CPU_WIN,
    }
    
    def __init__(self, rounds_to_win: int = 3):
        """
        Inizializza la logica del gioco.
        
        Args:
            rounds_to_win: Non più usato - mantenuto per compatibilità
        """
        self.rounds_to_win = rounds_to_win
        self.reset()
    
    def reset(self):
        """Resetta lo stato del gioco."""
        self.player_score = 0
        self.cpu_score = 0
        self.round_count = 0
        self.history = []  # Lista di (player_move, cpu_move, result)
    
    def get_cpu_move(self) -> Move:
        """
        Genera la mossa della CPU.
        
        Returns:
            Mossa casuale della CPU
        """
        return random.choice(list(Move))
    
    def determine_winner(self, player_move: Move, cpu_move: Move) -> RoundResult:
        """
        Determina il vincitore di un round.
        
        Args:
            player_move: Mossa del giocatore
            cpu_move: Mossa della CPU
            
        Returns:
            Risultato del round
        """
        if player_move == cpu_move:
            return RoundResult.DRAW
        
        return self.WIN_MATRIX.get((player_move, cpu_move), RoundResult.DRAW)
    
    def play_round(self, player_move: Move) -> Tuple[Move, RoundResult]:
        """
        Gioca un round completo.
        
        Args:
            player_move: Mossa del giocatore
            
        Returns:
            Tuple con (mossa_cpu, risultato)
        """
        cpu_move = self.get_cpu_move()
        result = self.determine_winner(player_move, cpu_move)
        
        # Aggiorna i punteggi
        if result == RoundResult.PLAYER_WIN:
            self.player_score += 1
        elif result == RoundResult.CPU_WIN:
            self.cpu_score += 1
        
        self.round_count += 1
        self.history.append((player_move, cpu_move, result))
        
        return cpu_move, result
    
    def is_game_over(self) -> bool:
        """
        Verifica se la partita è finita.
        In modalità sopravvivenza, il gioco finisce solo quando la CPU vince un round.
        """
        # Il gioco finisce quando la CPU vince (l'utente perde)
        return self.cpu_score >= 1
    
    def get_game_winner(self) -> Optional[str]:
        """
        Restituisce il vincitore della partita.
        In modalità sopravvivenza, se il gioco è finito, ha sempre vinto la CPU.
        
        Returns:
            'cpu' se il gioco è finito, None altrimenti
        """
        if self.cpu_score >= 1:
            return 'cpu'
        return None
    
    def get_score(self) -> Tuple[int, int]:
        """Restituisce il punteggio (giocatore, cpu)."""
        return self.player_score, self.cpu_score
    
    def get_win_streak(self) -> int:
        """
        Calcola la serie di vittorie consecutive del giocatore.
        
        Returns:
            Numero di vittorie consecutive
        """
        streak = 0
        for _, _, result in reversed(self.history):
            if result == RoundResult.PLAYER_WIN:
                streak += 1
            else:
                break
        return streak
    
    def get_stats(self) -> dict:
        """
        Calcola le statistiche della partita.
        
        Returns:
            Dizionario con le statistiche
        """
        if not self.history:
            return {
                'rounds_played': 0,
                'player_wins': 0,
                'cpu_wins': 0,
                'draws': 0,
                'win_rate': 0.0
            }
        
        player_wins = sum(1 for _, _, r in self.history if r == RoundResult.PLAYER_WIN)
        cpu_wins = sum(1 for _, _, r in self.history if r == RoundResult.CPU_WIN)
        draws = sum(1 for _, _, r in self.history if r == RoundResult.DRAW)
        
        return {
            'rounds_played': len(self.history),
            'player_wins': player_wins,
            'cpu_wins': cpu_wins,
            'draws': draws,
            'win_rate': player_wins / len(self.history) if self.history else 0.0
        }
