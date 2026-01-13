# Morra Cinese Portatile Interattiva

Un gioco di Morra Cinese (Sasso, Carta, Forbice) con riconoscimento dei gesti della mano tramite webcam.

## Requisiti

- Python 3.8+
- Webcam
- Sistema operativo: Windows, Linux (Raspberry Pi), macOS

## Installazione

```bash
# Crea un ambiente virtuale (opzionale ma consigliato)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Installa le dipendenze
pip install -r requirements.txt
```

## Avvio del Gioco

```bash
python main.py
```

## Come Giocare

### Gesti Riconosciuti
- Sasso (Rock): Pugno chiuso
- Carta (Paper): Mano aperta con tutte le dita estese
- Forbice (Scissors): Due dita estese (indice e medio)

### Navigazione Menu
- Seleziona: Premi INVIO
- Giu: Mano che scende

### Regole del Gioco
- Sasso batte Forbice
- Forbice batte Carta
- Carta batte Sasso

## Struttura del Progetto

```
Giochino/
├── main.py                 # Entry point dell'applicazione
├── game/
│   ├── __init__.py
│   ├── game_logic.py       # Logica del gioco
│   ├── game_state.py       # Gestione stati del gioco
│   └── highscore.py        # Sistema classifica
├── gesture/
│   ├── __init__.py
│   └── hand_detector.py    # Riconoscimento gesti mano
├── ui/
│   ├── __init__.py
│   ├── renderer.py         # Rendering grafico
│   ├── screens.py          # Schermate del gioco
│   └── assets/             # Risorse grafiche
├── config.py               # Configurazioni
├── requirements.txt        # Dipendenze
└── README.md               # Documentazione
```

## Configurazione

Modifica `config.py` per personalizzare:
- Risoluzione schermo
- Sensibilità riconoscimento
- Volume audio
- Tema grafico

## Per Raspberry Pi

Su Raspberry Pi, potrebbe essere necessario:

```bash
# Installa dipendenze di sistema
sudo apt-get update
sudo apt-get install -y libcamera-dev python3-libcamera
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

## Licenza

Progetto educativo - Uso libero per scopi didattici.
