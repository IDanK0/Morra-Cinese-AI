"""
Schermate del gioco
"""

import pygame
import math
import random
from typing import Optional
import time

from game.game_state import GameState, StateManager
from game.game_logic import GameLogic, Move, RoundResult
from game.highscore import HighScoreManager
from ui.renderer import Renderer
from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, ROUNDS_TO_WIN, COUNTDOWN_TIME, GAME_SETTINGS


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
        
        # Settings menu
        self.settings_selection = 0
        self.settings_options = [
            {'key': 'gesture_hold_time', 'label': 'Tempo conferma gesto', 'values': [0.5, 0.75, 1.0, 1.25, 1.5], 'unit': 's'},
            {'key': 'countdown_time', 'label': 'Tempo countdown', 'values': [2, 3, 4, 5], 'unit': 's'},
            {'key': 'camera_flip', 'label': 'Specchia camera', 'values': [True, False], 'unit': ''},
            {'key': 'show_fps', 'label': 'Mostra FPS', 'values': [True, False], 'unit': ''},
            {'key': 'reset_scores', 'label': 'Cancella classifica', 'values': ['action'], 'unit': ''},
            {'key': 'back', 'label': '<- Torna al menu', 'values': ['action'], 'unit': ''},
        ]
    
    def update(self, dt: float):
        """Aggiorna le animazioni e gli effetti."""
        self.animation_time += dt
        self.cursor_blink_time += dt
        self.renderer.update_particles(dt)
        self.renderer.apply_screen_overlay(dt)
    
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
        
        # Disegna particelle e overlay sopra tutto
        self.renderer.draw_particles()
        self.renderer.apply_screen_overlay(0)
    
    def _render_menu(self, frame, gesture: str):
        """Renderizza il menu principale con effetti migliorati."""
        # Sfondo con gradiente
        top_color = (30, 30, 50)
        bottom_color = COLORS['background']
        gradient_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_gradient_rect(gradient_rect, top_color, bottom_color)
        
        # Titolo con effetto pulsante
        y_offset = int(10 * math.sin(self.animation_time * 2))
        self.renderer.draw_text(
            "MORRA CINESE",
            (SCREEN_WIDTH // 2, 70 + y_offset),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        
        # Sottotitolo
        self.renderer.draw_text(
            "Portatile Interattiva",
            (SCREEN_WIDTH // 2, 130),
            'medium',
            COLORS['secondary'],
            center=True
        )
        
        # Decorazione: cerchi pulsanti
        pulse_time = self.animation_time
        self.renderer.draw_pulse_circle(
            (SCREEN_WIDTH // 2 - 250, 70 + y_offset),
            30, COLORS['primary'], pulse_time
        )
        self.renderer.draw_pulse_circle(
            (SCREEN_WIDTH // 2 + 250, 70 + y_offset),
            30, COLORS['secondary'], pulse_time + 0.3
        )
        
        # Feed camera (piccolo)
        if frame is not None:
            self.renderer.draw_camera_feed(
                frame,
                (SCREEN_WIDTH - 120, 80),
                (160, 120),
                COLORS['primary']
            )
        
        # Opzioni menu con effetti di glow
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
            
            # Effetto glow per pulsante selezionato
            glow = 0.5 + 0.3 * math.sin(self.animation_time * 4) if selected else 0.0
            
            self.renderer.draw_glowing_button(
                label,
                (SCREEN_WIDTH // 2, y),
                (250, 55),
                selected,
                glow
            )
        
        # Istruzioni eleganti
        self.renderer.draw_text(
            "Up Down per navigare  |  INVIO per selezionare",
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
        """Renderizza la schermata di gioco con effetti migliorati."""
        # Sfondo con gradiente
        top_color = COLORS['background']
        bottom_color = (40, 40, 50)
        gradient_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_gradient_rect(gradient_rect, top_color, bottom_color)
        
        # Punteggio con stile migliorato
        player_score, cpu_score = self.game.get_score()
        self.renderer.draw_score(
            player_score, cpu_score,
            (SCREEN_WIDTH // 2, 40)
        )
        
        # Feed camera (grande) con bordo luminoso
        if frame is not None:
            self.renderer.draw_camera_feed(
                frame,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                (400, 300),
                COLORS['primary']
            )
        
        # Istruzioni dinamiche
        instruction_color = COLORS['secondary'] if gesture in ['rock', 'paper', 'scissors'] else COLORS['white']
        self.renderer.draw_text(
            "Fai il tuo gesto e mantienilo!",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120),
            'medium',
            instruction_color,
            center=True
        )
        
        # Indicatore gesto attuale con effetto
        if gesture in ['rock', 'paper', 'scissors']:
            # Emetti particelle quando viene riconosciuto un gesto
            if gesture != getattr(self, '_last_gesture', None):
                self.renderer.emit_particles(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80,
                    count=8, color=COLORS['success']
                )
                self._last_gesture = gesture
            
            self.renderer.draw_gesture_indicator(
                gesture, 1.0,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
            )
        else:
            self._last_gesture = None
            self.renderer.draw_text(
                "In attesa di gesto...",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80),
                'small',
                COLORS['gray'],
                center=True
            )
        
        # Barra di progresso con animazione
        if gesture in ['rock', 'paper', 'scissors'] and progress > 0:
            bar_width = 300
            bar_height = 20
            bar_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - bar_width // 2,
                SCREEN_HEIGHT - 40,
                bar_width,
                bar_height
            )
            pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], bar_rect, border_radius=10)
            
            if progress > 0:
                progress_rect = pygame.Rect(
                    bar_rect.left,
                    bar_rect.top,
                    int(bar_rect.width * progress),
                    bar_height
                )
                color_progress = COLORS['secondary'] if progress < 0.5 else COLORS['success']
                pygame.draw.rect(self.renderer.screen, color_progress, progress_rect, border_radius=10)
            
            pygame.draw.rect(self.renderer.screen, COLORS['white'], bar_rect, width=2, border_radius=10)
    
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
        """Renderizza il risultato del round con effetti migliorati."""
        # Sfondo con gradiente dinamico
        if self.state.get_data('result') == 'player':
            top_color = (30, 50, 30)
            bottom_color = COLORS['success']
        elif self.state.get_data('result') == 'cpu':
            top_color = (50, 30, 30)
            bottom_color = COLORS['danger']
        else:
            top_color = (40, 40, 40)
            bottom_color = COLORS['secondary']
        
        gradient_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_gradient_rect(gradient_rect, top_color, bottom_color)
        
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
        
        # Badge round con stile esagonale
        round_num = self.game.round_count
        self.renderer.draw_round_badge(
            round_num,
            (SCREEN_WIDTH // 2, 85),
            COLORS['primary']
        )
        
        # Determina colori in base al risultato
        if result == 'player':
            player_border_color = COLORS['success']
            cpu_border_color = COLORS['danger']
            outcome_color = COLORS['success']
        elif result == 'cpu':
            player_border_color = COLORS['danger']
            cpu_border_color = COLORS['success']
            outcome_color = COLORS['danger']
        else:
            player_border_color = COLORS['secondary']
            cpu_border_color = COLORS['secondary']
            outcome_color = COLORS['secondary']
        
        # Box giocatore con effetto
        player_box_rect = pygame.Rect(SCREEN_WIDTH // 4 - 100, SCREEN_HEIGHT // 2 - 130, 200, 220)
        pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], player_box_rect, border_radius=15)
        pygame.draw.rect(self.renderer.screen, player_border_color, player_box_rect, width=4, border_radius=15)
        
        self.renderer.draw_text(
            "TU",
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 100),
            'medium',
            player_border_color,
            center=True
        )
        
        # Usa le nuove icone migliorate
        self.renderer.draw_move_icon_enhanced(
            player_move,
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 20),
            100,
            background=False
        )
        
        # Nome mossa giocatore
        move_names = {'rock': 'SASSO', 'paper': 'CARTA', 'scissors': 'FORBICE'}
        self.renderer.draw_text(
            move_names.get(player_move, '?'),
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 60),
            'small',
            COLORS['white'],
            center=True
        )
        
        # VS animato con pulsazione
        vs_offset = int(5 * math.sin(self.animation_time * 4))
        vs_scale = 1.0 + 0.1 * math.sin(self.animation_time * 3)
        self.renderer.draw_text(
            "VS",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + vs_offset),
            'title',
            outcome_color,
            center=True,
            shadow=True
        )
        
        # Box CPU con indicazione chiara
        cpu_box_rect = pygame.Rect(3 * SCREEN_WIDTH // 4 - 100, SCREEN_HEIGHT // 2 - 130, 200, 220)
        pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], cpu_box_rect, border_radius=15)
        pygame.draw.rect(self.renderer.screen, cpu_border_color, cpu_box_rect, width=4, border_radius=15)
        
        self.renderer.draw_text(
            "IA",
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 100),
            'medium',
            cpu_border_color,
            center=True
        )
        
        # Usa le nuove icone migliorate
        self.renderer.draw_move_icon_enhanced(
            cpu_move,
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 20),
            100,
            background=False
        )
        
        # Nome mossa CPU
        self.renderer.draw_text(
            move_names.get(cpu_move, '?'),
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 60),
            'small',
            COLORS['white'],
            center=True
        )
        
        # Banner risultato migliorato con particelle
        if result:
            self.renderer.draw_result_banner_improved(
                result, player_move, cpu_move,
                SCREEN_HEIGHT - 80
            )
            
            # Emetti particelle di celebrazione
            if result == 'player':
                for _ in range(2):
                    x = SCREEN_WIDTH // 4 + random.randint(-50, 50)
                    y = SCREEN_HEIGHT // 2
                    self.renderer.emit_particles(x, y, count=10, color=COLORS['success'], lifetime=1.5)
    
    def _render_game_over(self, frame):
        """Renderizza la schermata di fine partita con effetti spettacolari."""
        # Sfondo con gradiente drammatico
        top_color = (80, 30, 30)
        bottom_color = (30, 30, 30)
        gradient_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_gradient_rect(gradient_rect, top_color, bottom_color)
        
        player_score, cpu_score = self.game.get_score()
        
        # Emetti particelle di esplosione al primo render
        if not hasattr(self, '_game_over_particles_emitted'):
            self.renderer.emit_particles(
                SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3,
                count=30, color=COLORS['danger'], lifetime=2.0, velocity_range=8.0
            )
            self._game_over_particles_emitted = True
        
        # Titolo con flash
        title = "GAME OVER"
        self.renderer.draw_text(
            title,
            (SCREEN_WIDTH // 2, 80),
            'title',
            COLORS['danger'],
            center=True,
            shadow=True
        )
        
        self.renderer.draw_text(
            "Hai perso! La tua serie e' terminata.",
            (SCREEN_WIDTH // 2, 140),
            'medium',
            COLORS['white'],
            center=True
        )
        
        # Punteggio (vittorie consecutive) con enfasi
        self.renderer.draw_text(
            f"VITTORIE CONSECUTIVE: {player_score}",
            (SCREEN_WIDTH // 2, 200),
            'large',
            COLORS['secondary'],
            center=True
        )
        
        # Statistiche dettagliate con miglior design
        stats = self.game.get_stats()
        stats_y = 280
        
        # Box statistiche con bordo luminoso
        stats_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, stats_y - 20, 400, 160)
        pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], stats_rect, border_radius=15)
        pygame.draw.rect(self.renderer.screen, COLORS['primary'], stats_rect, width=3, border_radius=15)
        
        self.renderer.draw_text(
            "[STAT] STATISTICHE",
            (SCREEN_WIDTH // 2, stats_y + 10),
            'medium',
            COLORS['primary'],
            center=True
        )
        
        self.renderer.draw_text(
            f"Round giocati: {stats['rounds_played']}",
            (SCREEN_WIDTH // 2, stats_y + 50),
            'small',
            COLORS['white'],
            center=True
        )
        
        self.renderer.draw_text(
            f"Vittorie: {stats['player_wins']}  |  Pareggi: {stats['draws']}",
            (SCREEN_WIDTH // 2, stats_y + 85),
            'small',
            COLORS['success'],
            center=True
        )
        
        win_rate = stats.get('win_rate', 0) * 100
        win_color = COLORS['success'] if win_rate > 50 else COLORS['danger']
        self.renderer.draw_text(
            f"Tasso vittoria: {win_rate:.1f}%",
            (SCREEN_WIDTH // 2, stats_y + 120),
            'small',
            win_color,
            center=True
        )
        
        # Messaggio per highscore con effetto glow
        if self.highscore.is_high_score(player_score):
            # Particelle di celebrazione
            if not hasattr(self, '_highscore_particles'):
                self.renderer.emit_particles(
                    SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120,
                    count=20, color=COLORS['success'], lifetime=2.0, velocity_range=5.0
                )
                self._highscore_particles = True
            
            self.renderer.draw_text(
                "* NUOVO RECORD! Entrerai in classifica! *",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120),
                'medium',
                COLORS['success'],
                center=True
            )
        
        # Istruzioni
        self.renderer.draw_text(
            "Premi INVIO per continuare",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
            'medium',
            COLORS['white'],
            center=True
        )
    
    def _render_highscore(self, frame, gesture: str):
        """Renderizza la classifica con effetti migliorati."""
        # Sfondo con gradiente
        top_color = (30, 35, 50)
        bottom_color = COLORS['background']
        gradient_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_gradient_rect(gradient_rect, top_color, bottom_color)
        
        # Titolo con effetto pulsante
        self.renderer.draw_text(
            "[TROPHY] CLASSIFICA [TROPHY]",
            (SCREEN_WIDTH // 2, 50),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        
        self.renderer.draw_text(
            "Vittorie Consecutive",
            (SCREEN_WIDTH // 2, 95),
            'small',
            COLORS['secondary'],
            center=True
        )
        
        # Tabella punteggi (numero dinamico di righe basato sui punteggi presenti)
        scores = self.highscore.get_scores()
        if scores:
            self.renderer.draw_highscore_table_improved(
                scores,
                (SCREEN_WIDTH // 2, 140)
            )
        else:
            # Messaggio se nessun punteggio con design migliorato
            no_score_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 80, 360, 160)
            pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], no_score_rect, border_radius=15)
            pygame.draw.rect(self.renderer.screen, COLORS['gray'], no_score_rect, width=2, border_radius=15)
            
            self.renderer.draw_text(
                "[!] Nessun Punteggio",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30),
                'medium',
                COLORS['gray'],
                center=True
            )
            self.renderer.draw_text(
                "Gioca una partita per",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15),
                'small',
                COLORS['secondary'],
                center=True
            )
            self.renderer.draw_text(
                "entrare in classifica!",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45),
                'small',
                COLORS['secondary'],
                center=True
            )
        
        # Feed camera (piccolo, in basso a destra)
        if frame is not None:
            self.renderer.draw_camera_feed(
                frame,
                (SCREEN_WIDTH - 90, SCREEN_HEIGHT - 90),
                (120, 90),
                COLORS['primary']
            )
        
        # Indicatore gesto
        self.renderer.draw_gesture_indicator(
            gesture, 1.0,
            (SCREEN_WIDTH - 90, SCREEN_HEIGHT - 150)
        )
        
        # Istruzioni
        self.renderer.draw_text(
            "Premi INVIO per tornare al menu",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35),
            'small',
            COLORS['gray'],
            center=True
        )
    
    def _render_enter_name(self, frame):
        """Renderizza l'input del nome con effetti migliorati."""
        # Sfondo con gradiente celebrativo
        top_color = (50, 40, 30)
        bottom_color = (30, 30, 50)
        gradient_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_gradient_rect(gradient_rect, top_color, bottom_color)
        
        # Emetti particelle di celebrazione
        if not hasattr(self, '_name_input_particles'):
            for _ in range(3):
                x = SCREEN_WIDTH // 2 + random.randint(-100, 100)
                y = 80
                self.renderer.emit_particles(x, y, count=12, color=COLORS['success'], lifetime=1.5)
            self._name_input_particles = True
        
        self.renderer.draw_text(
            "* NUOVO RECORD! *",
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
        
        # Campo input con stile migliorato
        cursor_visible = int(self.cursor_blink_time * 2) % 2 == 0
        self.renderer.draw_name_input(
            self.input_name,
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
            cursor_visible
        )
        
        # Tastiera virtuale elegante
        self.renderer.draw_text(
            "Digita le lettere sulla tastiera",
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
        """Renderizza le impostazioni con design migliorato."""
        # Sfondo con gradiente
        top_color = COLORS['background']
        bottom_color = (40, 40, 50)
        gradient_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.renderer.draw_gradient_rect(gradient_rect, top_color, bottom_color)
        
        self.renderer.draw_text(
            "[GEAR] IMPOSTAZIONI [GEAR]",
            (SCREEN_WIDTH // 2, 50),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        
        # Box impostazioni con design migliorato
        settings_box = pygame.Rect(SCREEN_WIDTH // 2 - 300, 100, 600, 380)
        pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], settings_box, border_radius=15)
        pygame.draw.rect(self.renderer.screen, COLORS['primary'], settings_box, width=3, border_radius=15)
        
        y = 130
        for i, option in enumerate(self.settings_options):
            selected = i == self.settings_selection
            
            # Evidenzia opzione selezionata con glow
            if selected:
                highlight_rect = pygame.Rect(SCREEN_WIDTH // 2 - 285, y - 12, 570, 45)
                pygame.draw.rect(self.renderer.screen, COLORS['primary'], highlight_rect, border_radius=10)
                # Glow effect
                glow_intensity = 0.5 + 0.3 * math.sin(self.animation_time * 4)
                glow_color = tuple(int(c * glow_intensity * 0.5) for c in COLORS['primary'])
            
            label_color = COLORS['white'] if selected else COLORS['gray']
            
            # Label con icone per opzioni specifiche
            label_text = option['label']
            if selected:
                label_text = "> " + label_text + " <"
            
            self.renderer.draw_text(
                label_text,
                (SCREEN_WIDTH // 2 - 260, y),
                'medium' if selected else 'small',
                label_color
            )
            
            # Valore corrente
            if option['key'] == 'back':
                pass  # Nessun valore per il tasto indietro
            elif option['key'] == 'reset_scores':
                self.renderer.draw_text(
                    "[!] Premi INVIO",
                    (SCREEN_WIDTH // 2 + 150, y),
                    'small',
                    COLORS['danger'] if selected else COLORS['gray'],
                    center=True
                )
            else:
                current_value = getattr(GAME_SETTINGS, option['key'])
                if isinstance(current_value, bool):
                    value_text = "[ON] ON" if current_value else "[OFF] OFF"
                    value_color = COLORS['success'] if current_value else COLORS['danger']
                else:
                    value_text = f"{current_value}{option['unit']}"
                    value_color = COLORS['secondary']
                
                # Frecce per navigazione valori
                if selected:
                    self.renderer.draw_text("<", (SCREEN_WIDTH // 2 + 80, y), 'small', COLORS['white'], center=True)
                    self.renderer.draw_text(">", (SCREEN_WIDTH // 2 + 220, y), 'small', COLORS['white'], center=True)
                
                self.renderer.draw_text(
                    value_text,
                    (SCREEN_WIDTH // 2 + 150, y),
                    'medium' if selected else 'small',
                    value_color if selected else COLORS['gray'],
                    center=True
                )
            
            y += 55
        
        # Feed camera (piccolo)
        if frame is not None:
            self.renderer.draw_camera_feed(
                frame,
                (SCREEN_WIDTH - 90, SCREEN_HEIGHT - 90),
                (120, 90),
                COLORS['primary']
            )
        
        # Indicatore gesto
        self.renderer.draw_gesture_indicator(
            gesture, 1.0,
            (SCREEN_WIDTH - 90, SCREEN_HEIGHT - 150)
        )
        
        # Istruzioni
        self.renderer.draw_text(
            "Giu per scorrere | < > per modificare | INVIO per confermare",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35),
            'tiny',
            COLORS['gray'],
            center=True
        )
    
    def settings_up(self):
        """Naviga su nelle impostazioni."""
        self.settings_selection = (self.settings_selection - 1) % len(self.settings_options)
    
    def settings_down(self):
        """Naviga giu' nelle impostazioni."""
        self.settings_selection = (self.settings_selection + 1) % len(self.settings_options)
    
    def settings_change_value(self, direction: int) -> bool:
        """
        Modifica il valore dell'impostazione selezionata.
        
        Args:
            direction: -1 per precedente, 1 per successivo
            
        Returns:
            True se e' stata effettuata una modifica
        """
        option = self.settings_options[self.settings_selection]
        
        if option['key'] in ['back', 'reset_scores']:
            return False
        
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
        """
        Gestisce la selezione dell'impostazione corrente.
        
        Returns:
            'back' per tornare al menu, 'reset_scores' per cancellare la classifica, None altrimenti
        """
        option = self.settings_options[self.settings_selection]
        
        if option['key'] == 'back':
            return 'back'
        elif option['key'] == 'reset_scores':
            return 'reset_scores'
        
        return None
    
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
