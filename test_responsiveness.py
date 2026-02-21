#!/usr/bin/env python3
"""
Script di test per verificare la responsività UI su diverse risoluzioni.
Testa il sistema di scaling del renderer con varie risoluzioni.
"""

import sys
sys.path.insert(0, '.')

from config import SCREEN_WIDTH, SCREEN_HEIGHT, COLORS

# Test di scaling su diverse risoluzioni
test_resolutions = [
    (720, 480, "WVGA"),
    (800, 600, "Base"),
    (1024, 768, "XGA"),
    (1280, 720, "HD"),
    (1920, 1080, "Full HD"),
    (2560, 1440, "2K"),
]

print("=" * 60)
print("TEST RESPONSIVITÀ - Calcolo Scaling")
print("=" * 60)
print(f"Risoluzione base: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
print()

for width, height, name in test_resolutions:
    scale = max(0.5, min(width / SCREEN_WIDTH, height / SCREEN_HEIGHT))
    print(f"{name:12} ({width:4}x{height:4}): scale={scale:.2f}")
    print(f"  Font sizes: hero={int(96*scale):2}px, title={int(72*scale):2}px, medium={int(38*scale):2}px")

print()
print("=" * 60)
print("TEST SIMBOLI")
print("=" * 60)

# Testa i simboli UI
from config import UI_SYMBOLS

test_symbols = ['rock', 'paper', 'scissors', 'trophy', 'gamepad', 'settings']
print("Simboli disponibili:")
for sym in test_symbols:
    if sym in UI_SYMBOLS:
        print(f"  {sym:15}: '{UI_SYMBOLS[sym]}'")

print()
print("=" * 60)
print("TEST IMPORTS")
print("=" * 60)

try:
    from game.game_logic import Move
    print(f"✓ Move enum caricato: {[m.name for m in Move]}")
    
    rock = Move.ROCK
    print(f"✓ Move.ROCK.get_emoji() = '{rock.get_emoji()}'")
    print(f"✓ Move.ROCK.get_name() = '{rock.get_name()}'")
except Exception as e:
    print(f"✗ Errore nel caricamento Move: {e}")

print()
print("=" * 60)
print("TEST COLORI GAMING")
print("=" * 60)

colors_to_test = ['rock', 'paper', 'scissors', 'success', 'danger', 'warning']
print("Colori delle mosse:")
for color_name in colors_to_test:
    if color_name in COLORS:
        r, g, b = COLORS[color_name]
        print(f"  {color_name:15}: RGB({r:3}, {g:3}, {b:3})")

print()
print("✅ Tutti i test completati!")
print()
