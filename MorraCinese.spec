# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file per Morra Cinese - Portatile Interattiva
Questo file configura come PyInstaller deve costruire l'eseguibile.
"""

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Ottieni il percorso della directory corrente
block_cipher = None
project_dir = os.path.abspath('.')

# Raccogli tutti i dati da mediapipe (include modelli di ML)
mediapipe_datas = collect_data_files('mediapipe', include_py_files=False)

# Raccogli tutti i moduli hidden di mediapipe
mediapipe_hiddenimports = collect_submodules('mediapipe')

# Aggiungi moduli hidden per numpy, opencv e altri
additional_hiddenimports = [
    'numpy.core._dtype_ctypes',
    'numpy.core._multiarray_umath',
    'numpy.core._multiarray_tests',
    'cv2',
    'pygame',
    'mediapipe.python.solutions',
    'google.protobuf',
    'google.protobuf.internal',
]

# Combina tutte le hidden imports
all_hiddenimports = mediapipe_hiddenimports + additional_hiddenimports

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=[
        # Includi i dati di mediapipe (modelli ML)
        *mediapipe_datas,
        # Includi il file di configurazione
        ('config.py', '.'),
        # Includi tutti i moduli del gioco
        ('game/*.py', 'game'),
        ('gesture/*.py', 'gesture'),
        ('ui/*.py', 'ui'),
        # Includi highscores.json se esiste (opzionale)
        ('highscores.json', '.') if os.path.exists('highscores.json') else ('README.md', '.'),
    ],
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Escludi moduli non necessari per ridurre la dimensione
        'tkinter',
        'matplotlib.tests',
        'matplotlib.testing',
        'test',
        'tests',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MorraCinese',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Comprimi con UPX se disponibile
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Non mostrare console (GUI only)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Aggiungi un'icona .ico se disponibile
)
