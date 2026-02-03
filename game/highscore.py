"""
Sistema di gestione della classifica (High Score)
"""

import json
import os
from typing import List, Tuple, Optional
from datetime import datetime


class HighScoreManager:
    """
    Gestisce il salvataggio e caricamento dei punteggi.
    """
    
    def __init__(self, filename: str = 'highscores.json', max_entries: int = 10):
        """
        Inizializza il gestore dei punteggi.
        
        Args:
            filename: Nome del file per salvare i punteggi
            max_entries: Numero massimo di voci nella classifica
        """
        self.filename = filename
        self.max_entries = max_entries
        self.scores: List[dict] = []
        self.load()
    
    def load(self) -> bool:
        """
        Carica i punteggi dal file.
        
        Returns:
            True se il caricamento e' riuscito
        """
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.scores = data.get('scores', [])
                return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Errore caricamento classifica: {e}")
        
        self.scores = []
        return False
    
    def save(self) -> bool:
        """
        Salva i punteggi su file.
        
        Returns:
            True se il salvataggio e' riuscito
        """
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump({'scores': self.scores}, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Errore salvataggio classifica: {e}")
            return False
    
    def add_score(self, name: str, score: int, stats: Optional[dict] = None, game_mode: str = 'classic', difficulty: str = None) -> int:
        """
        Aggiunge un nuovo punteggio alla classifica.
        
        Args:
            name: Nome del giocatore (max 5 caratteri)
            score: Punteggio ottenuto
            stats: Statistiche aggiuntive opzionali
            game_mode: Modalità di gioco ('classic' o 'timed')
            difficulty: Difficoltà per modalità timed ('easy', 'medium', 'hard')
            
        Returns:
            Posizione in classifica (1-indexed) o -1 se non in classifica
        """
        # Limita il nome a 5 caratteri
        name = name.upper()[:5]
        
        entry = {
            'name': name,
            'score': score,
            'date': datetime.now().isoformat(),
            'stats': stats or {},
            'mode': game_mode,
            'difficulty': difficulty
        }
        
        # Inserisci in ordine decrescente
        position = 0
        for i, existing in enumerate(self.scores):
            if score > existing['score']:
                position = i
                break
            position = i + 1
        
        if position < self.max_entries:
            self.scores.insert(position, entry)
            # Limita a max_entries
            self.scores = self.scores[:self.max_entries]
            self.save()
            return position + 1  # 1-indexed
        
        return -1
    
    def get_scores(self, limit: Optional[int] = None, mode: Optional[str] = None, difficulty: Optional[str] = None) -> List[dict]:
        """
        Restituisce la lista dei punteggi filtrati per modalità e difficoltà.
        
        Args:
            limit: Numero massimo di voci da restituire
            mode: Filtra per modalità ('classic' o 'timed'), None per tutte
            difficulty: Filtra per difficoltà ('easy', 'medium', 'hard'), None per tutte
            
        Returns:
            Lista di dizionari con i punteggi
        """
        filtered_scores = self.scores
        
        # Filtra per modalità
        if mode:
            filtered_scores = [s for s in filtered_scores if s.get('mode', 'classic') == mode]
        
        # Filtra per difficoltà (solo se specificata)
        if difficulty:
            filtered_scores = [s for s in filtered_scores if s.get('difficulty') == difficulty]
        
        if limit:
            return filtered_scores[:limit]
        return filtered_scores
    
    def get_scores_by_mode(self) -> dict:
        """
        Restituisce i punteggi raggruppati per modalità.
        
        Returns:
            Dizionario con chiavi 'classic' e 'timed' (suddiviso per difficoltà)
        """
        result = {
            'classic': [],
            'timed': {
                'easy': [],
                'medium': [],
                'hard': [],
                'all': []
            }
        }
        
        for score in self.scores:
            mode = score.get('mode', 'classic')
            difficulty = score.get('difficulty')
            
            if mode == 'classic':
                result['classic'].append(score)
            elif mode == 'timed':
                result['timed']['all'].append(score)
                if difficulty:
                    result['timed'][difficulty].append(score)
        
        return result
    
    def get_top_scores(self, count: int = 5) -> List[Tuple[str, int]]:
        """
        Restituisce i migliori punteggi come tuple (nome, punteggio).
        
        Args:
            count: Numero di punteggi da restituire
            
        Returns:
            Lista di tuple (nome, punteggio)
        """
        return [(s['name'], s['score']) for s in self.scores[:count]]
    
    def is_high_score(self, score: int) -> bool:
        """
        Verifica se un punteggio entra in classifica.
        
        Args:
            score: Punteggio da verificare
            
        Returns:
            True se il punteggio e' abbastanza alto per la classifica
        """
        if len(self.scores) < self.max_entries:
            return True
        return score > self.scores[-1]['score']
    
    def get_rank(self, score: int) -> int:
        """
        Calcola la posizione che avrebbe un punteggio in classifica.
        
        Args:
            score: Punteggio da verificare
            
        Returns:
            Posizione (1-indexed) o -1 se non entrerebbe
        """
        for i, existing in enumerate(self.scores):
            if score > existing['score']:
                return i + 1
        
        if len(self.scores) < self.max_entries:
            return len(self.scores) + 1
        
        return -1
    
    def clear(self):
        """Cancella tutti i punteggi."""
        self.scores = []
        self.save()
    
    def get_stats(self) -> dict:
        """
        Calcola statistiche globali dalla classifica.
        
        Returns:
            Dizionario con statistiche
        """
        if not self.scores:
            return {
                'total_games': 0,
                'highest_score': 0,
                'average_score': 0,
                'unique_players': 0
            }
        
        return {
            'total_games': len(self.scores),
            'highest_score': self.scores[0]['score'] if self.scores else 0,
            'average_score': sum(s['score'] for s in self.scores) / len(self.scores),
            'unique_players': len(set(s['name'] for s in self.scores))
        }
