#!/usr/bin/env python3
"""
Test di verifica del sistema fullscreen e delle impostazioni.
"""

import sys
sys.path.insert(0, '.')

from config import FULLSCREEN, GAME_SETTINGS, GameMode, TimedDifficulty

print("=" * 60)
print("TEST FULLSCREEN E IMPOSTAZIONI")
print("=" * 60)
print()

print(f"Config Default Fullscreen: {FULLSCREEN}")
print(f"GAME_SETTINGS.fullscreen: {GAME_SETTINGS.fullscreen}")
print()

print("Opzioni Impostazioni Runtime:")
print(f"  gesture_hold_time: {GAME_SETTINGS.gesture_hold_time}s")
print(f"  countdown_time: {GAME_SETTINGS.countdown_time}s")
print(f"  camera_flip: {GAME_SETTINGS.camera_flip}")
print(f"  camera_index: {GAME_SETTINGS.camera_index}")
print(f"  show_fps: {GAME_SETTINGS.show_fps}")
print(f"  fullscreen: {GAME_SETTINGS.fullscreen}")
print(f"  game_mode: {GAME_SETTINGS.game_mode}")
print(f"  timed_difficulty: {GAME_SETTINGS.timed_difficulty}")
print()

print("Test Cambio Fullscreen:")
print(f"  Valore iniziale: {GAME_SETTINGS.fullscreen}")
GAME_SETTINGS.fullscreen = not GAME_SETTINGS.fullscreen
print(f"  Valore dopo toggle: {GAME_SETTINGS.fullscreen}")
GAME_SETTINGS.fullscreen = not GAME_SETTINGS.fullscreen
print(f"  Valore dopo secondo toggle: {GAME_SETTINGS.fullscreen}")
print()

print("Test Reset Defaults:")
GAME_SETTINGS.reset_defaults()
print(f"  fullscreen dopo reset: {GAME_SETTINGS.fullscreen}")
print(f"  gesture_hold_time dopo reset: {GAME_SETTINGS.gesture_hold_time}")
print()

print("=" * 60)
print("TEST MODALITÀ DI GIOCO")
print("=" * 60)
print()

print(f"Modalità disponibili: {[m.name for m in GameMode]}")
print(f"Difficoltà disponibili: {[d.name for d in TimedDifficulty]}")
print()

from config import PLAYER_RESPONSE_TIMES, DIFFICULTY_NAMES

print("Difficoltà e Tempi di Risposta:")
for diff in TimedDifficulty:
    time = PLAYER_RESPONSE_TIMES.get(diff, 0)
    name = DIFFICULTY_NAMES.get(diff, '?')
    print(f"  {name:10}: {time:.1f}s")
print()

print("✅ Tutti i test completati!")
