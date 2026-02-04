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
# COLORI (RGB) - TEMA GAMING MODERNO
# =====================
COLORS = {
    # Sfondo e base
    'background': (15, 15, 25),       # Blu scuro profondo
    'bg_gradient_top': (25, 28, 50),  # Gradiente top
    'bg_gradient_bottom': (10, 12, 22),# Gradiente bottom
    'card_bg': (28, 32, 55),          # Sfondo cards
    'card_bg_light': (38, 42, 70),    # Cards hover
    
    # Colori primari vivaci
    'primary': (99, 102, 241),        # Indigo moderno
    'primary_light': (129, 140, 248), # Indigo chiaro
    'primary_dark': (67, 56, 202),    # Indigo scuro
    'secondary': (251, 146, 60),      # Arancione caldo
    'secondary_light': (253, 186, 116),# Arancione chiaro
    'accent': (168, 85, 247),         # Viola accent
    'accent_light': (192, 132, 252),  # Viola chiaro
    
    # Stati
    'success': (34, 197, 94),         # Verde smeraldo
    'success_light': (74, 222, 128),  # Verde chiaro
    'success_glow': (22, 163, 74),    # Verde glow
    'danger': (239, 68, 68),          # Rosso coral
    'danger_light': (252, 129, 129),  # Rosso chiaro
    'danger_glow': (220, 38, 38),     # Rosso glow
    'warning': (250, 204, 21),        # Giallo dorato
    'warning_light': (253, 224, 71),  # Giallo chiaro
    
    # Neutri
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'gray': (148, 163, 184),          # Grigio moderno
    'light_gray': (226, 232, 240),    # Grigio chiaro
    'dark_gray': (51, 65, 85),        # Grigio scuro
    'muted': (100, 116, 139),         # Testo secondario
    
    # Mosse - Colori gaming vivaci
    'rock': (239, 68, 68),            # Rosso potenza (Sasso)
    'rock_light': (254, 202, 202),
    'rock_bg': (127, 29, 29),
    'paper': (59, 130, 246),          # Blu elegante (Carta)
    'paper_light': (191, 219, 254),
    'paper_bg': (30, 64, 175),
    'scissors': (234, 179, 8),        # Oro metallico (Forbice)
    'scissors_light': (254, 240, 138),
    'scissors_bg': (161, 98, 7),
    
    # Medaglie
    'gold': (255, 215, 0),            # Oro brillante
    'gold_glow': (234, 179, 8),
    'silver': (203, 213, 225),        # Argento moderno
    'silver_glow': (148, 163, 184),
    'bronze': (217, 119, 6),          # Bronzo caldo
    'bronze_glow': (180, 83, 9),
    
    # Effetti speciali
    'glow_blue': (96, 165, 250),      # Glow azzurro
    'glow_purple': (168, 85, 247),    # Glow viola
    'glow_pink': (236, 72, 153),      # Glow rosa
    'neon_green': (74, 222, 128),     # Neon verde
    'neon_cyan': (34, 211, 238),      # Neon ciano
    
    # UI specifica
    'button_bg': (55, 48, 107),       # Sfondo bottoni
    'button_hover': (79, 70, 138),    # Bottoni hover
    'button_border': (99, 102, 241),  # Bordo bottoni
    'input_bg': (30, 27, 60),         # Input background
    'progress_bg': (30, 41, 59),      # Progress bar bg
    'timer_critical': (239, 68, 68),  # Timer critico
    'timer_warning': (251, 146, 60),  # Timer warning
    'timer_safe': (34, 197, 94),      # Timer sicuro
}

# =====================
# EMOJI / SIMBOLI UI
# =====================
UI_SYMBOLS = {
    'rock': '✊',
    'paper': '✋', 
    'scissors': '✌️',
    'trophy': '🏆',
    'medal_gold': '🥇',
    'medal_silver': '🥈',
    'medal_bronze': '🥉',
    'star': '⭐',
    'fire': '🔥',
    'crown': '👑',
    'target': '🎯',
    'gamepad': '🎮',
    'settings': '⚙️',
    'back': '←',
    'next': '→',
    'check': '✓',
    'cross': '✗',
    'timer': '⏱️',
    'camera': '📷',
    'warning': '⚠️',
    'info': 'ℹ️',
    'play': '▶',
    'vs': '⚔️',
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
    'enter_name': 'Inserisci il tuo nome (max 5 caratteri)',
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
        self.camera_index = CAMERA_INDEX
        self.available_cameras = []  # Lista delle camera disponibili [(indice, nome)]
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
        self.camera_index = CAMERA_INDEX
        self.audio_enabled = AUDIO_ENABLED
        self.show_fps = SHOW_FPS
        self.game_mode = GameMode.CLASSIC
        self.timed_difficulty = TimedDifficulty.MEDIUM
    
    def get_player_response_time(self) -> float:
        """Restituisce il tempo di risposta del giocatore per la difficoltà corrente."""
        return PLAYER_RESPONSE_TIMES.get(self.timed_difficulty, 4.0)
    
    def get_camera_name(self) -> str:
        """Restituisce il nome della camera attualmente selezionata."""
        for idx, name in self.available_cameras:
            if idx == self.camera_index:
                return name
        return f"Camera {self.camera_index}"

# Istanza globale delle impostazioni
GAME_SETTINGS = GameSettings()
