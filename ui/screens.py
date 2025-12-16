"""
Schermate del gioco
"""

import pygame
import math
from typing import Optional
import time

from game.game_state import GameState, StateManager
from game.game_logic import GameLogic, Move, RoundResult
from game.highscore import HighScoreManager
from ui.renderer import Renderer
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, ROUNDS_TO_WIN, COUNTDOWN_TIME


class ScreenManager:
    """
    Gestisce il rendering delle diverse schermate del gioco.
    """
    
    def __init__(self, 
                 renderer: Renderer,
                 state_manager: StateManager,
                 game_logic: GameLogic,
                 highscore_manager: HighScoreManager):
        """
        Inizializza il gestore delle schermate.
        
        Args:
            renderer: Renderer per il disegno
            state_manager: Gestore degli stati
            game_logic: Logica del gioco
            highscore_manager: Gestore dei punteggi
        """
        self.renderer = renderer
        self.state = state_manager
        self.game = game_logic
        self.highscore = highscore_manager
        
        # Per l'input del nome
        self.input_name = ""
        self.cursor_blink_time = 0
        
        # Animazioni
        self.animation_time = 0
    
    def update(self, dt: float):
        """Aggiorna le animazioni."""
        self.animation_time += dt
        self.cursor_blink_time += dt
    
    def render(self, 
               current_state: GameState,
               frame = None,
               detected_gesture: str = 'none',
               gesture_progress: float = 0.0):
        """
        Renderizza la schermata corrente.
        
        Args:
            current_state: Stato corrente del gioco
            frame: Frame della camera (opzionale)
            detected_gesture: Gesto attualmente rilevato
            gesture_progress: Progresso della conferma del gesto
        """
        self.renderer.clear()
        
        if current_state == GameState.MENU:
            self._render_menu(frame, detected_gesture)
        elif current_state == GameState.PLAYING:
            self._render_playing(frame, detected_gesture, gesture_progress)
        elif current_state == GameState.COUNTDOWN:
            self._render_countdown(frame)
        elif current_state == GameState.SHOWING_RESULT:
            self._render_result(frame)
        elif current_state == GameState.GAME_OVER:
            self._render_game_over(frame)
        elif current_state == GameState.HIGHSCORE:
            self._render_highscore(frame, detected_gesture)
        elif current_state == GameState.ENTER_NAME:
            self._render_enter_name(frame)
        elif current_state == GameState.SETTINGS:
            self._render_settings(frame, detected_gesture)
    
    def _render_menu(self, frame, gesture: str):
        """Renderizza il menu principale."""
        # Titolo
        y_offset = int(10 * math.sin(self.animation_time * 2))
        self.renderer.draw_text(
            "MORRA CINESE",
            (SCREEN_WIDTH // 2, 80 + y_offset),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        self.renderer.draw_text(
            "Portatile Interattiva",
            (SCREEN_WIDTH // 2, 130),
            'medium',
            COLORS['secondary'],
            center=True
        )
        
        # Feed camera (piccolo)
        if frame is not None:
            self.renderer.draw_camera_feed(
                frame,
                (SCREEN_WIDTH - 120, 80),
                (160, 120),
                COLORS['primary']
            )
        
        # Opzioni menu
        menu_items = [
            ('GIOCA', 'play'),
            ('CLASSIFICA', 'highscore'),
            ('IMPOSTAZIONI', 'settings'),
            ('ESCI', 'exit')
        ]
        
        start_y = 220
        for i, (label, key) in enumerate(menu_items):
            selected = i == self.state.menu_selection
            y = start_y + i * 70
            self.renderer.draw_button(
                label,
                (SCREEN_WIDTH // 2, y),
                (250, 55),
                selected
            )
        
        # Istruzioni
        self.renderer.draw_text(
            "👆 Su/Giù per navigare | 👌 OK per selezionare",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
            'small',
            COLORS['gray'],
            center=True
        )
        
        # Indicatore gesto
        self.renderer.draw_gesture_indicator(
            gesture, 1.0, 
            (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 80)
        )
    
    def _render_playing(self, frame, gesture: str, progress: float):
        """Renderizza la schermata di gioco."""
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score(
            player_score, cpu_score,
            (SCREEN_WIDTH // 2, 40)
        )
        
        # Feed camera (grande)
        if frame is not None:
            self.renderer.draw_camera_feed(
                frame,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                (400, 300),
                COLORS['primary']
            )
        
        # Istruzioni
        self.renderer.draw_text(
            "Fai il tuo gesto e mantienilo!",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120),
            'medium',
            COLORS['white'],
            center=True
        )
        
        # Indicatore gesto attuale
        self.renderer.draw_gesture_indicator(
            gesture, 1.0,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        )
        
        # Barra di progresso per conferma gesto
        if gesture in ['rock', 'paper', 'scissors'] and progress > 0:
            self.renderer.draw_progress_bar(
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40),
                (300, 20),
                progress,
                COLORS['success']
            )
    
    def _render_countdown(self, frame):
        """Renderizza il countdown."""
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score(
            player_score, cpu_score,
            (SCREEN_WIDTH // 2, 40)
        )
        
        # Feed camera (sfondo)
        if frame is not None:
            self.renderer.draw_camera_feed(
                frame,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                (400, 300),
                COLORS['secondary']
            )
        
        # Numero countdown
        remaining = self.state.get_remaining_time()
        number = max(1, int(remaining) + 1)
        
        self.renderer.draw_countdown(
            number,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        
        # Mossa del giocatore
        player_move = self.state.get_data('player_move')
        if player_move:
            self.renderer.draw_text(
                f"La tua mossa: {Move[player_move.upper()].get_italian_name()}",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80),
                'medium',
                COLORS['white'],
                center=True
            )
    
    def _render_result(self, frame):
        """Renderizza il risultato del round."""
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score(
            player_score, cpu_score,
            (SCREEN_WIDTH // 2, 40)
        )
        
        # Risultato
        result = self.state.get_data('result')
        player_move = self.state.get_data('player_move')
        cpu_move = self.state.get_data('cpu_move')
        
        # Mosse affiancate
        self.renderer.draw_move_icon(
            player_move,
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 50),
            120
        )
        self.renderer.draw_text(
            "TU",
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 40),
            'medium',
            COLORS['white'],
            center=True
        )
        
        # VS
        self.renderer.draw_text(
            "VS",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50),
            'large',
            COLORS['secondary'],
            center=True
        )
        
        self.renderer.draw_move_icon(
            cpu_move,
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 50),
            120
        )
        self.renderer.draw_text(
            "CPU",
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 40),
            'medium',
            COLORS['white'],
            center=True
        )
        
        # Banner risultato
        if result:
            self.renderer.draw_result_banner(
                result, player_move, cpu_move,
                SCREEN_HEIGHT - 100
            )
    
    def _render_game_over(self, frame):
        """Renderizza la schermata di fine partita."""
        winner = self.game.get_game_winner()
        player_score, cpu_score = self.game.get_score()
        
        # Sfondo colorato
        if winner == 'player':
            bg_color = COLORS['success']
            title = "VITTORIA!"
            subtitle = "Complimenti, hai vinto la partita!"
        else:
            bg_color = COLORS['danger']
            title = "SCONFITTA"
            subtitle = "La CPU ha vinto questa volta..."
        
        # Overlay semi-trasparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(bg_color)
        overlay.set_alpha(50)
        self.renderer.screen.blit(overlay, (0, 0))
        
        # Titolo
        self.renderer.draw_text(
            title,
            (SCREEN_WIDTH // 2, 100),
            'title',
            COLORS['white'],
            center=True,
            shadow=True
        )
        
        self.renderer.draw_text(
            subtitle,
            (SCREEN_WIDTH // 2, 160),
            'medium',
            COLORS['white'],
            center=True
        )
        
        # Punteggio finale
        self.renderer.draw_text(
            f"Punteggio finale: {player_score} - {cpu_score}",
            (SCREEN_WIDTH // 2, 220),
            'large',
            COLORS['secondary'],
            center=True
        )
        
        # Statistiche
        stats = self.game.get_stats()
        stats_y = 300
        self.renderer.draw_text(
            f"Round giocati: {stats['rounds_played']}",
            (SCREEN_WIDTH // 2, stats_y),
            'small',
            COLORS['white'],
            center=True
        )
        self.renderer.draw_text(
            f"Vittorie: {stats['player_wins']} | Sconfitte: {stats['cpu_wins']} | Pareggi: {stats['draws']}",
            (SCREEN_WIDTH // 2, stats_y + 35),
            'small',
            COLORS['gray'],
            center=True
        )
        
        # Istruzioni
        self.renderer.draw_text(
            "👌 OK per continuare",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80),
            'medium',
            COLORS['white'],
            center=True
        )
    
    def _render_highscore(self, frame, gesture: str):
        """Renderizza la classifica."""
        self.renderer.draw_text(
            "CLASSIFICA",
            (SCREEN_WIDTH // 2, 60),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        
        # Tabella punteggi
        scores = self.highscore.get_scores(10)
        if scores:
            self.renderer.draw_highscore_table(
                scores,
                (SCREEN_WIDTH // 2 - 150, 130)
            )
        else:
            self.renderer.draw_text(
                "Nessun punteggio registrato",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                'medium',
                COLORS['gray'],
                center=True
            )
        
        # Istruzioni
        self.renderer.draw_text(
            "👌 OK per tornare al menu",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
            'small',
            COLORS['gray'],
            center=True
        )
    
    def _render_enter_name(self, frame):
        """Renderizza l'input del nome."""
        self.renderer.draw_text(
            "NUOVO RECORD!",
            (SCREEN_WIDTH // 2, 80),
            'title',
            COLORS['success'],
            center=True,
            shadow=True
        )
        
        self.renderer.draw_text(
            "Inserisci il tuo nome (3 lettere)",
            (SCREEN_WIDTH // 2, 150),
            'medium',
            COLORS['white'],
            center=True
        )
        
        # Campo input
        cursor_visible = int(self.cursor_blink_time * 2) % 2 == 0
        self.renderer.draw_name_input(
            self.input_name,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            cursor_visible
        )
        
        # Tastiera virtuale con lettere
        self.renderer.draw_text(
            "Usa la tastiera per inserire le lettere",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100),
            'small',
            COLORS['gray'],
            center=True
        )
        
        self.renderer.draw_text(
            "Premi INVIO per confermare | BACKSPACE per cancellare",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
            'small',
            COLORS['gray'],
            center=True
        )
    
    def _render_settings(self, frame, gesture: str):
        """Renderizza le impostazioni."""
        self.renderer.draw_text(
            "IMPOSTAZIONI",
            (SCREEN_WIDTH // 2, 60),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        
        # Opzioni (placeholder)
        settings_text = [
            "• Audio: Attivo",
            "• Camera: Attiva",
            "• Round per vincere: 3",
            "• Difficoltà: Normale"
        ]
        
        y = 160
        for text in settings_text:
            self.renderer.draw_text(
                text,
                (SCREEN_WIDTH // 2, y),
                'medium',
                COLORS['white'],
                center=True
            )
            y += 50
        
        # Istruzioni
        self.renderer.draw_text(
            "👌 OK per tornare al menu",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
            'small',
            COLORS['gray'],
            center=True
        )
    
    def handle_name_input(self, event: pygame.event) -> Optional[str]:
        """
        Gestisce l'input del nome.
        
        Args:
            event: Evento Pygame
            
        Returns:
            Nome completo se confermato, None altrimenti
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.input_name) == 3:
                name = self.input_name
                self.input_name = ""
                return name
            elif event.key == pygame.K_BACKSPACE:
                self.input_name = self.input_name[:-1]
            elif len(self.input_name) < 3 and event.unicode.isalpha():
                self.input_name += event.unicode.upper()
        
        return None
    
    def reset_name_input(self):
        """Resetta l'input del nome."""
        self.input_name = ""
        self.cursor_blink_time = 0
