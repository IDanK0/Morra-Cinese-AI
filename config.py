"""
Configurazione globale del gioco Morra Cinese
"""

# =====================
# CONFIGURAZIONE SCHERMO
# =====================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
FULLSCREEN = False

# =====================
# CONFIGURAZIONE CAMERA
# =====================
CAMERA_INDEX = 0  # Indice della webcam (0 = default)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FLIP = True  # Specchia l'immagine orizzontalmente

# =====================
# CONFIGURAZIONE GIOCO
# =====================
ROUNDS_TO_WIN = 3  # Punti per vincere una partita
GESTURE_HOLD_TIME = 1.0  # Secondi per confermare un gesto
COUNTDOWN_TIME = 3  # Secondi di countdown prima della mossa

# =====================
# RICONOSCIMENTO GESTI AVANZATO
# =====================
# Parametri per il riconoscimento migliorato
GESTURE_DETECTION = {
    'min_detection_confidence': 0.7,  # Soglia minima per rilevare la mano
    'min_tracking_confidence': 0.7,   # Soglia minima per tracking continuo
    'temporal_smoothing_frames': 5,    # Numero di frame per smoothing temporale
    
    # Parametri FORBICI
    'scissors_v_ratio_excellent': 1.3, # Rapporto punte/base per forbice perfetta
    'scissors_v_ratio_good': 1.1,      # Rapporto punte/base per forbice accettabile
    
    # Parametri DITA ESTESE
    'finger_extension_distance_ratio': 1.15,  # Ratio distanza per dito esteso
    'finger_angle_threshold': 140,     # Angolo minimo per considerare dito esteso (gradi)
    'wrist_distance_ratio': 1.3,       # Ratio distanza punta-polso vs base-polso
}

# =====================
# MODALITÀ A TEMPO
# =====================
from enum import Enum

class GameMode(Enum):
    """Modalità di gioco disponibili."""
    CLASSIC = 'classic'      # Modalità classica
    TIMED = 'timed'          # Modalità a tempo

class TimedDifficulty(Enum):
    """Difficoltà per la modalità a tempo."""
    EASY = 'easy'       # Facile - 6 secondi
    MEDIUM = 'medium'   # Media - 4 secondi
    HARD = 'hard'       # Difficile - 2 secondi

# Timer CPU (fisso per tutte le difficoltà)
CPU_MOVE_TIMER = 3.0  # Secondi prima che la CPU faccia la sua mossa

# Timer risposta giocatore per difficoltà
PLAYER_RESPONSE_TIMES = {
    TimedDifficulty.EASY: 6.0,
    TimedDifficulty.MEDIUM: 4.0,
    TimedDifficulty.HARD: 2.0,
}

# Nomi italiani delle difficoltà
DIFFICULTY_NAMES = {
    TimedDifficulty.EASY: 'Facile',
    TimedDifficulty.MEDIUM: 'Media',
    TimedDifficulty.HARD: 'Difficile',
}

# =====================
# COLORI (RGB)
# =====================
COLORS = {
    'background': (25, 25, 35),
    'primary': (100, 149, 237),  # Cornflower blue
    'secondary': (255, 165, 0),   # Orange
    'success': (50, 205, 50),     # Lime green
    'danger': (220, 20, 60),      # Crimson
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (128, 128, 128),
    'light_gray': (200, 200, 200),
    'dark_gray': (50, 50, 50),
    'rock': (139, 90, 43),        # Marrone roccia
    'paper': (245, 245, 220),     # Beige carta
    'scissors': (192, 192, 192),  # Argento forbici
    'gold': (255, 215, 0),        # Oro (primo posto)
    'silver': (192, 192, 192),    # Argento (secondo posto)
    'bronze': (205, 127, 50),     # Bronzo (terzo posto)
    'glow_blue': (173, 216, 230), # Light blue per glow
    'dark_blue': (10, 10, 20),    # Dark blue sfondo
}

# =====================
# GESTI RICONOSCIUTI
# =====================
GESTURES = {
    'rock': 'Sasso',
    'paper': 'Carta',
    'scissors': 'Forbice',
    'none': 'Nessun gesto'
}

# =====================
# REGOLE DEL GIOCO
# =====================
GAME_RULES = {
    ('rock', 'scissors'): 'player',     # Sasso batte Forbice
    ('scissors', 'paper'): 'player',    # Forbice batte Carta
    ('paper', 'rock'): 'player',        # Carta batte Sasso
    ('scissors', 'rock'): 'cpu',        # Forbice perde contro Sasso
    ('paper', 'scissors'): 'cpu',       # Carta perde contro Forbice
    ('rock', 'paper'): 'cpu',           # Sasso perde contro Carta
}

# =====================
# TESTI UI
# =====================
TEXTS = {
    'title': 'MORRA CINESE',
    'subtitle': 'Portatile Interattiva',
    'play': 'GIOCA',
    'highscore': 'CLASSIFICA',
    'settings': 'IMPOSTAZIONI',
    'exit': 'ESCI',
    'back': 'INDIETRO',
    'you_win': 'HAI VINTO!',
    'you_lose': 'HAI PERSO!',
    'draw': 'PAREGGIO!',
    'make_gesture': 'Fai il tuo gesto!',
    'countdown': 'Pronti in...',
    'enter_name': 'Inserisci il tuo nome (3 lettere)',
}

# =====================
# AUDIO
# =====================
AUDIO_ENABLED = True
MUSIC_VOLUME = 0.3
SFX_VOLUME = 0.5

# =====================
# HIGH SCORE
# =====================
HIGHSCORE_FILE = 'highscores.json'
MAX_HIGHSCORES = 10

# =====================
# DEBUG
# =====================
DEBUG_MODE = False
SHOW_FPS = True
SHOW_HAND_LANDMARKS = True

# =====================
# IMPOSTAZIONI RUNTIME (modificabili in-game)
# =====================
class GameSettings:
    """Classe per gestire le impostazioni modificabili a runtime."""
    
    def __init__(self):
        self.gesture_hold_time = GESTURE_HOLD_TIME
        self.countdown_time = COUNTDOWN_TIME
        self.camera_flip = CAMERA_FLIP
        self.audio_enabled = AUDIO_ENABLED
        self.show_fps = SHOW_FPS
        # Modalità di gioco
        self.game_mode = GameMode.CLASSIC
        self.timed_difficulty = TimedDifficulty.MEDIUM
        
    def reset_defaults(self):
        """Ripristina le impostazioni predefinite."""
        self.gesture_hold_time = GESTURE_HOLD_TIME
        self.countdown_time = COUNTDOWN_TIME
        self.camera_flip = CAMERA_FLIP
        self.audio_enabled = AUDIO_ENABLED
        self.show_fps = SHOW_FPS
        self.game_mode = GameMode.CLASSIC
        self.timed_difficulty = TimedDifficulty.MEDIUM
    
    def get_player_response_time(self) -> float:
        """Restituisce il tempo di risposta del giocatore per la difficoltà corrente."""
        return PLAYER_RESPONSE_TIMES.get(self.timed_difficulty, 4.0)

# Istanza globale delle impostazioni
GAME_SETTINGS = GameSettings()
