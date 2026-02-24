"""
Modulo di rendering grafico per il gioco - Design Moderno Gaming
"""

import pygame
import numpy as np
import cv2
from typing import Tuple, Optional, List
import math
import random

from config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, UI_SYMBOLS


class Particle:
    """Classe per gestire particelle di effetto."""
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 lifetime: float, color: Tuple[int, int, int], size: int = 4,
                 particle_type: str = 'circle'):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.gravity = 0.15
        self.particle_type = particle_type
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-5, 5)
    
    def update(self, dt: float):
        """Aggiorna la particella."""
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravity
        self.lifetime -= dt
        self.rotation += self.rotation_speed
    
    def is_alive(self) -> bool:
        """Verifica se la particella e' ancora viva."""
        return self.lifetime > 0
    
    def get_alpha(self) -> float:
        """Restituisce l'alpha (opacita') basato sulla vita rimanente."""
        return max(0, min(1, self.lifetime / self.max_lifetime))


class Renderer:
    """
    Classe per il rendering dell'interfaccia grafica del gioco.
    Design moderno con effetti gaming.
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
        
        # Carica i font - Stile moderno
        pygame.font.init()
        self.fonts = {
            'hero': pygame.font.Font(None, 96),       # Titoli grandi
            'title': pygame.font.Font(None, 72),      # Titoli
            'large': pygame.font.Font(None, 52),      # Sottotitoli
            'medium': pygame.font.Font(None, 38),     # Testo normale
            'small': pygame.font.Font(None, 28),      # Testo piccolo
            'tiny': pygame.font.Font(None, 22),       # Testo molto piccolo
            'micro': pygame.font.Font(None, 18),      # Micro testo
        }
        
        # Font emoji (per simboli)
        try:
            self.emoji_font = pygame.font.Font(None, 64)
        except:
            self.emoji_font = self.fonts['title']
        
        # Cache per superfici pre-renderizzate
        self._cache = {}
        
        # Sistema di particelle
        self.particles: List[Particle] = []
        
        # Effetti schermo
        self.screen_overlay_alpha = 0
        self.screen_overlay_color = (0, 0, 0)
        
        # Animazione globale
        self.global_time = 0
        
        # Pre-render di alcune superfici
        self._init_surfaces()
    
    def _init_surfaces(self):
        """Inizializza superfici pre-renderizzate."""
        # Superficie per glow effect
        self.glow_surface = pygame.Surface((200, 200), pygame.SRCALPHA)
        
    def update_time(self, dt: float):
        """Aggiorna il tempo globale per animazioni."""
        self.global_time += dt
    
    def clear(self, color: Tuple[int, int, int] = None):
        """Pulisce lo schermo con gradiente."""
        if color is None:
            self.draw_background_gradient()
        else:
            self.screen.fill(color)
    
    def draw_background_gradient(self):
        """Disegna lo sfondo con gradiente moderno."""
        top = COLORS['bg_gradient_top']
        bottom = COLORS['bg_gradient_bottom']
        
        for y in range(self.height):
            ratio = y / self.height
            # Ease in-out per transizione più smooth
            ratio = ratio * ratio * (3 - 2 * ratio)
            r = int(top[0] * (1 - ratio) + bottom[0] * ratio)
            g = int(top[1] * (1 - ratio) + bottom[1] * ratio)
            b = int(top[2] * (1 - ratio) + bottom[2] * ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.width, y))
        
        # Aggiungi pattern decorativo sottile
        self._draw_bg_pattern()
    
    def _draw_bg_pattern(self):
        """Disegna pattern decorativo sullo sfondo."""
        # Cerchi decorativi sfumati agli angoli
        patterns = [
            (50, 50, COLORS['primary'], 0.03),
            (self.width - 50, 50, COLORS['accent'], 0.02),
            (50, self.height - 50, COLORS['secondary'], 0.02),
            (self.width - 50, self.height - 50, COLORS['primary'], 0.03),
        ]
        
        for x, y, color, alpha in patterns:
            pulse = 0.5 + 0.5 * math.sin(self.global_time * 0.5 + x * 0.01)
            radius = int(80 + 20 * pulse)
            surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            for r in range(radius, 0, -2):
                a = int(255 * alpha * (r / radius))
                pygame.draw.circle(surf, (*color, a), (radius, radius), r)
            self.screen.blit(surf, (x - radius, y - radius))
    
    def draw_text(self, 
                  text: str, 
                  pos: Tuple[int, int], 
                  font_size: str = 'medium',
                  color: Tuple[int, int, int] = None,
                  center: bool = False,
                  shadow: bool = False,
                  glow: bool = False,
                  glow_color: Tuple[int, int, int] = None) -> pygame.Rect:
        """
        Disegna testo con effetti moderni.
        """
        if color is None:
            color = COLORS['white']
        
        font = self.fonts.get(font_size, self.fonts['medium'])
        
        # Effetto glow
        if glow:
            gc = glow_color if glow_color else color
            glow_surf = font.render(text, True, gc)
            for offset in [(2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                glow_rect = glow_surf.get_rect()
                if center:
                    glow_rect.center = (pos[0] + offset[0], pos[1] + offset[1])
                else:
                    glow_rect.topleft = (pos[0] + offset[0], pos[1] + offset[1])
                glow_surf.set_alpha(60)
                self.screen.blit(glow_surf, glow_rect)
        
        # Ombra
        if shadow:
            shadow_surf = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect()
            if center:
                shadow_rect.center = (pos[0] + 3, pos[1] + 3)
            else:
                shadow_rect.topleft = (pos[0] + 3, pos[1] + 3)
            shadow_surf.set_alpha(100)
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
    
    def draw_card(self,
                  pos: Tuple[int, int],
                  size: Tuple[int, int],
                  selected: bool = False,
                  glow_color: Tuple[int, int, int] = None,
                  border_radius: int = 15) -> pygame.Rect:
        """
        Disegna una card moderna con effetti.
        """
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Glow effect se selezionato
        if selected and glow_color:
            glow_rect = rect.inflate(10, 10)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pulse = 0.6 + 0.4 * math.sin(self.global_time * 4)
            pygame.draw.rect(glow_surf, (*glow_color, int(80 * pulse)), 
                           glow_surf.get_rect(), border_radius=border_radius + 5)
            self.screen.blit(glow_surf, glow_rect)
        
        # Sfondo card
        bg_color = COLORS['card_bg_light'] if selected else COLORS['card_bg']
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=border_radius)
        
        # Bordo
        border_color = glow_color if (selected and glow_color) else COLORS['dark_gray']
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=border_radius)
        
        # Highlight top (effetto 3D)
        if selected:
            highlight_rect = pygame.Rect(rect.left + 2, rect.top + 2, rect.width - 4, 3)
            pygame.draw.rect(self.screen, (*COLORS['white'], 30), highlight_rect, border_radius=2)
        
        return rect
    
    def draw_modern_button(self,
                           text: str,
                           pos: Tuple[int, int],
                           size: Tuple[int, int] = (220, 55),
                           selected: bool = False,
                           color: Tuple[int, int, int] = None,
                           icon: str = None) -> pygame.Rect:
        """
        Disegna un pulsante moderno con effetti gaming.
        """
        if color is None:
            color = COLORS['primary']
        
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Effetto glow quando selezionato
        if selected:
            pulse = 0.5 + 0.5 * math.sin(self.global_time * 5)
            glow_rect = rect.inflate(12, 12)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, int(100 * pulse)), 
                           glow_surf.get_rect(), border_radius=18)
            self.screen.blit(glow_surf, glow_rect)
        
        # Sfondo gradiente
        if selected:
            bg_color = color
        else:
            bg_color = COLORS['button_bg']
        
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=12)
        
        # Bordo luminoso
        border_color = COLORS['primary_light'] if selected else COLORS['muted']
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=12)
        
        # Highlight top
        highlight = pygame.Rect(rect.left + 4, rect.top + 4, rect.width - 8, 2)
        highlight_color = (*COLORS['white'], 60) if selected else (*COLORS['white'], 20)
        pygame.draw.rect(self.screen, highlight_color[:3], highlight, border_radius=1)
        
        # Icona + Testo
        text_x = pos[0]
        if icon:
            icon_offset = -20
            self.draw_text(icon, (pos[0] + icon_offset - 30, pos[1]), 'medium', COLORS['white'], center=True)
            text_x = pos[0] + 10
        
        text_color = COLORS['white'] if selected else COLORS['light_gray']
        self.draw_text(text, (text_x, pos[1]), 'medium', text_color, center=True)
        
        return rect
    
    def draw_glowing_button(self,
                           text: str,
                           pos: Tuple[int, int],
                           size: Tuple[int, int] = (200, 50),
                           selected: bool = False,
                           glow_intensity: float = 0.0) -> pygame.Rect:
        """Wrapper per compatibilità - usa draw_modern_button."""
        return self.draw_modern_button(text, pos, size, selected)
    
    def draw_button(self,
                    text: str,
                    pos: Tuple[int, int],
                    size: Tuple[int, int] = (200, 50),
                    selected: bool = False,
                    color: Tuple[int, int, int] = None) -> pygame.Rect:
        """Wrapper per compatibilità."""
        return self.draw_modern_button(text, pos, size, selected, color)
    
    def draw_camera_feed(self, 
                         frame: np.ndarray, 
                         pos: Tuple[int, int],
                         size: Tuple[int, int] = (320, 240),
                         border_color: Tuple[int, int, int] = None,
                         corner_style: bool = True):
        """
        Disegna il feed della camera con stile moderno.
        """
        if frame is None:
            self._draw_camera_placeholder(pos, size)
            return
        
        # Ridimensiona il frame
        frame_resized = cv2.resize(frame, size)
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
        frame_rotated = np.rot90(frame_rgb)
        frame_rotated = np.flipud(frame_rotated)
        
        # Crea superficie Pygame
        surf = pygame.surfarray.make_surface(frame_rotated)
        rect = surf.get_rect(center=pos)
        
        # Sfondo con padding
        bg_rect = rect.inflate(8, 8)
        pygame.draw.rect(self.screen, COLORS['card_bg'], bg_rect, border_radius=12)
        
        # Bordo stilizzato
        if border_color is None:
            border_color = COLORS['primary']
        pygame.draw.rect(self.screen, border_color, bg_rect, width=2, border_radius=12)
        
        # Angoli decorativi
        if corner_style:
            self._draw_corner_decorations(bg_rect, border_color)
        
        self.screen.blit(surf, rect)
    
    def _draw_camera_placeholder(self, pos: Tuple[int, int], size: Tuple[int, int]):
        """Disegna placeholder quando la camera non è disponibile."""
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Sfondo scuro
        pygame.draw.rect(self.screen, COLORS['card_bg'], rect, border_radius=10)
        
        # Bordo pulsante
        pulse = 0.5 + 0.5 * math.sin(self.global_time * 3)
        border_color = tuple(int(c * pulse) for c in COLORS['warning'])
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=10)
        
        # Icona camera
        self.draw_text("CAM", (pos[0], pos[1] - 10), 'large', COLORS['muted'], center=True)
        self.draw_text("Non connessa", (pos[0], pos[1] + 30), 'tiny', COLORS['muted'], center=True)
    
    def _draw_corner_decorations(self, rect: pygame.Rect, color: Tuple[int, int, int]):
        """Disegna decorazioni agli angoli in stile tech."""
        corner_size = 15
        thickness = 2
        
        corners = [
            (rect.topleft, (1, 0), (0, 1)),
            (rect.topright, (-1, 0), (0, 1)),
            (rect.bottomleft, (1, 0), (0, -1)),
            (rect.bottomright, (-1, 0), (0, -1)),
        ]
        
        for start, dir1, dir2 in corners:
            p1 = (start[0] + dir1[0] * corner_size, start[1] + dir1[1] * corner_size)
            p2 = (start[0] + dir2[0] * corner_size, start[1] + dir2[1] * corner_size)
            pygame.draw.line(self.screen, color, start, p1, thickness)
            pygame.draw.line(self.screen, color, start, p2, thickness)
    
    def draw_progress_bar(self,
                          pos: Tuple[int, int],
                          size: Tuple[int, int],
                          progress: float,
                          color: Tuple[int, int, int] = None,
                          bg_color: Tuple[int, int, int] = None,
                          show_glow: bool = True):
        """
        Disegna una barra di progresso moderna.
        """
        if color is None:
            color = COLORS['primary']
        if bg_color is None:
            bg_color = COLORS['progress_bg']
        
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Sfondo
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=size[1] // 2)
        
        # Bordo sottile
        pygame.draw.rect(self.screen, COLORS['muted'], rect, width=1, border_radius=size[1] // 2)
        
        # Progresso
        progress = max(0, min(1, progress))
        if progress > 0:
            progress_width = int((size[0] - 4) * progress)
            progress_rect = pygame.Rect(rect.left + 2, rect.top + 2, progress_width, size[1] - 4)
            
            # Glow effect
            if show_glow:
                glow_rect = progress_rect.inflate(4, 4)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*color, 80), glow_surf.get_rect(), 
                               border_radius=(size[1] - 4) // 2)
                self.screen.blit(glow_surf, glow_rect)
            
            pygame.draw.rect(self.screen, color, progress_rect, border_radius=(size[1] - 4) // 2)
            
            # Shine effect
            shine_rect = pygame.Rect(progress_rect.left, progress_rect.top, 
                                    progress_rect.width, progress_rect.height // 3)
            shine_surf = pygame.Surface((shine_rect.width, shine_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shine_surf, (*COLORS['white'], 40), shine_surf.get_rect(), 
                           border_radius=2)
            self.screen.blit(shine_surf, shine_rect)
    
    def draw_timer_bar(self,
                       pos: Tuple[int, int],
                       size: Tuple[int, int],
                       progress: float):
        """
        Disegna barra timer con colori dinamici.
        """
        if progress > 0.5:
            color = COLORS['timer_safe']
        elif progress > 0.25:
            color = COLORS['timer_warning']
        else:
            color = COLORS['timer_critical']
            # Effetto pulsante quando critico
            pulse = 0.7 + 0.3 * math.sin(self.global_time * 10)
            color = tuple(int(c * pulse) for c in color)
        
        self.draw_progress_bar(pos, size, progress, color, show_glow=progress < 0.3)
    
    def draw_move_icon(self,
                       move: str,
                       pos: Tuple[int, int],
                       size: int = 100,
                       color: Tuple[int, int, int] = None,
                       background: bool = True,
                       animated: bool = True):
        """
        Disegna l'icona di una mossa con stile moderno.
        """
        move_data = {
            'rock': {'symbol': 'S', 'color': COLORS['rock'], 'bg': COLORS['rock_bg'], 'name': 'SASSO'},
            'paper': {'symbol': 'C', 'color': COLORS['paper'], 'bg': COLORS['paper_bg'], 'name': 'CARTA'},
            'scissors': {'symbol': 'F', 'color': COLORS['scissors'], 'bg': COLORS['scissors_bg'], 'name': 'FORBICE'}
        }
        
        data = move_data.get(move, {'symbol': '?', 'color': COLORS['gray'], 'bg': COLORS['dark_gray'], 'name': '?'})
        move_color = color if color else data['color']
        
        if background:
            # Cerchio di sfondo con glow
            if animated:
                pulse = 1.0 + 0.1 * math.sin(self.global_time * 3)
                glow_radius = int(size // 2 * pulse)
            else:
                glow_radius = size // 2
            
            # Glow esterno
            glow_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*move_color, 40), 
                             (size // 2 + 10, size // 2 + 10), glow_radius)
            self.screen.blit(glow_surf, (pos[0] - size // 2 - 10, pos[1] - size // 2 - 10))
            
            # Cerchio sfondo
            pygame.draw.circle(self.screen, data['bg'], pos, size // 2)
            pygame.draw.circle(self.screen, move_color, pos, size // 2, width=3)
        
        # Simbolo
        self.draw_text(data['symbol'], pos, 'title', COLORS['white'], center=True)
    
    def draw_move_icon_enhanced(self,
                               move: str,
                               pos: Tuple[int, int],
                               size: int = 100,
                               color: Tuple[int, int, int] = None,
                               background: bool = True,
                               scale: float = 1.0):
        """Alias per compatibilità."""
        self.draw_move_icon(move, pos, int(size * scale), color, background)
    
    def draw_score_panel(self,
                         player_score: int,
                         cpu_score: int,
                         pos: Tuple[int, int]):
        """
        Disegna il pannello punteggio moderno.
        """
        panel_width = 280
        panel_height = 60
        
        rect = pygame.Rect(0, 0, panel_width, panel_height)
        rect.center = pos
        
        # Sfondo con bordo
        pygame.draw.rect(self.screen, COLORS['card_bg'], rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['primary'], rect, width=2, border_radius=15)
        
        # Divisore centrale
        pygame.draw.line(self.screen, COLORS['muted'], 
                        (pos[0], rect.top + 10), (pos[0], rect.bottom - 10), 2)
        
        # Punteggio giocatore (sinistra)
        player_x = pos[0] - panel_width // 4
        self.draw_text("TU", (player_x, pos[1] - 12), 'tiny', COLORS['success'], center=True)
        self.draw_text(str(player_score), (player_x, pos[1] + 12), 'large', COLORS['white'], center=True)
        
        # Punteggio CPU (destra)
        cpu_x = pos[0] + panel_width // 4
        self.draw_text("CPU", (cpu_x, pos[1] - 12), 'tiny', COLORS['danger'], center=True)
        self.draw_text(str(cpu_score), (cpu_x, pos[1] + 12), 'large', COLORS['white'], center=True)
    
    def draw_score(self, player_score: int, cpu_score: int, pos: Tuple[int, int]):
        """Alias per compatibilità."""
        self.draw_score_panel(player_score, cpu_score, pos)
    
    def draw_countdown(self, number: int, pos: Tuple[int, int]):
        """
        Disegna il numero del countdown con effetto drammatico.
        """
        # Cerchio pulsante
        pulse = 1.0 + 0.15 * math.sin(self.global_time * 8)
        radius = int(70 * pulse)
        
        # Glow
        glow_surf = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*COLORS['secondary'], 60), 
                         (radius * 1.5, radius * 1.5), radius * 1.2)
        self.screen.blit(glow_surf, (pos[0] - radius * 1.5, pos[1] - radius * 1.5))
        
        # Cerchio principale
        pygame.draw.circle(self.screen, COLORS['secondary'], pos, radius)
        pygame.draw.circle(self.screen, COLORS['secondary_light'], pos, radius, width=4)
        
        # Numero
        self.draw_text(str(number), pos, 'hero', COLORS['white'], center=True, shadow=True)
    
    def draw_result_banner(self,
                           result: str,
                           player_move: str,
                           cpu_move: str,
                           center_y: int):
        """Disegna banner risultato semplice."""
        self.draw_result_banner_improved(result, player_move, cpu_move, center_y)
    
    def draw_result_banner_improved(self,
                                    result: str,
                                    player_move: str,
                                    cpu_move: str,
                                    center_y: int):
        """
        Disegna un banner risultato moderno e accattivante.
        """
        if result == 'player':
            bg_color = COLORS['success']
            text = "VITTORIA!"
            explanation = self._get_win_explanation(player_move, cpu_move)
        elif result == 'cpu':
            bg_color = COLORS['danger']
            text = "SCONFITTA"
            explanation = self._get_lose_explanation(player_move, cpu_move)
        else:
            bg_color = COLORS['warning']
            text = "PAREGGIO"
            explanation = "Stessa mossa!"
        
        # Banner con gradiente
        banner_rect = pygame.Rect(50, center_y - 40, self.width - 100, 80)
        
        # Sfondo con glow
        glow_rect = banner_rect.inflate(10, 10)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*bg_color, 100), glow_surf.get_rect(), border_radius=20)
        self.screen.blit(glow_surf, glow_rect)
        pygame.draw.rect(self.screen, bg_color, banner_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['white'], banner_rect, width=2, border_radius=15)
        
        # Testo
        self.draw_text(text, (self.width // 2, center_y - 10), 'large', COLORS['white'], center=True)
        self.draw_text(explanation, (self.width // 2, center_y + 25), 'small', COLORS['white'], center=True)
    
    def _get_win_explanation(self, player_move: str, cpu_move: str) -> str:
        explanations = {
            ('rock', 'scissors'): "Sasso spacca Forbice!",
            ('scissors', 'paper'): "Forbice taglia Carta!",
            ('paper', 'rock'): "Carta avvolge Sasso!"
        }
        return explanations.get((player_move, cpu_move), "")
    
    def _get_lose_explanation(self, player_move: str, cpu_move: str) -> str:
        explanations = {
            ('scissors', 'rock'): "Sasso spacca la tua Forbice!",
            ('paper', 'scissors'): "Forbice taglia la tua Carta!",
            ('rock', 'paper'): "Carta avvolge il tuo Sasso!"
        }
        return explanations.get((player_move, cpu_move), "")
    
    def draw_highscore_table(self,
                             scores: List[dict],
                             pos: Tuple[int, int],
                             highlight_index: int = -1):
        """Wrapper per compatibilità."""
        self.draw_highscore_table_improved(scores, pos, highlight_index)
    
    def draw_highscore_table_improved(self,
                                      scores: List[dict],
                                      pos: Tuple[int, int],
                                      highlight_index: int = -1):
        """
        Disegna una tabella punteggi moderna.
        """
        center_x, start_y = pos
        table_width = 450
        row_height = 42
        
        # Sfondo tabella
        table_height = max(1, len(scores)) * row_height + 55
        table_rect = pygame.Rect(center_x - table_width // 2, start_y - 10, table_width, table_height)
        pygame.draw.rect(self.screen, COLORS['card_bg'], table_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['primary'], table_rect, width=2, border_radius=15)
        
        # Header
        header_y = start_y + 12
        self.draw_text("#", (center_x - 180, header_y), 'small', COLORS['primary'], center=True)
        self.draw_text("GIOCATORE", (center_x - 70, header_y), 'small', COLORS['primary'], center=True)
        self.draw_text("VITTORIE", (center_x + 80, header_y), 'small', COLORS['primary'], center=True)
        self.draw_text("DATA", (center_x + 180, header_y), 'tiny', COLORS['primary'], center=True)
        
        # Linea separatrice
        pygame.draw.line(self.screen, COLORS['muted'],
                        (center_x - table_width // 2 + 15, header_y + 18),
                        (center_x + table_width // 2 - 15, header_y + 18), 1)
        
        # Righe
        y = header_y + 35
        medal_colors = [COLORS['gold'], COLORS['silver'], COLORS['bronze']]
        medals = ['1', '2', '3']
        
        for i, score in enumerate(scores):
            # Highlight riga
            if i == highlight_index:
                row_rect = pygame.Rect(center_x - table_width // 2 + 8, y - 10, table_width - 16, row_height - 4)
                pygame.draw.rect(self.screen, COLORS['success'], row_rect, border_radius=8)
            
            # Posizione con medaglia
            if i < 3:
                rank_text = medals[i]
                rank_color = medal_colors[i]
            else:
                rank_text = f"{i + 1}."
                rank_color = COLORS['white']
            
            self.draw_text(rank_text, (center_x - 180, y), 'small', rank_color, center=True)
            
            # Nome
            name = score.get('name', '???')
            self.draw_text(name, (center_x - 70, y), 'small', COLORS['white'], center=True)
            
            # Punteggio
            score_val = score.get('score', 0)
            self.draw_text(str(score_val), (center_x + 80, y), 'medium', COLORS['success'], center=True)
            
            # Data
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
            self.draw_text(date_display, (center_x + 180, y), 'tiny', COLORS['muted'], center=True)
            
            y += row_height
    
    def draw_name_input(self,
                        current_name: str,
                        pos: Tuple[int, int],
                        cursor_visible: bool = True):
        """
        Disegna il campo di input nome moderno.
        """
        # Box sfondo
        input_width = 280
        input_height = 80
        input_rect = pygame.Rect(0, 0, input_width, input_height)
        input_rect.center = pos
        
        pygame.draw.rect(self.screen, COLORS['input_bg'], input_rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['primary'], input_rect, width=3, border_radius=15)
        
        # Caratteri con slot
        chars = list(current_name.ljust(5, ' '))
        char_width = 45
        start_x = pos[0] - (char_width * 2.5) + char_width // 2
        
        for i, char in enumerate(chars):
            char_x = int(start_x + i * char_width)
            
            # Slot background
            slot_rect = pygame.Rect(char_x - 18, pos[1] - 20, 36, 50)
            slot_color = COLORS['primary'] if char != ' ' else COLORS['dark_gray']
            pygame.draw.rect(self.screen, slot_color, slot_rect, border_radius=8)
            
            # Carattere
            if char != ' ':
                self.draw_text(char, (char_x, pos[1]), 'large', COLORS['white'], center=True)
        
        # Cursore lampeggiante
        if cursor_visible and len(current_name) < 5:
            cursor_x = int(start_x + len(current_name) * char_width)
            cursor_rect = pygame.Rect(cursor_x - 2, pos[1] - 15, 4, 30)
            pygame.draw.rect(self.screen, COLORS['secondary'], cursor_rect)
    
    def draw_gesture_indicator(self,
                               gesture: str,
                               confidence: float,
                               pos: Tuple[int, int]):
        """
        Disegna l'indicatore del gesto rilevato.
        """
        gesture_names = {
            'rock': ('Sasso', COLORS['rock']),
            'paper': ('Carta', COLORS['paper']),
            'scissors': ('Forbice', COLORS['scissors']),
            'point_down': ('Giu', COLORS['muted']),
            'none': ('Nessuno', COLORS['muted'])
        }
        
        name, color = gesture_names.get(gesture, ('?', COLORS['gray']))
        
        # Box indicatore
        box_rect = pygame.Rect(pos[0] - 60, pos[1] - 15, 120, 30)
        pygame.draw.rect(self.screen, COLORS['card_bg'], box_rect, border_radius=8)
        pygame.draw.rect(self.screen, color, box_rect, width=2, border_radius=8)
        
        self.draw_text(name, pos, 'small', color, center=True)
    
    def emit_particles(self, 
                      x: float, y: float, 
                      count: int = 10,
                      velocity_range: float = 5.0,
                      color: Tuple[int, int, int] = None,
                      lifetime: float = 1.0):
        """
        Emette particelle da una posizione.
        """
        if color is None:
            color = COLORS['primary']
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            velocity = random.uniform(1, velocity_range)
            vx = velocity * math.cos(angle)
            vy = velocity * math.sin(angle) - 2  # Bias verso l'alto
            
            size = random.randint(3, 8)
            particle = Particle(x, y, vx, vy, lifetime, color, size)
            self.particles.append(particle)
    
    def emit_confetti(self, x: float, y: float, count: int = 30):
        """Emette coriandoli per celebrazioni."""
        colors = [COLORS['success'], COLORS['warning'], COLORS['primary'], 
                 COLORS['secondary'], COLORS['accent']]
        
        for _ in range(count):
            color = random.choice(colors)
            angle = random.uniform(-math.pi, 0)
            velocity = random.uniform(3, 8)
            vx = velocity * math.cos(angle)
            vy = velocity * math.sin(angle) - 3
            
            particle = Particle(x, y, vx, vy, 2.0, color, random.randint(4, 10), 'rect')
            particle.gravity = 0.1
            self.particles.append(particle)
    
    def update_particles(self, dt: float):
        """Aggiorna tutte le particelle."""
        self.update_time(dt)
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Disegna tutte le particelle attive."""
        for particle in self.particles:
            if particle.is_alive():
                alpha = particle.get_alpha()
                size = max(1, int(particle.size * alpha))
                color = tuple(int(c * alpha) for c in particle.color)
                
                if particle.particle_type == 'rect':
                    rect = pygame.Rect(int(particle.x) - size // 2, 
                                      int(particle.y) - size // 2, size, size)
                    pygame.draw.rect(self.screen, color, rect)
                else:
                    pygame.draw.circle(self.screen, color, 
                                     (int(particle.x), int(particle.y)), size)
    
    def draw_gradient_rect(self,
                          rect: pygame.Rect,
                          color_top: Tuple[int, int, int],
                          color_bottom: Tuple[int, int, int]):
        """
        Disegna un rettangolo con gradiente verticale.
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
        """
        pulsation = 1.0 + 0.2 * math.sin(time * 4)
        actual_radius = int(radius * pulsation)
        
        # Glow esterno
        glow_surf = pygame.Surface((actual_radius * 3, actual_radius * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*color, 40), 
                         (actual_radius * 1.5, actual_radius * 1.5), actual_radius * 1.3)
        self.screen.blit(glow_surf, (pos[0] - actual_radius * 1.5, pos[1] - actual_radius * 1.5))
        
        pygame.draw.circle(self.screen, color, pos, actual_radius)
    
    def apply_screen_overlay(self, dt: float):
        """Applica overlay e aggiorna alpha."""
        if self.screen_overlay_alpha > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((*self.screen_overlay_color, int(self.screen_overlay_alpha)))
            self.screen.blit(overlay, (0, 0))
            self.screen_overlay_alpha = max(0, self.screen_overlay_alpha - 400 * dt)
    
    def flash_screen(self, color: Tuple[int, int, int] = None, intensity: float = 200):
        """Fa lampeggiare lo schermo."""
        if color is None:
            color = COLORS['white']
        self.screen_overlay_color = color
        self.screen_overlay_alpha = intensity
    
    def draw_title_fancy(self, text: str, pos: Tuple[int, int], 
                        color: Tuple[int, int, int] = None):
        """Disegna un titolo con effetti speciali."""
        if color is None:
            color = COLORS['primary']
        
        self.draw_text(text, pos, 'hero', color, center=True, shadow=True, 
                      glow=True, glow_color=color)
    
    def draw_stats_box(self, stats: dict, pos: Tuple[int, int], size: Tuple[int, int]):
        """Disegna un box statistiche moderno."""
        rect = pygame.Rect(0, 0, size[0], size[1])
        rect.center = pos
        
        # Card background
        pygame.draw.rect(self.screen, COLORS['card_bg'], rect, border_radius=15)
        pygame.draw.rect(self.screen, COLORS['primary'], rect, width=2, border_radius=15)
        
        # Header
        self.draw_text("STATISTICHE", (pos[0], rect.top + 25), 'medium', COLORS['primary'], center=True)
        
        # Stats
        y = rect.top + 60
        for key, value in stats.items():
            self.draw_text(f"{key}: {value}", (pos[0], y), 'small', COLORS['white'], center=True)
            y += 30
    
    def draw_round_badge(self,
                        round_num: int,
                        pos: Tuple[int, int],
                        color: Tuple[int, int, int] = None):
        """
        Disegna un badge round esagonale.
        """
        if color is None:
            color = COLORS['primary']
        
        radius = 35
        
        # Esagono con glow
        angles = [i * math.pi / 3 - math.pi / 6 for i in range(6)]
        points = [(pos[0] + radius * math.cos(a), pos[1] + radius * math.sin(a)) 
                 for a in angles]
        
        # Glow
        glow_surf = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
        glow_points = [(radius * 1.5 + radius * 1.2 * math.cos(a), 
                       radius * 1.5 + radius * 1.2 * math.sin(a)) for a in angles]
        pygame.draw.polygon(glow_surf, (*color, 40), glow_points)
        self.screen.blit(glow_surf, (pos[0] - radius * 1.5, pos[1] - radius * 1.5))
        
        pygame.draw.polygon(self.screen, color, points)
        pygame.draw.polygon(self.screen, COLORS['white'], points, width=2)
        
        self.draw_text(f"R{round_num}", pos, 'medium', COLORS['white'], center=True)
