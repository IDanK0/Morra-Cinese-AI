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
            {'key': 'back', 'label': '← Torna al menu', 'values': ['action'], 'unit': ''},
        ]
    
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
            "👆 Su/Giù per navigare | 👌 OK o 👍 Conferma per selezionare",
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
        
        # Titolo round
        round_num = self.game.round_count
        self.renderer.draw_text(
            f"ROUND {round_num}",
            (SCREEN_WIDTH // 2, 85),
            'medium',
            COLORS['secondary'],
            center=True
        )
        
        # Determina colori in base al risultato
        if result == 'player':
            player_border_color = COLORS['success']
            cpu_border_color = COLORS['danger']
        elif result == 'cpu':
            player_border_color = COLORS['danger']
            cpu_border_color = COLORS['success']
        else:
            player_border_color = COLORS['secondary']
            cpu_border_color = COLORS['secondary']
        
        # Box giocatore
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
        
        self.renderer.draw_move_icon(
            player_move,
            (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 20),
            100
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
        
        # VS animato
        vs_offset = int(5 * math.sin(self.animation_time * 4))
        self.renderer.draw_text(
            "VS",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20 + vs_offset),
            'title',
            COLORS['secondary'],
            center=True,
            shadow=True
        )
        
        # Box CPU con indicazione chiara
        cpu_box_rect = pygame.Rect(3 * SCREEN_WIDTH // 4 - 100, SCREEN_HEIGHT // 2 - 130, 200, 220)
        pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], cpu_box_rect, border_radius=15)
        pygame.draw.rect(self.renderer.screen, cpu_border_color, cpu_box_rect, width=4, border_radius=15)
        
        self.renderer.draw_text(
            "CPU",
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 100),
            'medium',
            cpu_border_color,
            center=True
        )
        
        self.renderer.draw_move_icon(
            cpu_move,
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - 20),
            100
        )
        
        # Nome mossa CPU
        self.renderer.draw_text(
            move_names.get(cpu_move, '?'),
            (3 * SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 60),
            'small',
            COLORS['white'],
            center=True
        )
        
        # Banner risultato migliorato
        if result:
            self.renderer.draw_result_banner_improved(
                result, player_move, cpu_move,
                SCREEN_HEIGHT - 80
            )
    
    def _render_game_over(self, frame):
        """Renderizza la schermata di fine partita (modalità sopravvivenza)."""
        player_score, cpu_score = self.game.get_score()
        
        # In modalità sopravvivenza, il game over significa sempre sconfitta
        bg_color = COLORS['danger']
        title = "GAME OVER"
        subtitle = "Hai perso! La tua serie è terminata."
        
        # Overlay semi-trasparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(bg_color)
        overlay.set_alpha(50)
        self.renderer.screen.blit(overlay, (0, 0))
        
        # Titolo
        self.renderer.draw_text(
            title,
            (SCREEN_WIDTH // 2, 80),
            'title',
            COLORS['white'],
            center=True,
            shadow=True
        )
        
        self.renderer.draw_text(
            subtitle,
            (SCREEN_WIDTH // 2, 140),
            'medium',
            COLORS['white'],
            center=True
        )
        
        # Punteggio (vittorie consecutive)
        self.renderer.draw_text(
            f"🏆 VITTORIE CONSECUTIVE: {player_score}",
            (SCREEN_WIDTH // 2, 200),
            'large',
            COLORS['secondary'],
            center=True
        )
        
        # Statistiche dettagliate
        stats = self.game.get_stats()
        stats_y = 280
        
        # Box statistiche
        stats_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, stats_y - 20, 360, 150)
        pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], stats_rect, border_radius=15)
        pygame.draw.rect(self.renderer.screen, COLORS['primary'], stats_rect, width=2, border_radius=15)
        
        self.renderer.draw_text(
            "📊 STATISTICHE",
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
            f"Vittorie: {stats['player_wins']} | Pareggi: {stats['draws']}",
            (SCREEN_WIDTH // 2, stats_y + 85),
            'small',
            COLORS['gray'],
            center=True
        )
        
        win_rate = stats.get('win_rate', 0) * 100
        self.renderer.draw_text(
            f"Tasso di vittoria: {win_rate:.1f}%",
            (SCREEN_WIDTH // 2, stats_y + 120),
            'small',
            COLORS['success'] if win_rate > 50 else COLORS['danger'],
            center=True
        )
        
        # Messaggio per highscore
        if self.highscore.is_high_score(player_score):
            self.renderer.draw_text(
                "🎉 NUOVO RECORD! Entrerai in classifica!",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 120),
                'medium',
                COLORS['success'],
                center=True
            )
        
        # Istruzioni
        self.renderer.draw_text(
            "👌 OK o 👍 Conferma per continuare",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60),
            'medium',
            COLORS['white'],
            center=True
        )
    
    def _render_highscore(self, frame, gesture: str):
        """Renderizza la classifica."""
        self.renderer.draw_text(
            "🏆 CLASSIFICA",
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
        
        # Tabella punteggi
        scores = self.highscore.get_scores(10)
        if scores:
            self.renderer.draw_highscore_table_improved(
                scores,
                (SCREEN_WIDTH // 2, 140)
            )
        else:
            # Messaggio se nessun punteggio
            no_score_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50, 300, 100)
            pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], no_score_rect, border_radius=15)
            pygame.draw.rect(self.renderer.screen, COLORS['gray'], no_score_rect, width=2, border_radius=15)
            
            self.renderer.draw_text(
                "Nessun punteggio",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 15),
                'medium',
                COLORS['gray'],
                center=True
            )
            self.renderer.draw_text(
                "Gioca per entrare in classifica!",
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20),
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
            "👌 OK o 👍 Conferma per tornare al menu",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35),
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
        """Renderizza le impostazioni con menu navigabile."""
        self.renderer.draw_text(
            "⚙️ IMPOSTAZIONI",
            (SCREEN_WIDTH // 2, 50),
            'title',
            COLORS['primary'],
            center=True,
            shadow=True
        )
        
        # Box impostazioni
        settings_box = pygame.Rect(SCREEN_WIDTH // 2 - 280, 100, 560, 380)
        pygame.draw.rect(self.renderer.screen, COLORS['dark_gray'], settings_box, border_radius=15)
        pygame.draw.rect(self.renderer.screen, COLORS['primary'], settings_box, width=2, border_radius=15)
        
        y = 130
        for i, option in enumerate(self.settings_options):
            selected = i == self.settings_selection
            
            # Evidenzia opzione selezionata
            if selected:
                highlight_rect = pygame.Rect(SCREEN_WIDTH // 2 - 265, y - 12, 530, 45)
                pygame.draw.rect(self.renderer.screen, COLORS['primary'], highlight_rect, border_radius=8)
            
            label_color = COLORS['white'] if selected else COLORS['gray']
            
            # Label
            self.renderer.draw_text(
                option['label'],
                (SCREEN_WIDTH // 2 - 240, y),
                'medium' if selected else 'small',
                label_color
            )
            
            # Valore corrente
            if option['key'] == 'back':
                pass  # Nessun valore per il tasto indietro
            elif option['key'] == 'reset_scores':
                self.renderer.draw_text(
                    "👌 Premi OK",
                    (SCREEN_WIDTH // 2 + 150, y),
                    'small',
                    COLORS['danger'] if selected else COLORS['gray'],
                    center=True
                )
            else:
                current_value = getattr(GAME_SETTINGS, option['key'])
                if isinstance(current_value, bool):
                    value_text = "Sì" if current_value else "No"
                    value_color = COLORS['success'] if current_value else COLORS['danger']
                else:
                    value_text = f"{current_value}{option['unit']}"
                    value_color = COLORS['secondary']
                
                # Frecce per navigazione valori
                if selected:
                    self.renderer.draw_text("◀", (SCREEN_WIDTH // 2 + 80, y), 'small', COLORS['white'], center=True)
                    self.renderer.draw_text("▶", (SCREEN_WIDTH // 2 + 220, y), 'small', COLORS['white'], center=True)
                
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
            "👆👇 Su/Giù per navigare | ◀▶ per modificare | 👌 OK per confermare",
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 35),
            'tiny',
            COLORS['gray'],
            center=True
        )
    
    def settings_up(self):
        """Naviga su nelle impostazioni."""
        self.settings_selection = (self.settings_selection - 1) % len(self.settings_options)
    
    def settings_down(self):
        """Naviga giù nelle impostazioni."""
        self.settings_selection = (self.settings_selection + 1) % len(self.settings_options)
    
    def settings_change_value(self, direction: int) -> bool:
        """
        Modifica il valore dell'impostazione selezionata.
        
        Args:
            direction: -1 per precedente, 1 per successivo
            
        Returns:
            True se è stata effettuata una modifica
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
