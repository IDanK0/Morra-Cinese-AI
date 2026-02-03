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
    HIGHSCORE_FILE, MAX_HIGHSCORES, DEBUG_MODE, SHOW_FPS,
    GAME_SETTINGS, GameMode, TimedDifficulty, CPU_MOVE_TIMER
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
        self.current_gesture_confidence = 0.0
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
            print("Il gioco funzionera con controlli da tastiera.")
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
        
        elif current_state == GameState.MODE_SELECT:
            if event.key == pygame.K_UP:
                self.screen_manager.mode_up()
            elif event.key == pygame.K_DOWN:
                self.screen_manager.mode_down()
            elif event.key == pygame.K_LEFT:
                self.screen_manager.difficulty_left()
            elif event.key == pygame.K_RIGHT:
                self.screen_manager.difficulty_right()
            elif event.key == pygame.K_RETURN:
                self._start_game_with_mode()
            elif event.key == pygame.K_ESCAPE:
                self.state_manager.change_state(GameState.MENU)
        
        elif current_state == GameState.PLAYING:
            # Controlli da tastiera per giocare (debug/backup)
            if event.key == pygame.K_1:  # Sasso
                self._process_player_move('rock')
            elif event.key == pygame.K_2:  # Carta
                self._process_player_move('paper')
            elif event.key == pygame.K_3:  # Forbice
                self._process_player_move('scissors')
        
        elif current_state == GameState.TIMED_PLAYER_TURN:
            # Controlli da tastiera per modalità a tempo
            if event.key == pygame.K_1:  # Sasso
                self._process_timed_player_move('rock')
            elif event.key == pygame.K_2:  # Carta
                self._process_timed_player_move('paper')
            elif event.key == pygame.K_3:  # Forbice
                self._process_timed_player_move('scissors')
        
        elif current_state == GameState.ENTER_NAME:
            name = self.screen_manager.handle_name_input(event)
            if name:
                self._save_highscore(name)
        
        elif current_state == GameState.SETTINGS:
            if event.key == pygame.K_UP:
                self.screen_manager.settings_up()
            elif event.key == pygame.K_DOWN:
                self.screen_manager.settings_down()
            elif event.key == pygame.K_LEFT:
                self.screen_manager.settings_change_value(-1)
            elif event.key == pygame.K_RIGHT:
                self.screen_manager.settings_change_value(1)
            elif event.key == pygame.K_RETURN:
                result = self.screen_manager.settings_select()
                if result == 'back':
                    self.state_manager.change_state(GameState.MENU)
                elif result == 'reset_scores':
                    self.highscore_manager.clear()
        
        elif current_state in [GameState.HIGHSCORE, GameState.GAME_OVER]:
            if event.key == pygame.K_LEFT:
                self.screen_manager.highscore_filter_left()
            elif event.key == pygame.K_RIGHT:
                self.screen_manager.highscore_filter_right()
            elif event.key == pygame.K_RETURN:
                if current_state == GameState.GAME_OVER:
                    self._check_and_save_highscore()
                else:
                    self.state_manager.change_state(GameState.MENU)
    
    def _handle_menu_selection(self):
        """Gestisce la selezione del menu."""
        selection = self.state_manager.get_selected_menu_item()
        
        if selection == 'play':
            # Apre la schermata di selezione modalità
            self.state_manager.change_state(GameState.MODE_SELECT)
        elif selection == 'highscore':
            self.state_manager.change_state(GameState.HIGHSCORE)
        elif selection == 'settings':
            self.state_manager.change_state(GameState.SETTINGS)
        elif selection == 'exit':
            self.running = False
    
    def _start_game_with_mode(self):
        """Avvia il gioco con la modalità selezionata."""
        # Imposta la modalità e difficoltà
        GAME_SETTINGS.game_mode = self.screen_manager.get_selected_mode()
        GAME_SETTINGS.timed_difficulty = self.screen_manager.get_selected_difficulty()
        
        # Avvia il gioco
        self._start_new_game()
    
    def _start_new_game(self):
        """Avvia una nuova partita."""
        self.game_logic.reset()
        self.hand_detector.reset_gesture_tracking()
        
        # Scegli lo stato iniziale in base alla modalità
        if GAME_SETTINGS.game_mode == GameMode.TIMED:
            # Modalità a tempo: la CPU inizia
            self._start_timed_cpu_turn()
        else:
            # Modalità classica
            self.state_manager.change_state(GameState.PLAYING)
    
    def _start_timed_cpu_turn(self):
        """Avvia il turno della CPU nella modalità a tempo."""
        # Genera la mossa della CPU in anticipo (ma non la mostra)
        cpu_move = self.game_logic.get_cpu_move()
        self.state_manager.change_state(
            GameState.TIMED_CPU_MOVE,
            duration=CPU_MOVE_TIMER,
            cpu_move=cpu_move.value
        )
    
    def _start_timed_player_turn(self):
        """Avvia il turno del giocatore nella modalità a tempo."""
        response_time = GAME_SETTINGS.get_player_response_time()
        self.hand_detector.reset_gesture_tracking()
        self.state_manager.change_state(
            GameState.TIMED_PLAYER_TURN,
            duration=response_time,
            cpu_move=self.state_manager.get_data('cpu_move'),
            player_move=None
        )
    
    def _process_timed_player_move(self, gesture: str):
        """Processa la mossa del giocatore nella modalità a tempo."""
        # Salva la mossa e risolvi immediatamente
        self.state_manager.set_data('player_move', gesture)
        self._resolve_timed_round()
    
    def _update_camera(self):
        """Aggiorna il frame della camera."""
        if self.camera and self.camera.is_opened():
            ret, frame = self.camera.read(flip=GAME_SETTINGS.camera_flip)
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
            # Riconosci il gesto con confidenza
            gesture, confidence = self.hand_detector.recognize_gesture(
                hand['landmarks'],
                self.current_frame.shape
            )
            
            # Applica smoothing temporale per ridurre jitter
            self.current_gesture, self.current_gesture_confidence = \
                self.hand_detector._apply_temporal_smoothing(gesture, confidence)
            
            # Durante il countdown, aggiorna la mossa immediatamente senza richiedere conferma
            if self.state_manager.current_state == GameState.COUNTDOWN:
                if self.current_gesture in ['rock', 'paper', 'scissors']:
                    self._update_player_move(self.current_gesture)
                self.gesture_progress = 1.0  # Mostra progresso pieno
                return
            
            # Durante il turno del giocatore in modalità a tempo, aggiorna la mossa immediatamente
            if self.state_manager.current_state == GameState.TIMED_PLAYER_TURN:
                if self.current_gesture in ['rock', 'paper', 'scissors']:
                    self.state_manager.set_data('player_move', self.current_gesture)
                self.gesture_progress = 1.0
                return
            
            # Controlla se il gesto e confermato
            hold_time = GAME_SETTINGS.gesture_hold_time
            confirmed = self.hand_detector.get_confirmed_gesture(
                self.current_gesture, 
                hold_time
            )
            
            self.gesture_progress = self.hand_detector.get_gesture_progress(hold_time)
            
            if confirmed:
                self._handle_confirmed_gesture(confirmed)
        else:
            self.current_gesture = 'none'
            self.current_gesture_confidence = 0.0
            self.gesture_progress = 0.0
            self.hand_detector.reset_gesture_tracking()
    
    def _handle_confirmed_gesture(self, gesture: str):
        """Gestisce un gesto confermato."""
        current_state = self.state_manager.current_state
        
        # Gioco
        if current_state == GameState.PLAYING:
            if gesture in ['rock', 'paper', 'scissors']:
                self._process_player_move(gesture)
                self.hand_detector.reset_gesture_tracking()
        
        # Countdown - permette di cambiare mossa
        elif current_state == GameState.COUNTDOWN:
            if gesture in ['rock', 'paper', 'scissors']:
                self._update_player_move(gesture)
                self.hand_detector.reset_gesture_tracking()
        
        # Modalità a tempo - turno del giocatore
        elif current_state == GameState.TIMED_PLAYER_TURN:
            if gesture in ['rock', 'paper', 'scissors']:
                self._process_timed_player_move(gesture)
                self.hand_detector.reset_gesture_tracking()
    
    def _process_player_move(self, gesture: str):
        """Processa la mossa del giocatore."""
        self.state_manager.change_state(
            GameState.COUNTDOWN,
            duration=GAME_SETTINGS.countdown_time,
            player_move=gesture
        )
    
    def _update_player_move(self, gesture: str):
        """Aggiorna la mossa del giocatore durante il countdown."""
        self.state_manager.state_data['player_move'] = gesture

    def _update_game_logic(self):
        """Aggiorna la logica di gioco."""
        current_state = self.state_manager.current_state
        
        # Gestione countdown (modalità classica)
        if current_state == GameState.COUNTDOWN:
            if self.state_manager.is_state_timed_out():
                self._resolve_round()
        
        # Gestione turno CPU (modalità a tempo)
        elif current_state == GameState.TIMED_CPU_MOVE:
            if self.state_manager.is_state_timed_out():
                # La CPU ha fatto la sua mossa, tocca al giocatore
                self._start_timed_player_turn()
        
        # Gestione turno giocatore (modalità a tempo)
        elif current_state == GameState.TIMED_PLAYER_TURN:
            # Controlla se il giocatore ha fatto una mossa
            player_move = self.state_manager.get_data('player_move')
            if player_move is not None:
                self._resolve_timed_round()
            elif self.state_manager.is_state_timed_out():
                # Tempo scaduto! Il giocatore non ha fatto la mossa
                self._handle_player_timeout()
        
        # Gestione risultato
        elif current_state == GameState.SHOWING_RESULT:
            if self.state_manager.is_state_timed_out():
                if self.game_logic.is_game_over():
                    self.state_manager.change_state(GameState.GAME_OVER)
                else:
                    # Continua con la modalità corretta
                    if GAME_SETTINGS.game_mode == GameMode.TIMED:
                        self._start_timed_cpu_turn()
                    else:
                        self.state_manager.change_state(GameState.PLAYING)
    
    def _handle_player_timeout(self):
        """Gestisce il timeout del giocatore nella modalità a tempo."""
        # Il giocatore non ha fatto la mossa in tempo - conta come sconfitta
        cpu_gesture = self.state_manager.get_data('cpu_move')
        
        # Incrementa il punteggio della CPU (il giocatore perde)
        self.game_logic.cpu_score += 1
        self.game_logic.round_count += 1
        
        self.state_manager.change_state(
            GameState.SHOWING_RESULT,
            duration=2.5,
            player_move=None,  # Nessuna mossa
            cpu_move=cpu_gesture,
            result='timeout',  # Risultato speciale per timeout
            timeout=True
        )
    
    def _resolve_timed_round(self):
        """Risolve un round nella modalità a tempo."""
        player_gesture = self.state_manager.get_data('player_move')
        cpu_gesture = self.state_manager.get_data('cpu_move')
        
        player_move = Move.from_gesture(player_gesture)
        cpu_move = Move.from_gesture(cpu_gesture)
        
        if player_move and cpu_move:
            # Determina il risultato
            result = self.game_logic.determine_winner(player_move, cpu_move)
            
            # Aggiorna i punteggi
            if result.value == 'player':
                self.game_logic.player_score += 1
            elif result.value == 'cpu':
                self.game_logic.cpu_score += 1
            
            self.game_logic.round_count += 1
            self.game_logic.history.append((player_move, cpu_move, result))
            
            self.state_manager.change_state(
                GameState.SHOWING_RESULT,
                duration=2.5,
                player_move=player_gesture,
                cpu_move=cpu_gesture,
                result=result.value
            )
    
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
        
        # Determina modalità e difficoltà
        game_mode = 'classic' if GAME_SETTINGS.game_mode == GameMode.CLASSIC else 'timed'
        difficulty = None
        if GAME_SETTINGS.game_mode == GameMode.TIMED:
            difficulty = GAME_SETTINGS.timed_difficulty.value
        
        position = self.highscore_manager.add_score(name, score, stats, game_mode, difficulty)
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
        if DEBUG_MODE or GAME_SETTINGS.show_fps:
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
