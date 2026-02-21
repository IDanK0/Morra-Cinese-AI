"""
Morra Cinese Portatile Interattiva
===================================
Entry point principale del gioco.

Controlli:
- Gesti della mano per navigazione e gioco
- ESC per uscire
- Tastiera per inserimento nome
"""

try:
    import pygame  # type: ignore[import]
    PYGAME_AVAILABLE = True
except ImportError as e:
    print(f"❌ ERRORE: pygame non è installato!")
    print(f"   Soluzione: python -m pip install pygame")
    print(f"   Dettagli: {e}")
    import sys
    sys.exit(1)
except Exception as e:
    print(f"❌ ERRORE sconosciuto nell'import di pygame: {e}")
    import sys
    sys.exit(1)
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
        , HAND_DETECTION_FPS
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
        # Pygame è già stato verificato durante l'import
        # Se arriviamo qui, pygame è disponibile
        
        # Inizializza pygame
        try:
            pygame.init()
        except Exception as e:
            print(f"❌ Errore nell'inizializzazione di pygame: {e}")
            raise SystemExit("Impossibile inizializzare pygame")
        
        # Imposta il titolo della finestra
        try:
            pygame.display.set_caption("Morra Cinese - Portatile Interattiva")
        except Exception as e:
            print(f"⚠️ Avviso: Impossibile impostare il titolo della finestra: {e}")
        
        # Crea la finestra
        try:
            runtime_fullscreen = getattr(GAME_SETTINGS, 'fullscreen', FULLSCREEN)
            flags = pygame.FULLSCREEN if runtime_fullscreen else 0
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
        except Exception as e:
            print(f"❌ Errore nella creazione della finestra pygame: {e}")
            raise SystemExit("Impossibile creare finestra pygame")
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
        self.previous_state_before_camera_error = None  # Stato precedente prima dell'errore camera
        
        # Variabili per gestione riconnessione camera
        self.last_camera_check_time = time.time()
        self.camera_check_interval = 3.0  # Controlla ogni 3 secondi quando senza camera
        self.camera_reconnect_attempts = 0
        self.max_reconnect_attempts = 3  # Dopo 3 tentativi, mostra schermata errore
        self.last_known_frame = None  # Ultimo frame valido (per mostrare durante disconnessione temporanea)
        
        # Notifica camera connessa
        self._show_camera_connected_notification = False
        self._camera_notification_time = 0
        # Hand detection throttling
        self.last_detection_time = 0.0
        self.detection_interval = 1.0 / float(getattr(GAME_SETTINGS, 'hand_detection_fps', HAND_DETECTION_FPS))
    
    def _init_camera(self):
        """Inizializza la camera."""
        # Rileva camera disponibili
        print("Ricerca camera disponibili...")
        try:
            available_cameras = CameraManager.get_available_cameras()
        except Exception as e:
            print(f"Errore durante ricerca camera: {e}")
            available_cameras = []
        
        GAME_SETTINGS.available_cameras = available_cameras
        
        if available_cameras:
            print(f"Trovate {len(available_cameras)} camera:")
            for idx, name in available_cameras:
                print(f"  - {name}")
            
            # Usa la camera configurata o la prima disponibile
            camera_index = GAME_SETTINGS.camera_index
            if camera_index not in [c[0] for c in available_cameras]:
                camera_index = available_cameras[0][0]
                GAME_SETTINGS.camera_index = camera_index
        else:
            camera_index = CAMERA_INDEX
        
        try:
            self.camera = CameraManager(
                camera_index=camera_index,
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
            
            # Aggiorna camera
            self._update_camera()
            # Aggiorna il rilevamento gesti solo alla frequenza configurata
            now = time.time()
            if (now - self.last_detection_time) >= self.detection_interval or \
               self.state_manager.current_state in (GameState.COUNTDOWN, GameState.TIMED_PLAYER_TURN):
                self._update_gesture_detection()
                self.last_detection_time = now
            
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
        current_state = self.state_manager.current_state
        
        # ESC per uscire (tranne in CAMERA_ERROR che ha gestione propria)
        if event.key == pygame.K_ESCAPE and current_state != GameState.CAMERA_ERROR:
            if current_state == GameState.MENU:
                self.running = False
            else:
                self.state_manager.change_state(GameState.MENU)
        
        # Controlli da tastiera per il menu (backup)
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
            # Controlli da tastiera per modalità Variante Riflessi
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
                prev_fullscreen = getattr(GAME_SETTINGS, 'fullscreen', None)
                result = self.screen_manager.settings_change_value(-1)
                # Verifica che sia un intero valido (non bool) e >= 0
                if isinstance(result, int) and not isinstance(result, bool) and result >= 0:
                    # Cambio camera richiesto
                    self._switch_camera(result)
                # Se l'opzione fullscreen è stata modificata, applica il cambio display
                new_fullscreen = getattr(GAME_SETTINGS, 'fullscreen', None)
                if prev_fullscreen is not None and new_fullscreen is not None and prev_fullscreen != new_fullscreen:
                    self._apply_fullscreen()
            elif event.key == pygame.K_RIGHT:
                prev_fullscreen = getattr(GAME_SETTINGS, 'fullscreen', None)
                result = self.screen_manager.settings_change_value(1)
                # Verifica che sia un intero valido (non bool) e >= 0
                if isinstance(result, int) and not isinstance(result, bool) and result >= 0:
                    # Cambio camera richiesto
                    self._switch_camera(result)
                # Se l'opzione fullscreen è stata modificata, applica il cambio display
                new_fullscreen = getattr(GAME_SETTINGS, 'fullscreen', None)
                if prev_fullscreen is not None and new_fullscreen is not None and prev_fullscreen != new_fullscreen:
                    self._apply_fullscreen()
            elif event.key == pygame.K_r:
                # Shortcut per aggiornare lista camera
                self._refresh_cameras_in_settings()
            elif event.key == pygame.K_RETURN:
                result = self.screen_manager.settings_select()
                if result == 'back':
                    self.state_manager.change_state(GameState.MENU)
                elif result == 'reset_scores':
                    self.highscore_manager.clear()
                elif result == 'refresh_cameras':
                    self._refresh_cameras_in_settings()
        
        elif current_state == GameState.CAMERA_ERROR:
            if event.key == pygame.K_UP:
                self.screen_manager.camera_error_up()
            elif event.key == pygame.K_DOWN:
                self.screen_manager.camera_error_down()
            elif event.key == pygame.K_r:
                # Aggiorna lista camera
                self._refresh_available_cameras()
            elif event.key == pygame.K_RETURN:
                selected_idx = self.screen_manager.get_selected_camera_index()
                if selected_idx == -1:
                    # Aggiorna lista
                    self._refresh_available_cameras()
                elif selected_idx is not None:
                    # Prova a connettersi alla camera selezionata
                    if self._try_connect_camera(selected_idx):
                        # Ripristina lo stato di gioco se necessario
                        self._restore_from_camera_error()
            elif event.key == pygame.K_ESCAPE:
                # Continua senza camera
                self.camera = None
                self._restore_from_camera_error()
        
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
    
    def _switch_camera(self, camera_index: int):
        """
        Cambia la camera attiva nelle impostazioni.
        
        Args:
            camera_index: Indice della nuova camera
        """
        if self.camera:
            if self.camera.switch_camera(camera_index):
                print(f"Camera cambiata a indice {camera_index}")
            else:
                print(f"Impossibile cambiare alla camera {camera_index}")
                # Prova a ricreare la camera
                self._try_connect_camera(camera_index)
        else:
            self._try_connect_camera(camera_index)
    
    def _refresh_cameras_in_settings(self):
        """
        Aggiorna la lista delle camera disponibili mentre si è nelle impostazioni.
        Non rilascia la camera corrente, ma cerca nuove camera.
        """
        print("Aggiornamento lista camera...")
        
        # Salva la camera corrente
        current_camera_index = GAME_SETTINGS.camera_index if self.camera else -1
        
        try:
            # Cerca tutte le camera disponibili (inclusa quella corrente)
            available_cameras = CameraManager.get_available_cameras(max_cameras=10)
            
            # Aggiorna la lista globale
            GAME_SETTINGS.available_cameras = available_cameras
            
            print(f"Trovate {len(available_cameras)} camera:")
            for idx, name in available_cameras:
                current_marker = " (in uso)" if idx == current_camera_index else ""
                print(f"  - {name}{current_marker}")
            
            # Notifica l'UI che le camera sono state aggiornate
            self.screen_manager.notify_cameras_refreshed()
            
        except Exception as e:
            print(f"Errore durante aggiornamento lista camera: {e}")
    
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
            # Variante Riflessi: la CPU inizia
            self._start_timed_cpu_turn()
        else:
            # Modalità Tradizionale
            self.state_manager.change_state(GameState.PLAYING)
    
    def _start_timed_cpu_turn(self):
        """Avvia il turno della CPU nella modalità Variante Riflessi."""
        # Genera la mossa della CPU in anticipo (ma non la mostra)
        cpu_move = self.game_logic.get_cpu_move()
        self.state_manager.change_state(
            GameState.TIMED_CPU_MOVE,
            duration=CPU_MOVE_TIMER,
            cpu_move=cpu_move.value
        )
    
    def _start_timed_player_turn(self):
        """Avvia il turno del giocatore nella modalità Variante Riflessi."""
        response_time = GAME_SETTINGS.get_player_response_time()
        self.hand_detector.reset_gesture_tracking()
        self.state_manager.change_state(
            GameState.TIMED_PLAYER_TURN,
            duration=response_time,
            cpu_move=self.state_manager.get_data('cpu_move'),
            player_move=None
        )
    
    def _process_timed_player_move(self, gesture: str):
        """Processa la mossa del giocatore nella modalità Variante Riflessi."""
        # Salva la mossa e risolvi immediatamente
        self.state_manager.set_data('player_move', gesture)
        self._resolve_timed_round()
    
    def _update_camera(self):
        """Aggiorna il frame della camera con gestione robusta degli errori."""
        current_time = time.time()
        
        # Se non abbiamo una camera, prova periodicamente a riconnettersi
        if self.camera is None:
            if current_time - self.last_camera_check_time >= self.camera_check_interval:
                self.last_camera_check_time = current_time
                self._try_auto_reconnect()
            return
        
        # Verifica se la camera è aperta
        if not self.camera.is_opened():
            self._handle_camera_disconnection()
            return
        
        try:
            ret, frame = self.camera.read(flip=GAME_SETTINGS.camera_flip)
            
            if ret and frame is not None:
                self.current_frame = frame
                self.last_known_frame = frame.copy()  # Salva copia dell'ultimo frame valido
                self.camera_reconnect_attempts = 0  # Reset tentativi se tutto ok
            else:
                # Frame non valido, usa l'ultimo frame conosciuto
                if self.last_known_frame is not None:
                    self.current_frame = self.last_known_frame
            
            # Controlla se la camera si è disconnessa
            if self.camera.is_disconnected():
                self._handle_camera_disconnection()
                
        except Exception as e:
            print(f"Errore imprevisto durante lettura camera: {e}")
            self._handle_camera_disconnection()
    
    def _try_auto_reconnect(self):
        """
        Tenta di riconnettere automaticamente la camera.
        Questo metodo viene chiamato periodicamente quando la camera non è disponibile.
        Funziona sia per riconnessione dopo disconnessione che per nuove camera collegate.
        """
        if self.state_manager.current_state == GameState.CAMERA_ERROR:
            # Non fare auto-reconnect se siamo nella schermata di errore (l'utente gestisce)
            return
        
        # Cerca camera disponibili
        try:
            available_cameras = CameraManager.get_available_cameras(max_cameras=5)
            
            if available_cameras:
                # Aggiorna la lista globale
                GAME_SETTINGS.available_cameras = available_cameras
                
                # Prova a connettersi alla camera preferita o alla prima disponibile
                preferred_index = GAME_SETTINGS.camera_index
                camera_indices = [c[0] for c in available_cameras]
                
                # Usa la camera preferita se disponibile, altrimenti la prima
                if preferred_index in camera_indices:
                    target_index = preferred_index
                else:
                    target_index = available_cameras[0][0]
                
                if self._try_connect_camera(target_index):
                    print(f">>> Camera {target_index} rilevata e connessa automaticamente! <<<")
                    self.camera_reconnect_attempts = 0
                    
                    # Mostra notifica temporanea all'utente
                    self._show_camera_connected_notification = True
                    self._camera_notification_time = time.time()
        except Exception as e:
            print(f"Errore durante auto-reconnect: {e}")
    
    def _handle_camera_disconnection(self):
        """
        Gestisce la disconnessione della camera con logica di retry.
        """
        self.camera_reconnect_attempts += 1
        print(f"Camera disconnessa - Tentativo {self.camera_reconnect_attempts}/{self.max_reconnect_attempts}")
        
        # Prova a riconnettere automaticamente prima di mostrare l'errore
        if self.camera_reconnect_attempts <= self.max_reconnect_attempts:
            if self.camera and self.camera.try_reconnect():
                print("Camera riconnessa con successo!")
                self.camera_reconnect_attempts = 0
                return
        
        # Dopo troppi tentativi falliti, vai alla schermata di errore
        self._handle_camera_error()
    
    def _handle_camera_error(self):
        """Gestisce l'errore di disconnessione camera con preservazione dello stato di gioco."""
        print("Errore: Camera disconnessa!")
        
        # Salva lo stato corrente e i dati di gioco per tornare dopo
        current_state = self.state_manager.current_state
        if current_state != GameState.CAMERA_ERROR:
            self.previous_state_before_camera_error = current_state
            
            # Se eravamo in una fase di gioco attivo, salva il contesto
            if self.state_manager.is_in_game():
                self._saved_game_context = {
                    'player_score': self.game_logic.player_score,
                    'cpu_score': self.game_logic.cpu_score,
                    'round_count': self.game_logic.round_count,
                    'state_data': dict(self.state_manager.state_data),
                    'game_mode': GAME_SETTINGS.game_mode,
                    'timed_difficulty': GAME_SETTINGS.timed_difficulty,
                }
                print(f"Contesto di gioco salvato: P{self.game_logic.player_score}-CPU{self.game_logic.cpu_score}")
            else:
                self._saved_game_context = None
        
        # Aggiorna lista camera disponibili
        self._refresh_available_cameras()
        
        # Vai allo stato di errore camera
        self.state_manager.change_state(GameState.CAMERA_ERROR)
    
    def _restore_from_camera_error(self):
        """
        Ripristina lo stato del gioco dopo un errore camera.
        Gestisce correttamente il ritorno alla partita in corso o al menu.
        """
        # Reset del contatore tentativi
        self.camera_reconnect_attempts = 0
        
        # Controlla se avevamo un contesto di gioco salvato
        saved_context = getattr(self, '_saved_game_context', None)
        
        if saved_context and self.previous_state_before_camera_error in [
            GameState.PLAYING, GameState.COUNTDOWN, 
            GameState.TIMED_CPU_MOVE, GameState.TIMED_PLAYER_TURN
        ]:
            # Eravamo in una partita attiva
            # Ripristina i punteggi
            self.game_logic.player_score = saved_context['player_score']
            self.game_logic.cpu_score = saved_context['cpu_score']
            self.game_logic.round_count = saved_context['round_count']
            
            print(f"Contesto di gioco ripristinato: P{self.game_logic.player_score}-CPU{self.game_logic.cpu_score}")
            
            # Reset del tracking gesti
            self.hand_detector.reset_gesture_tracking()
            
            # Torna a uno stato giocabile appropriato
            if GAME_SETTINGS.game_mode == GameMode.TIMED:
                # Ricomincia dal turno CPU
                self._start_timed_cpu_turn()
            else:
                # Torna allo stato PLAYING
                self.state_manager.change_state(GameState.PLAYING)
            
            # Pulisci il contesto salvato
            self._saved_game_context = None
        elif self.previous_state_before_camera_error:
            # Non eravamo in gioco, torna allo stato precedente
            self.state_manager.change_state(self.previous_state_before_camera_error)
        else:
            # Fallback al menu
            self.state_manager.change_state(GameState.MENU)
        
        self.previous_state_before_camera_error = None
    
    def _refresh_available_cameras(self):
        """Aggiorna la lista delle camera disponibili in modo sicuro."""
        # Rilascia la camera attuale se esiste
        if self.camera:
            try:
                self.camera.release()
            except Exception as e:
                print(f"Errore durante rilascio camera: {e}")
            finally:
                self.camera = None
        
        # Cerca nuove camera
        try:
            available_cameras = CameraManager.get_available_cameras()
        except Exception as e:
            print(f"Errore durante scansione camera: {e}")
            available_cameras = []
            
        GAME_SETTINGS.available_cameras = available_cameras
        self.screen_manager.set_available_cameras(available_cameras)
        
        print(f"Camera disponibili: {len(available_cameras)}")
        for idx, name in available_cameras:
            print(f"  - {name}")

    def _apply_fullscreen(self):
        """Applica la modalità fullscreen basata su GAME_SETTINGS.fullscreen e aggiorna il renderer."""
        try:
            flags = pygame.FULLSCREEN if getattr(GAME_SETTINGS, 'fullscreen', False) else 0
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)
            # Aggiorna renderer con la nuova superficie
            if hasattr(self, 'renderer') and self.renderer:
                self.renderer.update_screen(self.screen)
        except Exception as e:
            print(f"Impossibile applicare fullscreen: {e}")
    
    def _try_connect_camera(self, camera_index: int) -> bool:
        """
        Prova a connettersi a una camera specifica.
        
        Args:
            camera_index: Indice della camera
            
        Returns:
            True se la connessione è riuscita
        """
        try:
            self.camera = CameraManager(
                camera_index=camera_index,
                width=CAMERA_WIDTH,
                height=CAMERA_HEIGHT
            )
            GAME_SETTINGS.camera_index = camera_index
            print(f"Camera {camera_index} connessa con successo!")
            return True
        except RuntimeError as e:
            print(f"Impossibile connettersi alla camera {camera_index}: {e}")
            self.camera = None
            return False
    
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
            
            # Durante il turno del giocatore in Variante Riflessi, aggiorna la mossa immediatamente
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
        
        # Variante Riflessi - turno del giocatore
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
        
        # Gestione countdown (modalità Tradizionale)
        if current_state == GameState.COUNTDOWN:
            if self.state_manager.is_state_timed_out():
                self._resolve_round()
        
        # Gestione turno CPU (Variante Riflessi)
        elif current_state == GameState.TIMED_CPU_MOVE:
            if self.state_manager.is_state_timed_out():
                # La CPU ha fatto la sua mossa, tocca al giocatore
                self._start_timed_player_turn()
        
        # Gestione turno giocatore (Variante Riflessi)
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
        """Gestisce il timeout del giocatore nella modalità Variante Riflessi."""
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
        """Risolve un round nella modalità Variante Riflessi."""
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
        
        # Notifica camera connessa
        if self._show_camera_connected_notification:
            elapsed = time.time() - self._camera_notification_time
            if elapsed < 3.0:  # Mostra per 3 secondi
                # Calcola alpha per fade out
                alpha = 1.0 if elapsed < 2.0 else (3.0 - elapsed)
                self._render_camera_notification(alpha)
            else:
                self._show_camera_connected_notification = False
        
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
    
    def _render_camera_notification(self, alpha: float):
        """Mostra una notifica che la camera è stata connessa."""
        # Crea superficie semi-trasparente per la notifica
        notif_width, notif_height = 350, 50
        notif_surface = pygame.Surface((notif_width, notif_height), pygame.SRCALPHA)
        
        # Sfondo verde con alpha
        bg_alpha = int(200 * alpha)
        notif_surface.fill((30, 120, 50, bg_alpha))
        
        # Bordo
        pygame.draw.rect(notif_surface, (50, 180, 80, bg_alpha), 
                        (0, 0, notif_width, notif_height), 3, border_radius=10)
        
        # Testo
        font = pygame.font.Font(None, 28)
        text_alpha = int(255 * alpha)
        text = font.render("✓ Camera connessa!", True, (255, 255, 255, text_alpha))
        text_rect = text.get_rect(center=(notif_width // 2, notif_height // 2))
        notif_surface.blit(text, text_rect)
        
        # Posiziona in alto al centro
        x = (SCREEN_WIDTH - notif_width) // 2
        y = 10
        self.screen.blit(notif_surface, (x, y))
    
    def _cleanup(self):
        """Pulisce le risorse."""
        print("Chiusura del gioco...")
        
        if self.camera:
            self.camera.release()
        
        try:
            self.hand_detector.release()
        except Exception:
            pass
        if hasattr(pygame, 'quit') and callable(getattr(pygame, 'quit')):
            try:
                pygame.quit()
            except Exception:
                pass


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
        if hasattr(pygame, 'quit') and callable(getattr(pygame, 'quit')):
            try:
                pygame.quit()
            except Exception:
                pass
        sys.exit(1)
    
    print("Arrivederci!")


if __name__ == "__main__":
    main()
