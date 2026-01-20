"""
Modulo di rendering grafico per il gioco
"""

import pygame
import numpy as np
import cv2
from typing import Tuple, Optional, List
import math
import random

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT


class Particle:
    """Classe per gestire particelle di effetto."""
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 lifetime: float, color: Tuple[int, int, int], size: int = 4):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.gravity = 0.2
    
    def update(self, dt: float):
        """Aggiorna la particella."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity
        self.lifetime -= dt
    
    def is_alive(self) -> bool:
        """Verifica se la particella e' ancora viva."""
        return self.lifetime > 0
    
    def get_alpha(self) -> float:
        """Restituisce l'alpha (opacita') basato sulla vita rimanente."""
        return max(0, self.lifetime / self.max_lifetime)


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
        
        # Sistema di particelle
        self.particles: List[Particle] = []
        
        # Effetti schermo (transizioni, flash, ecc.)
        self.screen_overlay_alpha = 0
        self.screen_overlay_color = (0, 0, 0)
    
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
                       color: Tuple[int, int, int] = None,
                       background: bool = True):
        """
        Disegna l'icona di una mossa.
        
        Args:
            move: 'rock', 'paper', o 'scissors'
            pos: Posizione centrale
            size: Dimensione dell'icona
            color: Colore dell'icona
            background: Se True disegna il cerchio di sfondo (default True)
        """
        if color is None:
            color_map = {
                'rock': COLORS['rock'],
                'paper': COLORS['paper'],
                'scissors': COLORS['scissors']
            }
            color = color_map.get(move, COLORS['white'])
        
        # Cerchio di sfondo opzionale
        if background:
            pygame.draw.circle(self.screen, COLORS['dark_gray'], pos, size // 2)
            pygame.draw.circle(self.screen, color, pos, size // 2, width=4)
        
        # Simbolo testuale della mossa
        symbols = {
            'rock': 'SASSO',
            'paper': 'CARTA',
            'scissors': 'FORBICE'
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
    
    def draw_result_banner_improved(self,
                                    result: str,
                                    player_move: str,
                                    cpu_move: str,
                                    center_y: int):
        """
        Disegna un banner migliorato con il risultato del round.
        
        Args:
            result: 'player', 'cpu', o 'draw'
            player_move: Mossa del giocatore
            cpu_move: Mossa della CPU
            center_y: Posizione Y centrale
        """
        # Colore e testo basati sul risultato
        if result == 'player':
            bg_color = COLORS['success']
            text = "[OK] HAI VINTO IL ROUND!"
            explanation = self._get_win_explanation(player_move, cpu_move)
        elif result == 'cpu':
            bg_color = COLORS['danger']
            text = "[NO] HAI PERSO IL ROUND!"
            explanation = self._get_lose_explanation(player_move, cpu_move)
        else:
            bg_color = COLORS['secondary']
            text = "> PAREGGIO!"
            explanation = "Stessa mossa - Si ripete!"
        
        # Banner con sfondo
        banner_rect = pygame.Rect(0, center_y - 50, self.width, 100)
        pygame.draw.rect(self.screen, bg_color, banner_rect)
        
        # Bordo luminoso
        pygame.draw.rect(self.screen, COLORS['white'], banner_rect, width=2)
        
        # Testo risultato principale
        self.draw_text(text, (self.width // 2, center_y - 20), 'large', COLORS['white'], center=True, shadow=True)
        
        # Spiegazione del risultato
        self.draw_text(explanation, (self.width // 2, center_y + 25), 'small', COLORS['white'], center=True)
    
    def _get_win_explanation(self, player_move: str, cpu_move: str) -> str:
        """Restituisce la spiegazione della vittoria."""
        explanations = {
            ('rock', 'scissors'): "Sasso spacca Forbice!",
            ('scissors', 'paper'): "Forbice taglia Carta!",
            ('paper', 'rock'): "Carta avvolge Sasso!"
        }
        return explanations.get((player_move, cpu_move), "")
    
    def _get_lose_explanation(self, player_move: str, cpu_move: str) -> str:
        """Restituisce la spiegazione della sconfitta."""
        explanations = {
            ('scissors', 'rock'): "Sasso spacca Forbice!",
            ('paper', 'scissors'): "Forbice taglia Carta!",
            ('rock', 'paper'): "Carta avvolge Sasso!"
        }
        return explanations.get((player_move, cpu_move), "")
    
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
    
    def draw_highscore_table_improved(self,
                                      scores: List[dict],
                                      pos: Tuple[int, int],
                                      highlight_index: int = -1):
        """
        Disegna una tabella punteggi migliorata e centrata.
        
        Args:
            scores: Lista di dizionari con punteggi
            pos: Posizione centrale orizzontale e Y iniziale
            highlight_index: Indice da evidenziare
        """
        center_x, start_y = pos
        table_width = 400
        row_height = 38
        
        # Sfondo tabella (altezza dinamica in base al numero di righe)
        table_height = max(1, len(scores)) * row_height + 50
        table_rect = pygame.Rect(center_x - table_width // 2, start_y - 10, table_width, table_height)
        pygame.draw.rect(self.screen, COLORS['dark_gray'], table_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLORS['primary'], table_rect, width=2, border_radius=10)
        
        # Intestazione
        header_y = start_y + 10
        self.draw_text("#", (center_x - 150, header_y), 'small', COLORS['secondary'], center=True)
        self.draw_text("NOME", (center_x - 50, header_y), 'small', COLORS['secondary'], center=True)
        self.draw_text("VITTORIE", (center_x + 80, header_y), 'small', COLORS['secondary'], center=True)
        self.draw_text("DATA", (center_x + 170, header_y), 'tiny', COLORS['secondary'], center=True)
        
        # Linea separatrice
        pygame.draw.line(
            self.screen, COLORS['gray'],
            (center_x - table_width // 2 + 10, header_y + 20),
            (center_x + table_width // 2 - 10, header_y + 20), 1
        )
        
        # Righe punteggi
        y = header_y + 35
        for i, score in enumerate(scores):
            # Colore basato sulla posizione
            if i == 0:
                rank_color = (255, 215, 0)  # Oro
                rank_text = "1."
            elif i == 1:
                rank_color = (192, 192, 192)  # Argento
                rank_text = "2."
            elif i == 2:
                rank_color = (205, 127, 50)  # Bronzo
                rank_text = "3."
            else:
                rank_color = COLORS['white']
                rank_text = f"{i + 1}."
            
            # Evidenzia riga se richiesto
            if i == highlight_index:
                row_rect = pygame.Rect(center_x - table_width // 2 + 5, y - 8, table_width - 10, row_height - 2)
                pygame.draw.rect(self.screen, COLORS['success'], row_rect, border_radius=5)
            
            # Posizione
            self.draw_text(rank_text, (center_x - 150, y), 'small', rank_color, center=True)
            
            # Nome
            name = score.get('name', '???')
            self.draw_text(name, (center_x - 50, y), 'small', COLORS['white'], center=True)
            
            # Punteggio (vittorie consecutive)
            score_val = score.get('score', 0)
            self.draw_text(str(score_val), (center_x + 80, y), 'small', COLORS['success'], center=True)
            
            # Data (formattata)
            date_str = score.get('date', '')
            if date_str:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(date_str)
                    date_display = date_obj.strftime("%d/%m")
                except:
                    date_display = "-"
            else:
                date_display = "-"
            self.draw_text(date_display, (center_x + 170, y), 'tiny', COLORS['gray'], center=True)
            
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
            'rock': 'Sasso (S)',
            'paper': 'Carta (C)',
            'scissors': 'Forbice (F)',
            'point_down': 'Giu',
            'none': 'Nessun gesto'
        }
        
        text = gesture_names.get(gesture, gesture)
        color = COLORS['success'] if confidence > 0.7 else COLORS['secondary']
        
        self.draw_text(text, pos, 'small', color, center=True)
    
    def emit_particles(self, 
                      x: float, y: float, 
                      count: int = 10,
                      velocity_range: float = 5.0,
                      color: Tuple[int, int, int] = None,
                      lifetime: float = 1.0):
        """
        Emette particelle da una posizione.
        
        Args:
            x: Posizione X
            y: Posizione Y
            count: Numero di particelle
            velocity_range: Intervallo di velocita'
            color: Colore delle particelle
            lifetime: Durata della vita
        """
        if color is None:
            color = COLORS['primary']
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(0, velocity_range)
            vx = velocity * math.cos(angle)
            vy = velocity * math.sin(angle)
            
            particle = Particle(x, y, vx, vy, lifetime, color)
            self.particles.append(particle)
    
    def update_particles(self, dt: float):
        """Aggiorna tutte le particelle."""
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Disegna tutte le particelle attive."""
        for particle in self.particles:
            if particle.is_alive():
                # Calcola il colore con alpha
                alpha = particle.get_alpha()
                color = tuple(int(c * alpha) for c in particle.color)
                
                # Disegna cerchio con dimensione che diminuisce
                size = max(1, int(particle.size * alpha))
                pygame.draw.circle(self.screen, color, 
                                 (int(particle.x), int(particle.y)), size)
    
    def draw_glowing_button(self,
                           text: str,
                           pos: Tuple[int, int],
                           size: Tuple[int, int] = (200, 50),
                           selected: bool = False,
                           glow_intensity: float = 0.0) -> pygame.Rect:
        """
        Disegna un pulsante con effetto glow.
        
        Args:
            text: Testo del pulsante
            pos: Posizione centrale
            size: Dimensioni
            selected: Se evidenziato
            glow_intensity: Intensita' del glow (0-1)
        """
        if selected:
            color = COLORS['primary']
        else:
            color = COLORS['dark_gray']
        
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Effetto glow
        if glow_intensity > 0:
            glow_surf = pygame.Surface((size[0] + 20, size[1] + 20), pygame.SRCALPHA)
            glow_color = (*COLORS['primary'], int(100 * glow_intensity))
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=10)
            glow_rect = glow_surf.get_rect(center=pos)
            self.screen.blit(glow_surf, glow_rect)
        
        # Sfondo
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        
        # Bordo
        border_color = COLORS['white'] if selected else COLORS['gray']
        pygame.draw.rect(self.screen, border_color, rect, width=3, border_radius=10)
        
        # Testo
        self.draw_text(text, pos, 'medium', COLORS['white'], center=True)
        
        return rect
    
    def draw_move_icon_enhanced(self,
                               move: str,
                               pos: Tuple[int, int],
                               size: int = 100,
                               color: Tuple[int, int, int] = None,
                               background: bool = True,
                               scale: float = 1.0):
        """
        Disegna l'icona di una mossa con rendering migliorato.
        
        Args:
            move: 'rock', 'paper', o 'scissors'
            pos: Posizione centrale
            size: Dimensione dell'icona
            color: Colore dell'icona
            background: Se True disegna il cerchio di sfondo
            scale: Fattore di scala per animazioni
        """
        if color is None:
            color_map = {
                'rock': COLORS['rock'],
                'paper': COLORS['paper'],
                'scissors': COLORS['scissors']
            }
            color = color_map.get(move, COLORS['white'])
        
        scaled_size = int(size * scale)
        
        # Cerchio di sfondo opzionale
        if background:
            # Ombra
            pygame.draw.circle(self.screen, (0, 0, 0), pos, scaled_size // 2 + 3, width=0)
            pygame.draw.circle(self.screen, COLORS['dark_gray'], pos, scaled_size // 2)
            pygame.draw.circle(self.screen, color, pos, scaled_size // 2, width=4)
        
        # Simbolo con emoji-like
        symbols = {
            'rock': '[R]',
            'paper': '[P]',
            'scissors': '[S]'
        }
        
        # Fallback a testo se emoji non supportate
        if move == 'rock':
            self._draw_rock(pos, scaled_size // 2 - 10, COLORS['white'])
        elif move == 'paper':
            self._draw_paper(pos, scaled_size // 2 - 10, COLORS['white'])
        elif move == 'scissors':
            self._draw_scissors(pos, scaled_size // 2 - 10, COLORS['white'])
    
    def _draw_rock(self, pos: Tuple[int, int], size: int, color: Tuple[int, int, int]):
        """Disegna l'icona di un sasso."""
        # Forma approssimativa irregolare
        points = [
            (pos[0] - size//2, pos[1] - size//3),
            (pos[0] - size//3, pos[1] - size//2),
            (pos[0] + size//2, pos[1] - size//3),
            (pos[0] + size//2, pos[1] + size//2),
            (pos[0] - size//2, pos[1] + size//3),
        ]
        if len(points) >= 3:
            pygame.draw.polygon(self.screen, color, points)
    
    def _draw_paper(self, pos: Tuple[int, int], size: int, color: Tuple[int, int, int]):
        """Disegna l'icona di una carta."""
        rect = pygame.Rect(pos[0] - size//2, pos[1] - size//2, size, size * 1.3)
        pygame.draw.rect(self.screen, color, rect)
        # Linee di testo sulla carta
        for i in range(3):
            y = pos[1] - size//3 + i * size//3
            pygame.draw.line(self.screen, COLORS['background'], 
                           (pos[0] - size//3, y), (pos[0] + size//3, y), 2)
    
    def _draw_scissors(self, pos: Tuple[int, int], size: int, color: Tuple[int, int, int]):
        """Disegna l'icona di forbici."""
        # Due cerchi per i buchi
        circle_offset = size // 4
        pygame.draw.circle(self.screen, COLORS['background'], 
                         (pos[0] - circle_offset, pos[1] - circle_offset), 3)
        pygame.draw.circle(self.screen, COLORS['background'], 
                         (pos[0] + circle_offset, pos[1] + circle_offset), 3)
        # Due linee a forma di X
        pygame.draw.line(self.screen, color,
                        (pos[0] - size//2, pos[1] - size//2),
                        (pos[0] + size//2, pos[1] + size//2), 4)
        pygame.draw.line(self.screen, color,
                        (pos[0] + size//2, pos[1] - size//2),
                        (pos[0] - size//2, pos[1] + size//2), 4)
    
    def draw_round_badge(self,
                        round_num: int,
                        pos: Tuple[int, int],
                        color: Tuple[int, int, int] = None):
        """
        Disegna un badge esagonale con il numero del round.
        
        Args:
            round_num: Numero del round
            pos: Posizione centrale
            color: Colore del badge
        """
        if color is None:
            color = COLORS['primary']
        
        radius = 40
        
        # Esagono
        angles = [i * math.pi / 3 for i in range(6)]
        points = [(pos[0] + radius * math.cos(a), pos[1] + radius * math.sin(a)) 
                 for a in angles]
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, COLORS['white'], points, width=2)
        
        # Testo
        self.draw_text(str(round_num), pos, 'large', COLORS['white'], center=True)
    
    def draw_gradient_rect(self,
                          rect: pygame.Rect,
                          color_top: Tuple[int, int, int],
                          color_bottom: Tuple[int, int, int]):
        """
        Disegna un rettangolo con gradiente verticale.
        
        Args:
            rect: Rettangolo da riempire
            color_top: Colore in alto
            color_bottom: Colore in basso
        """
        for y in range(rect.height):
            ratio = y / max(1, rect.height)
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), 
                           (rect.left, rect.top + y), 
                           (rect.right, rect.top + y))
    
    def draw_pulse_circle(self,
                         pos: Tuple[int, int],
                         radius: int,
                         color: Tuple[int, int, int],
                         time: float):
        """
        Disegna un cerchio con effetto pulsante.
        
        Args:
            pos: Posizione centrale
            radius: Raggio base
            color: Colore
            time: Tempo per l'animazione
        """
        pulsation = 1.0 + 0.3 * math.sin(time * 6)
        actual_radius = int(radius * pulsation)
        pygame.draw.circle(self.screen, color, pos, actual_radius)
        
        # Bordo esterno che svanisce
        fade_radius = int(radius * (1.5 + 0.2 * math.sin(time * 6)))
        fade_color = tuple(int(c * 0.3) for c in color)
        pygame.draw.circle(self.screen, fade_color, pos, fade_radius, width=2)
    
    def apply_screen_overlay(self, dt: float):
        """Applica l'overlay dello schermo e aggiorna l'alpha."""
        if self.screen_overlay_alpha > 0:
            overlay = pygame.Surface((self.width, self.height))
            overlay.fill(self.screen_overlay_color)
            overlay.set_alpha(int(self.screen_overlay_alpha))
            self.screen.blit(overlay, (0, 0))
            # Fade out graduale
            self.screen_overlay_alpha = max(0, self.screen_overlay_alpha - 2.0 * dt)
    
    def flash_screen(self, color: Tuple[int, int, int] = None, duration: float = 0.2):
        """
        Fa lampeggiare lo schermo.
        
        Args:
            color: Colore del flash
            duration: Durata del flash
        """
        if color is None:
            color = COLORS['white']
        self.screen_overlay_color = color
        self.screen_overlay_alpha = 255

