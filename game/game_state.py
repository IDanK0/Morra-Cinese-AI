"""
Gestione degli stati del gioco
"""

from enum import Enum, auto
from typing import Optional, Callable, Dict, Any
import time


class GameState(Enum):
    """Stati possibili del gioco."""
    MENU = auto()           # Menu principale
    MODE_SELECT = auto()    # Selezione modalità di gioco
    PLAYING = auto()        # In gioco - attesa gesto
    COUNTDOWN = auto()      # Countdown prima della mossa
    TIMED_CPU_MOVE = auto() # Variante Riflessi - CPU sta scegliendo
    TIMED_PLAYER_TURN = auto() # Variante Riflessi - turno del giocatore
    SHOWING_RESULT = auto() # Mostra risultato round
    GAME_OVER = auto()      # Fine partita
    HIGHSCORE = auto()      # Schermata classifica
    ENTER_NAME = auto()     # Inserimento nome per classifica
    SETTINGS = auto()       # Impostazioni
    PAUSED = auto()         # Gioco in pausa
    CAMERA_ERROR = auto()   # Errore camera (disconnessa)


class StateManager:
    """
    Gestisce le transizioni tra gli stati del gioco.
    """
    
    def __init__(self):
        """Inizializza il gestore degli stati."""
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_data: Dict[str, Any] = {}
        
        # Callbacks per l'ingresso in ogni stato
        self.on_enter_callbacks: Dict[GameState, Callable] = {}
        self.on_exit_callbacks: Dict[GameState, Callable] = {}
        
        # Timer per stati temporizzati
        self.state_start_time = time.time()
        self.state_duration = 0
        
        # Menu state
        self.menu_selection = 0
        self.menu_items = ['play', 'highscore', 'settings', 'exit']
    
    def change_state(self, new_state: GameState, **kwargs):
        """
        Cambia lo stato corrente.
        
        Args:
            new_state: Nuovo stato
            **kwargs: Dati aggiuntivi per lo stato
        """
        # Esegui callback di uscita
        if self.current_state in self.on_exit_callbacks:
            self.on_exit_callbacks[self.current_state]()
        
        # Salva lo stato precedente
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Aggiorna i dati dello stato
        self.state_data = kwargs
        self.state_start_time = time.time()
        self.state_duration = kwargs.get('duration', 0)
        
        # Esegui callback di ingresso
        if new_state in self.on_enter_callbacks:
            self.on_enter_callbacks[new_state]()
    
    def go_back(self):
        """Torna allo stato precedente."""
        if self.previous_state:
            self.change_state(self.previous_state)
    
    def register_enter_callback(self, state: GameState, callback: Callable):
        """Registra una callback per l'ingresso in uno stato."""
        self.on_enter_callbacks[state] = callback
    
    def register_exit_callback(self, state: GameState, callback: Callable):
        """Registra una callback per l'uscita da uno stato."""
        self.on_exit_callbacks[state] = callback
    
    def get_state_time(self) -> float:
        """Restituisce il tempo trascorso nello stato corrente."""
        return time.time() - self.state_start_time
    
    def is_state_timed_out(self) -> bool:
        """Verifica se lo stato temporizzato e' scaduto."""
        if self.state_duration <= 0:
            return False
        return self.get_state_time() >= self.state_duration
    
    def get_remaining_time(self) -> float:
        """Restituisce il tempo rimanente per stati temporizzati."""
        if self.state_duration <= 0:
            return 0
        remaining = self.state_duration - self.get_state_time()
        return max(0, remaining)
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Recupera un dato dallo stato corrente."""
        return self.state_data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """Imposta un dato nello stato corrente."""
        self.state_data[key] = value
    
    # Menu navigation
    def menu_up(self):
        """Naviga su nel menu."""
        self.menu_selection = (self.menu_selection - 1) % len(self.menu_items)
    
    def menu_down(self):
        """Naviga giu' nel menu."""
        self.menu_selection = (self.menu_selection + 1) % len(self.menu_items)
    
    def get_selected_menu_item(self) -> str:
        """Restituisce l'elemento del menu selezionato."""
        return self.menu_items[self.menu_selection]
    
    def is_in_game(self) -> bool:
        """Verifica se siamo in una fase di gioco attivo."""
        return self.current_state in [
            GameState.PLAYING, 
            GameState.COUNTDOWN, 
            GameState.SHOWING_RESULT
        ]
