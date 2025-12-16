"""
Modulo di rendering grafico per il gioco
"""

import pygame
import numpy as np
import cv2
from typing import Tuple, Optional, List
import math

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


class Renderer:
    """
    Classe per il rendering dell'interfaccia grafica del gioco.
    """
    
    def __init__(self, screen: pygame.Surface):
        """
        Inizializza il renderer.
        
        Args:
            screen: Superficie Pygame su cui disegnare
        """
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Carica i font
        pygame.font.init()
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'large': pygame.font.Font(None, 56),
            'medium': pygame.font.Font(None, 42),
            'small': pygame.font.Font(None, 32),
            'tiny': pygame.font.Font(None, 24),
        }
        
        # Cache per superfici pre-renderizzate
        self._cache = {}
    
    def clear(self, color: Tuple[int, int, int] = None):
        """Pulisce lo schermo."""
        if color is None:
            color = COLORS['background']
        self.screen.fill(color)
    
    def draw_text(self, 
                  text: str, 
                  pos: Tuple[int, int], 
                  font_size: str = 'medium',
                  color: Tuple[int, int, int] = None,
                  center: bool = False,
                  shadow: bool = False) -> pygame.Rect:
        """
        Disegna testo sulla schermata.
        
        Args:
            text: Testo da disegnare
            pos: Posizione (x, y)
            font_size: Chiave del font ('title', 'large', 'medium', 'small', 'tiny')
            color: Colore RGB del testo
            center: Se True, centra il testo sulla posizione
            shadow: Se True, aggiunge un'ombra
            
        Returns:
            Rettangolo del testo
        """
        if color is None:
            color = COLORS['white']
        
        font = self.fonts.get(font_size, self.fonts['medium'])
        
        # Ombra
        if shadow:
            shadow_surf = font.render(text, True, COLORS['black'])
            shadow_rect = shadow_surf.get_rect()
            if center:
                shadow_rect.center = (pos[0] + 2, pos[1] + 2)
            else:
                shadow_rect.topleft = (pos[0] + 2, pos[1] + 2)
            self.screen.blit(shadow_surf, shadow_rect)
        
        # Testo principale
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect()
        
        if center:
            text_rect.center = pos
        else:
            text_rect.topleft = pos
        
        self.screen.blit(text_surf, text_rect)
        return text_rect
    
    def draw_button(self,
                    text: str,
                    pos: Tuple[int, int],
                    size: Tuple[int, int] = (200, 50),
                    selected: bool = False,
                    color: Tuple[int, int, int] = None) -> pygame.Rect:
        """
        Disegna un pulsante.
        
        Args:
            text: Testo del pulsante
            pos: Posizione centrale
            size: Dimensioni (larghezza, altezza)
            selected: Se True, evidenzia il pulsante
            color: Colore di sfondo
            
        Returns:
            Rettangolo del pulsante
        """
        if color is None:
            color = COLORS['primary'] if selected else COLORS['dark_gray']
        
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Sfondo
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        # Bordo
        border_color = COLORS['white'] if selected else COLORS['gray']
        pygame.draw.rect(self.screen, border_color, rect, width=3, border_radius=10)
        
        # Testo
        self.draw_text(text, pos, 'medium', COLORS['white'], center=True)
        
        return rect
    
    def draw_camera_feed(self, 
                         frame: np.ndarray, 
                         pos: Tuple[int, int],
                         size: Tuple[int, int] = (320, 240),
                         border_color: Tuple[int, int, int] = None):
        """
        Disegna il feed della camera.
        
        Args:
            frame: Frame BGR da OpenCV
            pos: Posizione centrale
            size: Dimensioni target
            border_color: Colore del bordo
        """
        if frame is None:
            return
        
        # Ridimensiona il frame
        frame_resized = cv2.resize(frame, size)
        
        # Converti da BGR a RGB
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        
        # Ruota per Pygame (necessario per orientamento corretto)
        frame_rotated = np.rot90(frame_rgb)
        frame_rotated = np.flipud(frame_rotated)
        
        # Crea superficie Pygame
        surf = pygame.surfarray.make_surface(frame_rotated)
        rect = surf.get_rect(center=pos)
        
        # Disegna bordo
        if border_color:
            border_rect = rect.inflate(6, 6)
            pygame.draw.rect(self.screen, border_color, border_rect, border_radius=5)
        
        self.screen.blit(surf, rect)
    
    def draw_progress_bar(self,
                          pos: Tuple[int, int],
                          size: Tuple[int, int],
                          progress: float,
                          color: Tuple[int, int, int] = None,
                          bg_color: Tuple[int, int, int] = None):
        """
        Disegna una barra di progresso.
        
        Args:
            pos: Posizione centrale
            size: Dimensioni (larghezza, altezza)
            progress: Valore da 0.0 a 1.0
            color: Colore della barra
            bg_color: Colore dello sfondo
        """
        if color is None:
            color = COLORS['primary']
        if bg_color is None:
            bg_color = COLORS['dark_gray']
        
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Sfondo
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=5)
        
        # Progresso
        progress = max(0, min(1, progress))
        progress_width = int(size[0] * progress)
        if progress_width > 0:
            progress_rect = pygame.Rect(rect.left, rect.top, progress_width, size[1])
            pygame.draw.rect(self.screen, color, progress_rect, border_radius=5)
        
        # Bordo
        pygame.draw.rect(self.screen, COLORS['white'], rect, width=2, border_radius=5)
    
    def draw_move_icon(self,
                       move: str,
                       pos: Tuple[int, int],
                       size: int = 100,
                       color: Tuple[int, int, int] = None):
        """
        Disegna l'icona di una mossa.
        
        Args:
            move: 'rock', 'paper', o 'scissors'
            pos: Posizione centrale
            size: Dimensione dell'icona
            color: Colore dell'icona
        """
        if color is None:
            color_map = {
                'rock': COLORS['rock'],
                'paper': COLORS['paper'],
                'scissors': COLORS['scissors']
            }
            color = color_map.get(move, COLORS['white'])
        
        # Cerchio di sfondo
        pygame.draw.circle(self.screen, COLORS['dark_gray'], pos, size // 2)
        pygame.draw.circle(self.screen, color, pos, size // 2, width=4)
        
        # Emoji/simbolo
        symbols = {
            'rock': '✊',
            'paper': '✋',
            'scissors': '✌️'
        }
        symbol = symbols.get(move, '?')
        self.draw_text(symbol, pos, 'large', COLORS['white'], center=True)
    
    def draw_score(self,
                   player_score: int,
                   cpu_score: int,
                   pos: Tuple[int, int]):
        """
        Disegna il punteggio.
        
        Args:
            player_score: Punteggio del giocatore
            cpu_score: Punteggio della CPU
            pos: Posizione centrale
        """
        # Sfondo
        rect = pygame.Rect(0, 0, 200, 60)
        rect.center = pos
        pygame.draw.rect(self.screen, COLORS['dark_gray'], rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['primary'], rect, width=2, border_radius=10)
        
        # Punteggi
        score_text = f"TU: {player_score}  -  CPU: {cpu_score}"
        self.draw_text(score_text, pos, 'medium', COLORS['white'], center=True)
    
    def draw_countdown(self, number: int, pos: Tuple[int, int]):
        """
        Disegna il numero del countdown.
        
        Args:
            number: Numero da mostrare
            pos: Posizione centrale
        """
        # Cerchio di sfondo animato
        radius = 80 + int(10 * math.sin(pygame.time.get_ticks() / 100))
        pygame.draw.circle(self.screen, COLORS['secondary'], pos, radius)
        pygame.draw.circle(self.screen, COLORS['white'], pos, radius, width=4)
        
        # Numero
        self.draw_text(str(number), pos, 'title', COLORS['white'], center=True, shadow=True)
    
    def draw_result_banner(self,
                           result: str,
                           player_move: str,
                           cpu_move: str,
                           center_y: int):
        """
        Disegna il banner con il risultato del round.
        
        Args:
            result: 'player', 'cpu', o 'draw'
            player_move: Mossa del giocatore
            cpu_move: Mossa della CPU
            center_y: Posizione Y centrale
        """
        # Colore basato sul risultato
        if result == 'player':
            bg_color = COLORS['success']
            text = "HAI VINTO!"
        elif result == 'cpu':
            bg_color = COLORS['danger']
            text = "HAI PERSO!"
        else:
            bg_color = COLORS['secondary']
            text = "PAREGGIO!"
        
        # Banner
        banner_rect = pygame.Rect(0, center_y - 40, self.width, 80)
        pygame.draw.rect(self.screen, bg_color, banner_rect)
        
        # Testo risultato
        self.draw_text(text, (self.width // 2, center_y), 'large', COLORS['white'], center=True, shadow=True)
        
        # Mosse
        move_names = {
            'rock': 'Sasso',
            'paper': 'Carta',
            'scissors': 'Forbice'
        }
        
        moves_text = f"Tu: {move_names.get(player_move, '?')} vs CPU: {move_names.get(cpu_move, '?')}"
        self.draw_text(moves_text, (self.width // 2, center_y + 50), 'small', COLORS['white'], center=True)
    
    def draw_highscore_table(self,
                             scores: List[dict],
                             pos: Tuple[int, int],
                             highlight_index: int = -1):
        """
        Disegna la tabella dei punteggi.
        
        Args:
            scores: Lista di dizionari con punteggi
            pos: Posizione in alto a sinistra
            highlight_index: Indice da evidenziare
        """
        x, y = pos
        row_height = 40
        
        # Intestazione
        self.draw_text("#", (x, y), 'medium', COLORS['secondary'])
        self.draw_text("NOME", (x + 60, y), 'medium', COLORS['secondary'])
        self.draw_text("PUNTI", (x + 200, y), 'medium', COLORS['secondary'])
        
        y += row_height + 10
        pygame.draw.line(self.screen, COLORS['gray'], (x, y - 5), (x + 300, y - 5), 2)
        
        # Righe
        for i, score in enumerate(scores):
            color = COLORS['secondary'] if i == highlight_index else COLORS['white']
            bg_color = COLORS['dark_gray'] if i == highlight_index else None
            
            if bg_color:
                row_rect = pygame.Rect(x - 10, y - 5, 320, row_height)
                pygame.draw.rect(self.screen, bg_color, row_rect, border_radius=5)
            
            self.draw_text(f"{i + 1}.", (x, y), 'small', color)
            self.draw_text(score.get('name', '???'), (x + 60, y), 'small', color)
            self.draw_text(str(score.get('score', 0)), (x + 200, y), 'small', color)
            
            y += row_height
    
    def draw_name_input(self,
                        current_name: str,
                        pos: Tuple[int, int],
                        cursor_visible: bool = True):
        """
        Disegna il campo di input per il nome.
        
        Args:
            current_name: Nome corrente (max 3 caratteri)
            pos: Posizione centrale
            cursor_visible: Se mostrare il cursore
        """
        # Sfondo
        input_rect = pygame.Rect(0, 0, 200, 80)
        input_rect.center = pos
        pygame.draw.rect(self.screen, COLORS['dark_gray'], input_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['primary'], input_rect, width=3, border_radius=10)
        
        # Caratteri
        chars = list(current_name.ljust(3, '_'))
        char_width = 50
        start_x = pos[0] - char_width
        
        for i, char in enumerate(chars):
            char_x = start_x + i * char_width
            char_color = COLORS['white'] if char != '_' else COLORS['gray']
            self.draw_text(char, (char_x, pos[1]), 'large', char_color, center=True)
            
            # Sottolineatura
            pygame.draw.line(
                self.screen, 
                COLORS['primary'],
                (char_x - 15, pos[1] + 30),
                (char_x + 15, pos[1] + 30),
                3
            )
        
        # Cursore lampeggiante
        if cursor_visible and len(current_name) < 3:
            cursor_x = start_x + len(current_name) * char_width
            pygame.draw.line(
                self.screen,
                COLORS['white'],
                (cursor_x, pos[1] - 20),
                (cursor_x, pos[1] + 20),
                2
            )
    
    def draw_gesture_indicator(self,
                               gesture: str,
                               confidence: float,
                               pos: Tuple[int, int]):
        """
        Disegna l'indicatore del gesto rilevato.
        
        Args:
            gesture: Nome del gesto
            confidence: Confidenza del riconoscimento (0-1)
            pos: Posizione
        """
        gesture_names = {
            'rock': 'Sasso ✊',
            'paper': 'Carta ✋',
            'scissors': 'Forbice ✌️',
            'ok': 'OK 👌',
            'point_up': 'Su 👆',
            'point_down': 'Giù 👇',
            'none': 'Nessun gesto'
        }
        
        text = gesture_names.get(gesture, gesture)
        color = COLORS['success'] if confidence > 0.7 else COLORS['secondary']
        
        self.draw_text(text, pos, 'small', color, center=True)
