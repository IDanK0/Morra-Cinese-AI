"""
Schermate del gioco - Design Moderno Gaming
============================================
Interfaccia utente riprogettata con stile professionale e carino.
"""

try:
    import pygame  # type: ignore[import]
    if not hasattr(pygame, 'Surface') or not hasattr(pygame, 'display'):
        raise ImportError("pygame non ha gli attributi richiesti (Surface, display)")
except ImportError as e:
    print(f"❌ ERRORE: pygame non è disponibile!")
    print(f"   {"Motivo: " + str(e) if str(e) else ""}")
    print(f"   Soluzione: python -m pip install pygame")
    import sys
    sys.exit(1)

import math
import random
from typing import Optional, Any
import time

from game.game_state import GameState, StateManager
from game.game_logic import GameLogic, Move, RoundResult
from game.highscore import HighScoreManager
from ui.renderer import Renderer
from config import (
    COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, ROUNDS_TO_WIN, COUNTDOWN_TIME, 
    GAME_SETTINGS, GameMode, TimedDifficulty, DIFFICULTY_NAMES, 
    CPU_MOVE_TIMER, PLAYER_RESPONSE_TIMES, UI_SYMBOLS
)


class ScreenManager:
    """
    Gestisce il rendering delle diverse schermate del gioco.
    Design moderno con animazioni fluide e stile gaming.
    """
    
    def __init__(self, 
                 renderer: Renderer,
                 state_manager: StateManager,
                 game_logic: GameLogic,
                 highscore_manager: HighScoreManager):
        """
        Inizializza il gestore delle schermate.
        """
        self.renderer = renderer
        self.state = state_manager
        self.game = game_logic
        self.highscore = highscore_manager
        
        # Input nome
        self.input_name = ""
        self.cursor_blink_time = 0
        self._name_input_particles = False
        
        # Filtro highscore
        self.highscore_filter = 'all'
        
        # Animazioni
        self.animation_time = 0
        
        # Selezione menu
        self.mode_selection = 0
        self.difficulty_selection = 1
        
        self.mode_options = [
            {'key': 'classic', 'label': 'Tradizionale', 'icon': '🎮', 'description': 'Gioca senza limiti di tempo'},
            {'key': 'timed', 'label': 'Variante Riflessi', 'icon': '⚡', 'description': 'Rispondi prima che scada il timer'},
        ]
        
        self.difficulty_options = [
            {'key': TimedDifficulty.EASY, 'label': 'Facile', 'time': '6s', 'color': COLORS['success']},
            {'key': TimedDifficulty.MEDIUM, 'label': 'Media', 'time': '4s', 'color': COLORS['warning']},
            {'key': TimedDifficulty.HARD, 'label': 'Difficile', 'time': '2s', 'color': COLORS['danger']},
        ]
        
        # Settings
        self.settings_selection = 0
        self.settings_options = [
            {'key': 'camera_index', 'label': 'Camera', 'values': 'dynamic', 'unit': ''},
            {'key': 'refresh_cameras', 'label': 'Aggiorna Camera', 'values': ['action'], 'unit': ''},
            {'key': 'gesture_hold_time', 'label': 'Tempo Conferma', 'values': [0.5, 0.75, 1.0, 1.25, 1.5], 'unit': 's'},
            {'key': 'countdown_time', 'label': 'Countdown', 'values': [2, 3, 4, 5], 'unit': 's'},
            {'key': 'camera_flip', 'label': 'Specchia Camera', 'values': [True, False], 'unit': ''},
            {'key': 'show_fps', 'label': 'Mostra FPS', 'values': [True, False], 'unit': ''},
            {'key': 'fullscreen', 'label': 'Schermo intero', 'values': [True, False], 'unit': ''},
            {'key': 'reset_scores', 'label': 'Cancella Classifica', 'values': ['action'], 'unit': ''},
            {'key': 'back', 'label': 'Torna al Menu', 'values': ['action'], 'unit': ''},
        ]
        
        # Camera refresh
        self._cameras_refreshed = False
        self._cameras_refresh_time = 0
        
        # Camera error
        self.camera_error_selection = 0
        self.available_cameras = []
    
    def update(self, dt: float):
        """Aggiorna le animazioni."""
        self.animation_time += dt
        self.cursor_blink_time += dt
        self.renderer.update_particles(dt)
        self.renderer.apply_screen_overlay(dt)
    
    def _draw_no_camera_indicator(self, position: tuple, size: tuple):
        """Disegna indicatore camera non connessa."""
        x, y = position
        w, h = size
        rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
        
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], rect, border_radius=12)
        
        pulse = 0.5 + 0.5 * math.sin(self.animation_time * 3)
        border_color = tuple(int(c * (0.5 + 0.5 * pulse)) for c in COLORS['warning'])
        pygame.draw.rect(self.renderer.screen, border_color, rect, width=2, border_radius=12)
        
        self.renderer.draw_text("CAM", (x, y - 15), 'large', COLORS['muted'], center=True)
        
        dots = "." * (int(self.animation_time * 2) % 4)
        self.renderer.draw_text(f"Ricerca{dots}", (x, y + 25), 'tiny', COLORS['warning'], center=True)
    
    def render(self, 
               current_state: GameState,
               frame = None,
               detected_gesture: str = 'none',
               gesture_progress: float = 0.0):
        """Renderizza la schermata corrente."""
        self.renderer.clear()
        
        if current_state == GameState.MENU:
            self._render_menu(frame, detected_gesture)
        elif current_state == GameState.MODE_SELECT:
            self._render_mode_select(frame, detected_gesture)
        elif current_state == GameState.PLAYING:
            self._render_playing(frame, detected_gesture, gesture_progress)
        elif current_state == GameState.COUNTDOWN:
            self._render_countdown(frame)
        elif current_state == GameState.TIMED_CPU_MOVE:
            self._render_timed_cpu_move(frame)
        elif current_state == GameState.TIMED_PLAYER_TURN:
            self._render_timed_player_turn(frame, detected_gesture, gesture_progress)
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
        elif current_state == GameState.CAMERA_ERROR:
            self._render_camera_error()
        
        self.renderer.draw_particles()
        self.renderer.apply_screen_overlay(0)
    
    # =========================================================================
    # MENU PRINCIPALE
    # =========================================================================
    
    def _render_menu(self, frame, gesture: str):
        """Renderizza il menu principale."""
        # Titolo con animazione
        y_offset = int(8 * math.sin(self.animation_time * 1.5))
        
        # Logo/Titolo principale
        self.renderer.draw_text(
            "MORRA CINESE",
            (SCREEN_WIDTH // 2, 80 + y_offset),
            'hero',
            COLORS['primary'],
            center=True,
            shadow=True,
            glow=True,
            glow_color=COLORS['primary_light']
        )
        
        # Sottotitolo
        self.renderer.draw_text(
            "Portatile Interattiva",
            (SCREEN_WIDTH // 2, 140),
            'medium',
            COLORS['secondary'],
            center=True
        )
        
        # Decorazioni laterali animate
        self._draw_menu_decorations()
        
        # Feed camera (spostato in basso a sinistra)
        cam_pos_menu = (80, SCREEN_HEIGHT - 120)
        cam_size_menu = (140, 105)
        if frame is not None:
            self.renderer.draw_camera_feed(frame, cam_pos_menu, cam_size_menu, COLORS['primary'])
        else:
            self._draw_no_camera_indicator(cam_pos_menu, cam_size_menu)
        
        # Menu items
        menu_items = [
            ('🎮 GIOCA', 'play', COLORS['success']),
            ('🏆 CLASSIFICA', 'trophy', COLORS['warning']),
            ('⚙️ IMPOSTAZIONI', 'settings', COLORS['accent']),
            ('🚪 ESCI', 'exit', COLORS['danger'])
        ]
        
        start_y = 220
        for i, (label, key, accent_color) in enumerate(menu_items):
            selected = i == self.state.menu_selection
            y = start_y + i * 70
            
            self.renderer.draw_modern_button(
                label,
                (SCREEN_WIDTH // 2, y),
                (280, 55),
                selected,
                accent_color if selected else None
            )
        
        # Istruzioni
        self.renderer.draw_text(
            "↑↓ Naviga  •  INVIO Seleziona",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50),
            'small',
            COLORS['muted'],
            center=True
        )
        
        # Indicatore gesto
        self.renderer.draw_gesture_indicator(gesture, 1.0, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 85))
    
    def _draw_menu_decorations(self):
        """Disegna decorazioni animate per il menu."""
        # Cerchi pulsanti decorativi
        pulse = self.animation_time
        
        # Sinistra
        self.renderer.draw_pulse_circle(
            (60, 80),
            25, COLORS['primary'], pulse
        )
        self.renderer.draw_pulse_circle(
            (100, 120),
            15, COLORS['secondary'], pulse + 0.5
        )
        
        # Destra (sotto camera)
        self.renderer.draw_pulse_circle(
            (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 100),
            20, COLORS['accent'], pulse + 1.0
        )
    
    # =========================================================================
    # SELEZIONE MODALITA'
    # =========================================================================
    
    def _render_mode_select(self, frame, gesture: str):
        """Renderizza la selezione modalità."""
        # Titolo
        y_offset = int(5 * math.sin(self.animation_time * 2))
        self.renderer.draw_text(
            "SELEZIONA MODALITA'",
            (SCREEN_WIDTH // 2, 55 + y_offset),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        
        # Camera (basso a sinistra)
        cam_pos_mode = (80, SCREEN_HEIGHT - 120)
        cam_size_mode = (140, 105)
        if frame is not None:
            self.renderer.draw_camera_feed(frame, cam_pos_mode, cam_size_mode, COLORS['primary'])
        else:
            self._draw_no_camera_indicator(cam_pos_mode, cam_size_mode)
        
        # Cards modalità (allargati)
        card_width = 500
        card_height = 120
        start_y = 140
        
        for i, option in enumerate(self.mode_options):
            selected = i == self.mode_selection
            y = start_y + i * (card_height + 20)
            
            # Card
            card_rect = self.renderer.draw_card(
                (SCREEN_WIDTH // 2, y),
                (card_width, card_height),
                selected,
                COLORS['primary'] if selected else None
            )
            
            # Icona
            icon_x = card_rect.left + 50
            self.renderer.draw_text(option['icon'], (icon_x, y), 'title', 
                                   COLORS['secondary'] if selected else COLORS['muted'], center=True)
            
            # Testo
            text_x = SCREEN_WIDTH // 2 + 20
            self.renderer.draw_text(option['label'], (text_x, y - 12), 
                                   'large' if selected else 'medium',
                                   COLORS['white'] if selected else COLORS['gray'], center=True)
            self.renderer.draw_text(option['description'], (text_x, y + 18), 
                                   'small', COLORS['muted'], center=True)
        
        # Difficoltà (se modalità Variante Riflessi)
        if self.mode_selection == 1:
            self._draw_difficulty_selector(start_y + 2 * (card_height + 20) - 30)
        
        # Pulsante indietro
        back_y = SCREEN_HEIGHT - 90
        back_selected = False
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], 
                pygame.Rect(SCREEN_WIDTH // 2 - 100, back_y - 18, 200, 36), border_radius=10)
        self.renderer.draw_text("<- INDIETRO (ESC)", (SCREEN_WIDTH // 2, back_y), 
                       'small', COLORS['muted'], center=True)
        
        # Istruzioni
        self.renderer.draw_text(
            "SU/GIU Modalità  •  <- -> Difficoltà  •  INVIO Conferma",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40),
            'tiny',
            COLORS['muted'],
            center=True
        )
        
        self.renderer.draw_gesture_indicator(gesture, 1.0, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 85))
    
    def _draw_difficulty_selector(self, y: int):
        """Disegna il selettore difficoltà."""
        self.renderer.draw_text("Difficoltà:", (SCREEN_WIDTH // 2, y), 'small', COLORS['secondary'], center=True)
        
        # Box difficoltà
        box_width = 100
        total_width = len(self.difficulty_options) * (box_width + 15) - 15
        start_x = SCREEN_WIDTH // 2 - total_width // 2 + box_width // 2
        box_y = y + 45
        
        for i, diff in enumerate(self.difficulty_options):
            selected = i == self.difficulty_selection
            x = start_x + i * (box_width + 15)
            
            # Box
            box_rect = pygame.Rect(x - box_width // 2, box_y - 30, box_width, 60)
            
            if selected:
                # Glow
                glow_surf = pygame.Surface((box_width + 10, 70), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*diff['color'], 60), glow_surf.get_rect(), border_radius=12)
                self.renderer.screen.blit(glow_surf, (box_rect.left - 5, box_rect.top - 5))
                
                pygame.draw.rect(self.renderer.screen, diff['color'], box_rect, border_radius=10)
            else:
                pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], box_rect, border_radius=10)
                pygame.draw.rect(self.renderer.screen, COLORS['muted'], box_rect, width=1, border_radius=10)
            
            # Testo
            text_color = COLORS['white'] if selected else COLORS['gray']
            self.renderer.draw_text(diff['label'], (x, box_y - 8), 'small', text_color, center=True)
            self.renderer.draw_text(diff['time'], (x, box_y + 15), 'tiny', 
                                   diff['color'] if selected else COLORS['muted'], center=True)
    
    # =========================================================================
    # GIOCO CLASSICO
    # =========================================================================
    
    def _render_playing(self, frame, gesture: str, progress: float):
        """Renderizza la schermata di gioco."""
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score_panel(player_score, cpu_score, (SCREEN_WIDTH // 2, 45))
        
        # Feed camera (spostato in basso a sinistra all'inizio del gioco)
        if frame is not None:
            border_color = COLORS['success'] if gesture in ['rock', 'paper', 'scissors'] else COLORS['primary']
            # Posizione bottom-left con dimensione ridotta per non occupare il centro
            cam_pos = (80, SCREEN_HEIGHT - 120)
            cam_size = (320, 240)
            self.renderer.draw_camera_feed(frame, cam_pos, cam_size, border_color)
        
        # Istruzioni
        if gesture in ['rock', 'paper', 'scissors']:
            instruction = "Mantieni il gesto..."
            color = COLORS['success']
        else:
            instruction = "Mostra Sasso, Carta o Forbice!"
            color = COLORS['white']
        
        self.renderer.draw_text(instruction, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 110), 
                               'medium', color, center=True)
        
        # Indicatore gesto
        self.renderer.draw_gesture_indicator(gesture, 1.0, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 85))
        
        # Barra progresso
        if gesture in ['rock', 'paper', 'scissors'] and progress > 0:
            bar_color = COLORS['success'] if progress > 0.6 else COLORS['secondary']
            self.renderer.draw_progress_bar(
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35),
                (350, 18),
                progress,
                bar_color
            )
    
    def _render_countdown(self, frame):
        """Renderizza il countdown."""
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score_panel(player_score, cpu_score, (SCREEN_WIDTH // 2, 45))
        
        # Camera sfondo
        if frame is not None:
            self.renderer.draw_camera_feed(frame, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
                                          (380, 285), COLORS['secondary'])
        
        # Countdown
        remaining = self.state.get_remaining_time()
        number = max(1, int(remaining) + 1)
        self.renderer.draw_countdown(number, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        # Mossa scelta
        player_move = self.state.get_data('player_move')
        if player_move:
            move_names = {'rock': 'Sasso', 'paper': 'Carta', 'scissors': 'Forbice'}
            self.renderer.draw_text(
                f"Tua mossa: {move_names.get(player_move, '?')}",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
                'medium', COLORS['white'], center=True
            )
    
    # =========================================================================
    # MODALITA' VARIANTE RIFLESSI
    # =========================================================================
    
    def _render_timed_cpu_move(self, frame):
        """Renderizza quando la CPU sceglie."""
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score_panel(player_score, cpu_score, (SCREEN_WIDTH // 2, 45))
        
        # Titolo
        self.renderer.draw_text("VARIANTE RIFLESSI", (SCREEN_WIDTH // 2, 90), 
                               'medium', COLORS['secondary'], center=True)
        
        # CPU pensa
        remaining = self.state.get_remaining_time()
        dots = "." * (int(self.animation_time * 3) % 4)
        
        # Box centrale
        box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 80, 360, 160)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], box_rect, border_radius=20)
        pygame.draw.rect(self.renderer.screen, COLORS['accent'], box_rect, width=2, border_radius=20)
        
        self.renderer.draw_text(f"La CPU sta scegliendo{dots}", 
                               (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40), 
                               'medium', COLORS['primary'], center=True)
        
        # Timer grande
        self.renderer.draw_text(f"{remaining:.1f}", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20), 
                               'hero', COLORS['secondary'], center=True, shadow=True)
        
        # Barra progresso
        progress = remaining / CPU_MOVE_TIMER
        self.renderer.draw_timer_bar((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80), (320, 20), progress)
        
        # Istruzioni
        self.renderer.draw_text("Preparati a rispondere!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), 
                               'medium', COLORS['white'], center=True)
        
        diff_name = DIFFICULTY_NAMES.get(GAME_SETTINGS.timed_difficulty, 'Media')
        response_time = GAME_SETTINGS.get_player_response_time()
        self.renderer.draw_text(f"Difficoltà: {diff_name} • {response_time:.0f}s per rispondere", 
                               (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30), 
                               'tiny', COLORS['muted'], center=True)
    
    def _render_timed_player_turn(self, frame, gesture: str, progress: float):
        """Renderizza il turno del giocatore (modalità Variante Riflessi)."""
        remaining = self.state.get_remaining_time()
        response_time = GAME_SETTINGS.get_player_response_time()
        time_ratio = remaining / response_time
        
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score_panel(player_score, cpu_score, (SCREEN_WIDTH // 2, 45))
        
        # Titolo urgenza
        if time_ratio < 0.3:
            title_color = COLORS['danger']
            flash = int(self.animation_time * 6) % 2
            if flash:
                self.renderer.draw_text("SBRIGATI!", (SCREEN_WIDTH // 2, 85), 
                                       'large', COLORS['danger'], center=True, glow=True)
        else:
            title_color = COLORS['secondary']
        
        self.renderer.draw_text("FAI LA TUA MOSSA!", (SCREEN_WIDTH // 2, 85), 
                               'large', title_color, center=True)
        
        # Box mossa CPU (sinistra)
        cpu_move = self.state.get_data('cpu_move')
        cpu_box = pygame.Rect(25, 115, 150, 170)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], cpu_box, border_radius=15)
        pygame.draw.rect(self.renderer.screen, COLORS['danger'], cpu_box, width=2, border_radius=15)
        
        self.renderer.draw_text("CPU:", (100, 130), 'small', COLORS['danger'], center=True)
        self.renderer.draw_move_icon(cpu_move, (100, 200), 70, background=False)
        
        move_names = {'rock': 'SASSO', 'paper': 'CARTA', 'scissors': 'FORBICE'}
        self.renderer.draw_text(move_names.get(cpu_move, '?'), (100, 260), 
                               'small', COLORS['danger'], center=True)
        
        # Camera centrale
        if frame is not None:
            border_color = COLORS['danger'] if time_ratio < 0.3 else COLORS['primary']
            self.renderer.draw_camera_feed(frame, (SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT // 2 + 10), 
                                          (320, 240), border_color)
        
        # Timer (destra)
        timer_color = COLORS['danger'] if time_ratio < 0.3 else COLORS['success']
        timer_box = pygame.Rect(SCREEN_WIDTH - 120, 115, 95, 100)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], timer_box, border_radius=12)
        pygame.draw.rect(self.renderer.screen, timer_color, timer_box, width=2, border_radius=12)
        
        self.renderer.draw_text(f"{remaining:.1f}", (SCREEN_WIDTH - 72, 155), 
                               'title', timer_color, center=True)
        self.renderer.draw_text("sec", (SCREEN_WIDTH - 72, 195), 'tiny', timer_color, center=True)
        
        # Barra tempo
        self.renderer.draw_timer_bar((SCREEN_WIDTH // 2 + 30, SCREEN_HEIGHT - 100), (320, 22), time_ratio)
        
        # Mossa giocatore (se rilevata)
        player_move = self.state.get_data('player_move')
        if player_move:
            self.renderer.draw_text(f"Tua mossa: {move_names.get(player_move, '?')}", 
                                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), 
                                   'medium', COLORS['success'], center=True)
        else:
            self.renderer.draw_text("Mostra il tuo gesto!", 
                                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), 
                                   'small', COLORS['gray'], center=True)
        
        # Istruzioni
        self.renderer.draw_text("Sasso, Carta, Forbice (o 1, 2, 3)", 
                               (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30), 
                               'tiny', COLORS['muted'], center=True)
    
    # =========================================================================
    # RISULTATO
    # =========================================================================
    
    def _render_result(self, frame):
        """Renderizza il risultato del round."""
        result = self.state.get_data('result')
        is_timeout = self.state.get_data('timeout', False)
        
        # Punteggio
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score_panel(player_score, cpu_score, (SCREEN_WIDTH // 2, 45))
        
        # Round badge
        round_num = self.game.round_count
        self.renderer.draw_round_badge(round_num, (SCREEN_WIDTH // 2, 100), COLORS['primary'])
        
        # Determina colori
        if result == 'player':
            player_color = COLORS['success']
            cpu_color = COLORS['danger']
        elif result == 'cpu' or result == 'timeout':
            player_color = COLORS['danger']
            cpu_color = COLORS['success']
        else:
            player_color = COLORS['warning']
            cpu_color = COLORS['warning']
        
        # Box giocatore
        player_box = pygame.Rect(SCREEN_WIDTH // 4 - 90, 150, 180, 200)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], player_box, border_radius=15)
        pygame.draw.rect(self.renderer.screen, player_color, player_box, width=3, border_radius=15)
        
        self.renderer.draw_text("TU", (SCREEN_WIDTH // 4, 170), 'medium', player_color, center=True)
        
        player_move = self.state.get_data('player_move')
        move_names = {'rock': 'SASSO', 'paper': 'CARTA', 'scissors': 'FORBICE'}
        
        if is_timeout:
            self.renderer.draw_text("TEMPO", (SCREEN_WIDTH // 4, 240), 'large', COLORS['danger'], center=True)
            self.renderer.draw_text("SCADUTO", (SCREEN_WIDTH // 4, 280), 'medium', COLORS['danger'], center=True)
        else:
            self.renderer.draw_move_icon(player_move, (SCREEN_WIDTH // 4, 250), 80, background=False)
            self.renderer.draw_text(move_names.get(player_move, '?'), (SCREEN_WIDTH // 4, 320), 
                                   'small', COLORS['white'], center=True)
        
        # VS
        vs_offset = int(5 * math.sin(self.animation_time * 4))
        self.renderer.draw_text("VS", (SCREEN_WIDTH // 2, 250 + vs_offset), 
                               'title', COLORS['accent'], center=True, shadow=True)
        
        # Box CPU
        cpu_box = pygame.Rect(3 * SCREEN_WIDTH // 4 - 90, 150, 180, 200)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], cpu_box, border_radius=15)
        pygame.draw.rect(self.renderer.screen, cpu_color, cpu_box, width=3, border_radius=15)
        
        self.renderer.draw_text("CPU", (3 * SCREEN_WIDTH // 4, 170), 'medium', cpu_color, center=True)
        
        cpu_move = self.state.get_data('cpu_move')
        self.renderer.draw_move_icon(cpu_move, (3 * SCREEN_WIDTH // 4, 250), 80, background=False)
        self.renderer.draw_text(move_names.get(cpu_move, '?'), (3 * SCREEN_WIDTH // 4, 320), 
                               'small', COLORS['white'], center=True)
        
        # Banner risultato
        if is_timeout:
            self.renderer.draw_text("TEMPO SCADUTO!", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), 
                                   'large', COLORS['danger'], center=True, shadow=True)
            self.renderer.draw_text("Non hai fatto la mossa in tempo!", 
                                   (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60), 
                                   'small', COLORS['white'], center=True)
        else:
            self.renderer.draw_result_banner_improved(result, player_move, cpu_move, SCREEN_HEIGHT - 80)
    
    # =========================================================================
    # GAME OVER
    # =========================================================================
    
    def _render_game_over(self, frame):
        """Renderizza il game over."""
        player_score, cpu_score = self.game.get_score()
        
        # Effetto particelle
        if not hasattr(self, '_game_over_particles_emitted'):
            self.renderer.emit_confetti(SCREEN_WIDTH // 2, 150, 40)
            self._game_over_particles_emitted = True
        
        # Titolo
        self.renderer.draw_text("GAME OVER", (SCREEN_WIDTH // 2, 70), 
                               'hero', COLORS['danger'], center=True, shadow=True, glow=True)
        
        self.renderer.draw_text("La tua serie è terminata!", (SCREEN_WIDTH // 2, 130), 
                               'medium', COLORS['white'], center=True)
        
        # Punteggio grande
        score_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, 160, 300, 80)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], score_box, border_radius=15)
        pygame.draw.rect(self.renderer.screen, COLORS['secondary'], score_box, width=2, border_radius=15)
        
        self.renderer.draw_text("VITTORIE CONSECUTIVE", (SCREEN_WIDTH // 2, 180), 
                               'small', COLORS['secondary'], center=True)
        self.renderer.draw_text(str(player_score), (SCREEN_WIDTH // 2, 218), 
                               'title', COLORS['white'], center=True)
        
        # Statistiche
        stats = self.game.get_stats()
        stats_box = pygame.Rect(SCREEN_WIDTH // 2 - 180, 260, 360, 140)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], stats_box, border_radius=15)
        pygame.draw.rect(self.renderer.screen, COLORS['primary'], stats_box, width=2, border_radius=15)
        
        self.renderer.draw_text("STATISTICHE", (SCREEN_WIDTH // 2, 280), 
                               'medium', COLORS['primary'], center=True)
        
        self.renderer.draw_text(f"Round: {stats['rounds_played']}", (SCREEN_WIDTH // 2, 315), 
                               'small', COLORS['white'], center=True)
        self.renderer.draw_text(f"Vittorie: {stats['player_wins']}  •  Pareggi: {stats['draws']}", 
                               (SCREEN_WIDTH // 2, 345), 'small', COLORS['success'], center=True)
        
        win_rate = stats.get('win_rate', 0) * 100
        win_color = COLORS['success'] if win_rate > 50 else COLORS['danger']
        self.renderer.draw_text(f"Tasso vittoria: {win_rate:.1f}%", (SCREEN_WIDTH // 2, 375), 
                               'small', win_color, center=True)
        
        # Highscore
        if self.highscore.is_high_score(player_score):
            pulse = 0.5 + 0.5 * math.sin(self.animation_time * 5)
            glow_color = tuple(int(c * pulse) for c in COLORS['success'])
            self.renderer.draw_text("* NUOVO RECORD! *", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100), 
                                   'large', COLORS['success'], center=True, glow=True)
        
        # Continua
        self.renderer.draw_text("Premi INVIO per continuare", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50), 
                               'medium', COLORS['white'], center=True)
    
    # =========================================================================
    # CLASSIFICA
    # =========================================================================
    
    def _render_highscore(self, frame, gesture: str):
        """Renderizza la classifica."""
        # Titolo
        self.renderer.draw_text("CLASSIFICA", (SCREEN_WIDTH // 2, 35), 
                               'title', COLORS['primary'], center=True, shadow=True)
        
        # Tab filtri
        tabs = [
            ('all', 'TUTTE'),
            ('classic', 'TRADIZIONALE'),
            ('timed_easy', 'FACILE'),
            ('timed_medium', 'MEDIA'),
            ('timed_hard', 'DIFFICILE')
        ]
        
        tab_width = 130
        start_x = SCREEN_WIDTH // 2 - (len(tabs) * tab_width) // 2 + tab_width // 2
        tab_y = 75
        
        for i, (filter_id, label) in enumerate(tabs):
            x = start_x + i * tab_width
            selected = self.highscore_filter == filter_id
            
            tab_rect = pygame.Rect(x - 60, tab_y - 12, 120, 28)
            if selected:
                pygame.draw.rect(self.renderer.screen, COLORS['secondary'], tab_rect, border_radius=8)
            else:
                pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], tab_rect, border_radius=8)
            
            self.renderer.draw_text(label, (x, tab_y), 'tiny', 
                                   COLORS['white'] if selected else COLORS['muted'], center=True)
        
        # Filtra punteggi
        if self.highscore_filter == 'all':
            scores = self.highscore.get_scores()
        elif self.highscore_filter == 'classic':
            scores = self.highscore.get_scores(mode='classic')
        elif self.highscore_filter == 'timed_easy':
            scores = self.highscore.get_scores(mode='timed', difficulty='easy')
        elif self.highscore_filter == 'timed_medium':
            scores = self.highscore.get_scores(mode='timed', difficulty='medium')
        elif self.highscore_filter == 'timed_hard':
            scores = self.highscore.get_scores(mode='timed', difficulty='hard')
        else:
            scores = self.highscore.get_scores()
        
        # Tabella
        if scores:
            self.renderer.draw_highscore_table_improved(scores, (SCREEN_WIDTH // 2, 120))
        else:
            empty_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 100)
            pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], empty_box, border_radius=15)
            pygame.draw.rect(self.renderer.screen, COLORS['muted'], empty_box, width=1, border_radius=15)
            
            self.renderer.draw_text("Nessun punteggio", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10), 
                                   'medium', COLORS['muted'], center=True)
            self.renderer.draw_text("in questa modalità", (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20), 
                                   'small', COLORS['secondary'], center=True)
        
        # Camera
        if frame is not None:
            self.renderer.draw_camera_feed(frame, (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 80), 
                                          (110, 80), COLORS['primary'])
        
        self.renderer.draw_gesture_indicator(gesture, 1.0, (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 145))
        
        # Istruzioni
        self.renderer.draw_text("<- -> Filtro  •  INVIO Torna", (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30), 
                       'small', COLORS['muted'], center=True)
    
    # =========================================================================
    # INSERIMENTO NOME
    # =========================================================================
    
    def _render_enter_name(self, frame):
        """Renderizza l'inserimento nome."""
        if not hasattr(self, '_name_input_particles') or not self._name_input_particles:
            self.renderer.emit_confetti(SCREEN_WIDTH // 2, 100, 30)
            self._name_input_particles = True
        
        # Titolo
        self.renderer.draw_text("* NUOVO RECORD! *", (SCREEN_WIDTH // 2, 80), 
                       'title', COLORS['success'], center=True, shadow=True, glow=True)
        
        self.renderer.draw_text("Inserisci il tuo nome (max 5 caratteri)", 
                               (SCREEN_WIDTH // 2, 140), 'medium', COLORS['white'], center=True)
        
        # Input
        cursor_visible = int(self.cursor_blink_time * 2) % 2 == 0
        self.renderer.draw_name_input(self.input_name, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20), cursor_visible)
        
        # Istruzioni
        box = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 60, 400, 80)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], box, border_radius=12)
        
        self.renderer.draw_text("Digita le lettere sulla tastiera", 
                               (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 85), 
                               'small', COLORS['muted'], center=True)
        self.renderer.draw_text("INVIO = Conferma  •  BACKSPACE = Cancella", 
                               (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 115), 
                               'small', COLORS['muted'], center=True)
    
    # =========================================================================
    # IMPOSTAZIONI
    # =========================================================================
    
    def _render_settings(self, frame, gesture: str):
        """Renderizza le impostazioni."""
        # Titolo
        self.renderer.draw_text("IMPOSTAZIONI", (SCREEN_WIDTH // 2, 45), 
                               'title', COLORS['primary'], center=True, shadow=True)
        
        # Box settings
        settings_box = pygame.Rect(SCREEN_WIDTH // 2 - 320, 85, 640, 400)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], settings_box, border_radius=20)
        pygame.draw.rect(self.renderer.screen, COLORS['primary'], settings_box, width=2, border_radius=20)
        
        y = 115
        for i, option in enumerate(self.settings_options):
            selected = i == self.settings_selection
            
            # Highlight
            if selected:
                highlight = pygame.Rect(SCREEN_WIDTH // 2 - 300, y - 15, 600, 40)
                pygame.draw.rect(self.renderer.screen, COLORS['primary'], highlight, border_radius=10)
            
            # Label
            label_color = COLORS['white'] if selected else COLORS['gray']
            prefix = "► " if selected else "  "
            self.renderer.draw_text(prefix + option['label'], (SCREEN_WIDTH // 2 - 280, y), 
                                   'medium' if selected else 'small', label_color)
            
            # Valore
            if option['key'] == 'back':
                pass
            elif option['key'] in ['reset_scores', 'refresh_cameras']:
                action_text = "Premi INVIO" if option['key'] == 'reset_scores' else "Premi R"
                self.renderer.draw_text(action_text, (SCREEN_WIDTH // 2 + 150, y), 
                                       'small', COLORS['secondary'] if selected else COLORS['muted'], center=True)
            elif option['key'] == 'camera_index':
                camera_name = GAME_SETTINGS.get_camera_name()
                if len(camera_name) > 22:
                    camera_name = camera_name[:19] + "..."
                
                if selected:
                    self.renderer.draw_text("◄", (SCREEN_WIDTH // 2 + 50, y), 'small', COLORS['white'], center=True)
                    self.renderer.draw_text("►", (SCREEN_WIDTH // 2 + 250, y), 'small', COLORS['white'], center=True)
                
                self.renderer.draw_text(camera_name, (SCREEN_WIDTH // 2 + 150, y), 
                                       'small', COLORS['secondary'], center=True)
            else:
                current_value = getattr(GAME_SETTINGS, option['key'])
                if isinstance(current_value, bool):
                    value_text = "ON" if current_value else "OFF"
                    value_color = COLORS['success'] if current_value else COLORS['danger']
                else:
                    value_text = f"{current_value}{option['unit']}"
                    value_color = COLORS['secondary']
                
                if selected:
                    self.renderer.draw_text("◄", (SCREEN_WIDTH // 2 + 80, y), 'small', COLORS['white'], center=True)
                    self.renderer.draw_text("►", (SCREEN_WIDTH // 2 + 220, y), 'small', COLORS['white'], center=True)
                
                self.renderer.draw_text(value_text, (SCREEN_WIDTH // 2 + 150, y), 
                                       'medium' if selected else 'small', 
                                       value_color if selected else COLORS['muted'], center=True)
            
            y += 48
        
        # Camera
        if frame is not None:
            self.renderer.draw_camera_feed(frame, (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 80), 
                                          (110, 80), COLORS['primary'])
        
        self.renderer.draw_gesture_indicator(gesture, 1.0, (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 145))
        
        # Istruzioni
        self.renderer.draw_text("SU/GIU Scorri  •  <- -> Modifica  •  INVIO Conferma  •  R Aggiorna camera", 
                       (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30), 'tiny', COLORS['muted'], center=True)
    
    # =========================================================================
    # ERRORE CAMERA
    # =========================================================================
    
    def _render_camera_error(self):
        """Renderizza errore camera."""
        # Titolo
        pulse = 0.7 + 0.3 * math.sin(self.animation_time * 4)
        error_color = tuple(int(c * pulse) for c in COLORS['danger'])
        
        self.renderer.draw_text("ERRORE CAMERA", (SCREEN_WIDTH // 2, 70), 
                               'title', error_color, center=True, shadow=True)
        
        self.renderer.draw_text("Camera disconnessa o non disponibile", 
                               (SCREEN_WIDTH // 2, 120), 'medium', COLORS['white'], center=True)
        
        # Box selezione
        box = pygame.Rect(SCREEN_WIDTH // 2 - 220, 160, 440, 300)
        pygame.draw.rect(self.renderer.screen, COLORS['card_bg'], box, border_radius=20)
        pygame.draw.rect(self.renderer.screen, COLORS['danger'], box, width=2, border_radius=20)
        
        self.renderer.draw_text("Seleziona una camera:", (SCREEN_WIDTH // 2, 190), 
                               'medium', COLORS['primary'], center=True)
        
        y = 230
        if self.available_cameras:
            for i, (idx, name) in enumerate(self.available_cameras):
                selected = i == self.camera_error_selection
                
                if selected:
                    highlight = pygame.Rect(SCREEN_WIDTH // 2 - 200, y - 12, 400, 35)
                    pygame.draw.rect(self.renderer.screen, COLORS['primary'], highlight, border_radius=8)
                
                display_name = name if len(name) <= 35 else name[:32] + "..."
                prefix = "► " if selected else "  "
                self.renderer.draw_text(prefix + display_name, (SCREEN_WIDTH // 2 - 180, y), 
                                       'small', COLORS['white'] if selected else COLORS['gray'])
                y += 40
            
            # Aggiorna lista
            selected = self.camera_error_selection >= len(self.available_cameras)
            if selected:
                highlight = pygame.Rect(SCREEN_WIDTH // 2 - 200, y - 12, 400, 35)
                pygame.draw.rect(self.renderer.screen, COLORS['secondary'], highlight, border_radius=8)
            
            self.renderer.draw_text("► Aggiorna lista camera" if selected else "  Aggiorna lista camera", 
                                   (SCREEN_WIDTH // 2 - 180, y), 
                                   'small', COLORS['white'] if selected else COLORS['gray'])
        else:
            self.renderer.draw_text("Nessuna camera trovata!", (SCREEN_WIDTH // 2, y), 
                                   'medium', COLORS['danger'], center=True)
            y += 40
            self.renderer.draw_text("Collega una camera e premi R", (SCREEN_WIDTH // 2, y), 
                                   'small', COLORS['muted'], center=True)
        
        # Istruzioni
        self.renderer.draw_text("↑↓ Seleziona  •  INVIO Conferma  •  R Aggiorna", 
                               (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 55), 'tiny', COLORS['muted'], center=True)
        self.renderer.draw_text("ESC = Continua senza camera", 
                               (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30), 'tiny', COLORS['muted'], center=True)
    
    # =========================================================================
    # METODI NAVIGAZIONE
    # =========================================================================
    
    def mode_up(self):
        self.mode_selection = (self.mode_selection - 1) % len(self.mode_options)
    
    def mode_down(self):
        self.mode_selection = (self.mode_selection + 1) % len(self.mode_options)
    
    def difficulty_left(self):
        if self.mode_selection == 1:
            self.difficulty_selection = (self.difficulty_selection - 1) % len(self.difficulty_options)
    
    def difficulty_right(self):
        if self.mode_selection == 1:
            self.difficulty_selection = (self.difficulty_selection + 1) % len(self.difficulty_options)
    
    def get_selected_mode(self) -> GameMode:
        return GameMode.CLASSIC if self.mode_selection == 0 else GameMode.TIMED
    
    def get_selected_difficulty(self) -> TimedDifficulty:
        return self.difficulty_options[self.difficulty_selection]['key']
    
    def settings_up(self):
        self.settings_selection = (self.settings_selection - 1) % len(self.settings_options)
    
    def settings_down(self):
        self.settings_selection = (self.settings_selection + 1) % len(self.settings_options)
    
    def settings_change_value(self, direction: int) -> Optional[int]:
        option = self.settings_options[self.settings_selection]
        
        if option['key'] in ['back', 'reset_scores', 'refresh_cameras']:
            return False
        
        if option['key'] == 'camera_index':
            cameras = GAME_SETTINGS.available_cameras
            if not cameras:
                return False
            
            current_idx = 0
            for i, (idx, name) in enumerate(cameras):
                if idx == GAME_SETTINGS.camera_index:
                    current_idx = i
                    break
            
            new_idx = (current_idx + direction) % len(cameras)
            new_camera_index = cameras[new_idx][0]
            GAME_SETTINGS.camera_index = new_camera_index
            return new_camera_index
        
        current_value = getattr(GAME_SETTINGS, option['key'])
        values = option['values']
        
        try:
            current_idx = values.index(current_value)
        except ValueError:
            current_idx = 0
        
        new_idx = (current_idx + direction) % len(values)
        setattr(GAME_SETTINGS, option['key'], values[new_idx])
        return True
    
    def settings_select(self) -> Optional[str]:
        option = self.settings_options[self.settings_selection]
        
        if option['key'] == 'back':
            return 'back'
        elif option['key'] == 'reset_scores':
            return 'reset_scores'
        elif option['key'] == 'refresh_cameras':
            return 'refresh_cameras'
        
        return None
    
    def notify_cameras_refreshed(self):
        self._cameras_refreshed = True
        self._cameras_refresh_time = self.animation_time
    
    def handle_name_input(self, event: Any) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and len(self.input_name) >= 1:
                name = self.input_name
                self.input_name = ""
                return name
            elif event.key == pygame.K_BACKSPACE:
                self.input_name = self.input_name[:-1]
            elif len(self.input_name) < 5 and event.unicode.isalpha():
                self.input_name += event.unicode.upper()
        
        return None
    
    def reset_name_input(self):
        self.input_name = ""
        self.cursor_blink_time = 0
        self._name_input_particles = False
    
    def highscore_filter_left(self):
        filters = ['all', 'classic', 'timed_easy', 'timed_medium', 'timed_hard']
        current_idx = filters.index(self.highscore_filter)
        self.highscore_filter = filters[(current_idx - 1) % len(filters)]
    
    def highscore_filter_right(self):
        filters = ['all', 'classic', 'timed_easy', 'timed_medium', 'timed_hard']
        current_idx = filters.index(self.highscore_filter)
        self.highscore_filter = filters[(current_idx + 1) % len(filters)]
    
    def set_available_cameras(self, cameras: list):
        self.available_cameras = cameras
        self.camera_error_selection = 0
    
    def camera_error_up(self):
        if self.available_cameras:
            self.camera_error_selection = (self.camera_error_selection - 1) % (len(self.available_cameras) + 1)
        else:
            self.camera_error_selection = 0
    
    def camera_error_down(self):
        if self.available_cameras:
            self.camera_error_selection = (self.camera_error_selection + 1) % (len(self.available_cameras) + 1)
        else:
            self.camera_error_selection = 0
    
    def get_selected_camera_index(self) -> Optional[int]:
        if not self.available_cameras:
            return None
        
        if self.camera_error_selection >= len(self.available_cameras):
            return -1
        
        return self.available_cameras[self.camera_error_selection][0]
