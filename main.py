"""
Morra Cinese Portatile Interattiva
===================================
Entry point principale del gioco.

Controlli:
- Gesti della mano per navigazione e gioco
- ESC per uscire
- Tastiera per inserimento nome
"""

import pygame
import sys
import time
from typing import Optional

# Moduli del gioco
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, FULLSCREEN,
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FLIP,
    GESTURE_HOLD_TIME, COUNTDOWN_TIME, ROUNDS_TO_WIN,
    HIGHSCORE_FILE, MAX_HIGHSCORES, DEBUG_MODE, SHOW_FPS
)
from gesture.hand_detector import HandDetector, CameraManager
from game.game_logic import GameLogic, Move
from game.game_state import GameState, StateManager
from game.highscore import HighScoreManager
from ui.renderer import Renderer
from ui.screens import ScreenManager


class MorraCineseGame:
    """
    Classe principale del gioco Morra Cinese.
    Gestisce il game loop, l'input e il coordinamento tra i moduli.
    """
    
    def __init__(self):
        """Inizializza il gioco."""
        # Inizializza Pygame
        pygame.init()
        pygame.display.set_caption("Morra Cinese - Portatile Interattiva")
        
        # Crea la finestra
        flags = pygame.FULLSCREEN if FULLSCREEN else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inizializza i componenti
        self._init_camera()
        self._init_hand_detector()
        self._init_game_systems()
        self._init_ui()
        
        # Variabili di stato
        self.current_frame = None
        self.current_gesture = 'none'
        self.gesture_progress = 0.0
        self.last_confirmed_gesture = None
        self.last_frame_time = time.time()
    
    def _init_camera(self):
        """Inizializza la camera."""
        try:
            self.camera = CameraManager(
                camera_index=CAMERA_INDEX,
                width=CAMERA_WIDTH,
                height=CAMERA_HEIGHT
            )
            print(f"Camera inizializzata: {self.camera.width}x{self.camera.height}")
        except RuntimeError as e:
            print(f"Attenzione: Camera non disponibile - {e}")
            print("Il gioco funzionerà con controlli da tastiera.")
            self.camera = None
    
    def _init_hand_detector(self):
        """Inizializza il rilevatore di mani."""
        self.hand_detector = HandDetector(
            max_hands=1,
            detection_confidence=0.7,
            tracking_confidence=0.7
        )
    
    def _init_game_systems(self):
        """Inizializza i sistemi di gioco."""
        self.game_logic = GameLogic(rounds_to_win=ROUNDS_TO_WIN)
        self.state_manager = StateManager()
        self.highscore_manager = HighScoreManager(
            filename=HIGHSCORE_FILE,
            max_entries=MAX_HIGHSCORES
        )
    
    def _init_ui(self):
        """Inizializza l'interfaccia utente."""
        self.renderer = Renderer(self.screen)
        self.screen_manager = ScreenManager(
            self.renderer,
            self.state_manager,
            self.game_logic,
            self.highscore_manager
        )
    
    def run(self):
        """Esegue il game loop principale."""
        print("Avvio Morra Cinese...")
        print("Premi ESC per uscire")
        
        while self.running:
            # Calcola delta time
            current_time = time.time()
            dt = current_time - self.last_frame_time
            self.last_frame_time = current_time
            
            # Gestione eventi
            self._handle_events()
            
            # Aggiorna camera e gesti
            self._update_camera()
            self._update_gesture_detection()
            
            # Aggiorna logica di gioco
            self._update_game_logic()
            
            # Rendering
            self._render(dt)
            
            # Limita FPS
            self.clock.tick(FPS)
        
        self._cleanup()
    
    def _handle_events(self):
        """Gestisce gli eventi Pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_key_event(event)
    
    def _handle_key_event(self, event):
        """Gestisce gli eventi da tastiera."""
        # ESC per uscire
        if event.key == pygame.K_ESCAPE:
            if self.state_manager.current_state == GameState.MENU:
                self.running = False
            else:
                self.state_manager.change_state(GameState.MENU)
        
        # Controlli da tastiera per il menu (backup)
        current_state = self.state_manager.current_state
        
        if current_state == GameState.MENU:
            if event.key == pygame.K_UP:
                self.state_manager.menu_up()
            elif event.key == pygame.K_DOWN:
                self.state_manager.menu_down()
            elif event.key == pygame.K_RETURN:
                self._handle_menu_selection()
        
        elif current_state == GameState.PLAYING:
            # Controlli da tastiera per giocare (debug/backup)
            if event.key == pygame.K_1:  # Sasso
                self._process_player_move('rock')
            elif event.key == pygame.K_2:  # Carta
                self._process_player_move('paper')
            elif event.key == pygame.K_3:  # Forbice
                self._process_player_move('scissors')
        
        elif current_state == GameState.ENTER_NAME:
            name = self.screen_manager.handle_name_input(event)
            if name:
                self._save_highscore(name)
        
        elif current_state in [GameState.HIGHSCORE, GameState.SETTINGS, GameState.GAME_OVER]:
            if event.key == pygame.K_RETURN:
                self.state_manager.change_state(GameState.MENU)
    
    def _handle_menu_selection(self):
        """Gestisce la selezione del menu."""
        selection = self.state_manager.get_selected_menu_item()
        
        if selection == 'play':
            self._start_new_game()
        elif selection == 'highscore':
            self.state_manager.change_state(GameState.HIGHSCORE)
        elif selection == 'settings':
            self.state_manager.change_state(GameState.SETTINGS)
        elif selection == 'exit':
            self.running = False
    
    def _start_new_game(self):
        """Avvia una nuova partita."""
        self.game_logic.reset()
        self.hand_detector.reset_gesture_tracking()
        self.state_manager.change_state(GameState.PLAYING)
    
    def _update_camera(self):
        """Aggiorna il frame della camera."""
        if self.camera and self.camera.is_opened():
            ret, frame = self.camera.read(flip=CAMERA_FLIP)
            if ret:
                self.current_frame = frame
    
    def _update_gesture_detection(self):
        """Aggiorna il rilevamento dei gesti."""
        if self.current_frame is None:
            return
        
        # Rileva le mani nel frame
        processed_frame, hands = self.hand_detector.find_hands(
            self.current_frame, 
            draw=True
        )
        self.current_frame = processed_frame
        
        if hands:
            hand = hands[0]
            # Riconosci il gesto
            self.current_gesture = self.hand_detector.recognize_gesture(
                hand['landmarks'],
                self.current_frame.shape
            )
            
            # Durante il countdown, aggiorna la mossa immediatamente senza richiedere conferma
            if self.state_manager.current_state == GameState.COUNTDOWN:
                if self.current_gesture in ['rock', 'paper', 'scissors']:
                    self._update_player_move(self.current_gesture)
                self.gesture_progress = 1.0  # Mostra progresso pieno
                return
            
            # Controlla se il gesto è confermato
            hold_time = GESTURE_HOLD_TIME
            confirmed = self.hand_detector.get_confirmed_gesture(
                self.current_gesture, 
                hold_time
            )
            
            self.gesture_progress = self.hand_detector.get_gesture_progress(hold_time)
            
            if confirmed:
                self._handle_confirmed_gesture(confirmed)
        else:
            self.current_gesture = 'none'
            self.gesture_progress = 0.0
            self.hand_detector.reset_gesture_tracking()
    
    def _handle_confirmed_gesture(self, gesture: str):
        """Gestisce un gesto confermato."""
        current_state = self.state_manager.current_state
        
        # Navigazione nel menu
        if current_state == GameState.MENU:
            if gesture == 'point_up':
                self.state_manager.menu_up()
                self.hand_detector.reset_gesture_tracking()
            elif gesture == 'point_down':
                self.state_manager.menu_down()
                self.hand_detector.reset_gesture_tracking()
            elif gesture == 'ok':
                self._handle_menu_selection()
                self.hand_detector.reset_gesture_tracking()
        
        # Gioco
        elif current_state == GameState.PLAYING:
            if gesture in ['rock', 'paper', 'scissors']:
                self._process_player_move(gesture)
                self.hand_detector.reset_gesture_tracking()
        
        # Countdown - permette di cambiare mossa
        elif current_state == GameState.COUNTDOWN:
            if gesture in ['rock', 'paper', 'scissors']:
                self._update_player_move(gesture)
                self.hand_detector.reset_gesture_tracking()
        
        # Conferma in altre schermate
        elif current_state in [GameState.HIGHSCORE, GameState.SETTINGS]:
            if gesture == 'ok':
                self.state_manager.change_state(GameState.MENU)
                self.hand_detector.reset_gesture_tracking()
        
        elif current_state == GameState.GAME_OVER:
            if gesture == 'ok':
                self._check_and_save_highscore()
                self.hand_detector.reset_gesture_tracking()
    
    def _process_player_move(self, gesture: str):
        """Processa la mossa del giocatore."""
        self.state_manager.change_state(
            GameState.COUNTDOWN,
            duration=COUNTDOWN_TIME,
            player_move=gesture
        )
    
    def _update_player_move(self, gesture: str):
        """Aggiorna la mossa del giocatore durante il countdown."""
        self.state_manager.state_data['player_move'] = gesture

    def _update_game_logic(self):
        """Aggiorna la logica di gioco."""
        current_state = self.state_manager.current_state
        
        # Gestione countdown
        if current_state == GameState.COUNTDOWN:
            if self.state_manager.is_state_timed_out():
                self._resolve_round()
        
        # Gestione risultato
        elif current_state == GameState.SHOWING_RESULT:
            if self.state_manager.is_state_timed_out():
                if self.game_logic.is_game_over():
                    self.state_manager.change_state(GameState.GAME_OVER)
                else:
                    self.state_manager.change_state(GameState.PLAYING)
    
    def _resolve_round(self):
        """Risolve un round di gioco."""
        player_gesture = self.state_manager.get_data('player_move')
        player_move = Move.from_gesture(player_gesture)
        
        if player_move:
            cpu_move, result = self.game_logic.play_round(player_move)
            
            self.state_manager.change_state(
                GameState.SHOWING_RESULT,
                duration=2.5,
                player_move=player_gesture,
                cpu_move=cpu_move.value,
                result=result.value
            )
    
    def _check_and_save_highscore(self):
        """Controlla e salva il punteggio."""
        player_score, _ = self.game_logic.get_score()
        
        if self.highscore_manager.is_high_score(player_score):
            self.screen_manager.reset_name_input()
            self.state_manager.change_state(
                GameState.ENTER_NAME,
                score=player_score
            )
        else:
            self.state_manager.change_state(GameState.MENU)
    
    def _save_highscore(self, name: str):
        """Salva il punteggio nella classifica."""
        score = self.state_manager.get_data('score', 0)
        stats = self.game_logic.get_stats()
        
        position = self.highscore_manager.add_score(name, score, stats)
        print(f"Nuovo record! {name}: {score} punti (posizione {position})")
        
        self.state_manager.change_state(GameState.HIGHSCORE)
    
    def _render(self, dt: float):
        """Renderizza il frame corrente."""
        # Aggiorna animazioni
        self.screen_manager.update(dt)
        
        # Renderizza la schermata corrente
        self.screen_manager.render(
            self.state_manager.current_state,
            self.current_frame,
            self.current_gesture,
            self.gesture_progress
        )
        
        # Debug info
        if DEBUG_MODE or SHOW_FPS:
            fps = self.clock.get_fps()
            self.renderer.draw_text(
                f"FPS: {fps:.0f}",
                (10, 10),
                'tiny',
                (100, 100, 100)
            )
        
        # Aggiorna display
        pygame.display.flip()
    
    def _cleanup(self):
        """Pulisce le risorse."""
        print("Chiusura del gioco...")
        
        if self.camera:
            self.camera.release()
        
        self.hand_detector.release()
        pygame.quit()


def main():
    """Funzione principale."""
    print("=" * 50)
    print("  MORRA CINESE - Portatile Interattiva")
    print("=" * 50)
    print()
    
    try:
        game = MorraCineseGame()
        game.run()
    except Exception as e:
        print(f"Errore critico: {e}")
        import traceback
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)
    
    print("Arrivederci!")


if __name__ == "__main__":
    main()
