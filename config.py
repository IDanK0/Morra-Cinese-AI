"""
Configurazione globale del gioco Morra Cinese
"""

# =====================
# CONFIGURAZIONE SCHERMO
# =====================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 30
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
}

# =====================
# GESTI RICONOSCIUTI
# =====================
GESTURES = {
    'rock': 'Sasso',
    'paper': 'Carta',
    'scissors': 'Forbice',
    'ok': 'OK/Seleziona',
    'point_up': 'Su',
    'point_down': 'Giù',
    'thumbs_up': 'Conferma',
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
        
    def reset_defaults(self):
        """Ripristina le impostazioni predefinite."""
        self.gesture_hold_time = GESTURE_HOLD_TIME
        self.countdown_time = COUNTDOWN_TIME
        self.camera_flip = CAMERA_FLIP
        self.audio_enabled = AUDIO_ENABLED
        self.show_fps = SHOW_FPS

# Istanza globale delle impostazioni
GAME_SETTINGS = GameSettings()
