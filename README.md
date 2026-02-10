# 🎮 Morra Cinese - Portatile Interattiva

Un gioco di Morra Cinese (Sasso-Carta-Forbice) completamente **interattivo con riconoscimento gestuale della mano in tempo reale**. Gioca contro l'IA muovendo la tua mano davanti alla webcam!

![Python](https://img.shields.io/badge/Python-3.12.0-blue)
![Pip](https://img.shields.io/badge/pip-23.2.1-yellow)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Raspberry%20Pi-orange)

---

## ✨ Caratteristiche Principali

### 🎯 Gioco Interattivo
- **Riconoscimento gestuale in tempo reale** usando MediaPipe
- Gesti della mano per controllare il gioco
- Interfaccia grafica moderna e reattiva
- Sistema di punteggi e classifica persistente

### 🤖 Intelligenza Artificiale
- IA adattiva per sfide variegate
- Scelta casuale intelligente delle mosse

### 📊 Gestione Risultati
- Sistema di punteggi con classifica Top 10
- Salvataggio automatico delle prestazioni
- Statistiche per ogni giocatore

### 🎨 Interfaccia Utente
- Menu principale intuitivo
- Animazioni particellari e effetti visuali
- Supporto a schermo intero (modalità arcade)
- Visualizzazione feed webcam in tempo reale
- Countdown interattivo prima di ogni mossa

### ⚙️ Configurabilità
- Impostazioni in-game modificabili
- Parametri personalizzabili in `config.py`
- Supporto per diverse risoluzioni di camera
- Debug mode e visualizzazione FPS

---

## 📋 Requisiti di Sistema

### Hardware
- **Webcam** (consigliata integrata o USB)
- **CPU**: Processore moderno (Intel i5/AMD Ryzen 3+ per Windows, ARM Cortex-A72+ per Raspberry Pi)
- **RAM**: Minimo 2GB (4GB consigliato)
- **Display**: 800x600 minimo (consigliato 1920x1080)

### Software
- **Python 3.12.0** (versione consigliata per compatibilità ottimale)
- **pip 23.2.1** (o superiore) per la gestione pacchetti

### Sistema Operativo Supportati
✅ Windows 10/11  
✅ Linux (Ubuntu, Debian)  
✅ Raspberry Pi OS (bullseye/bookworm)

---

## 🚀 Installazione

### 1. Clonare il Repository
```bash
git clone https://github.com/usuario/Morra-Cinese-AI.git
cd Morra-Cinese-AI
```

### 2. Creare un Ambiente Virtuale (Consigliato)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Raspberry Pi:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installare le Dipendenze
```bash
pip install -r requirements.txt
```

### 4. Verificare l'Installazione (Opzionale)
```bash
python -c "import cv2; import mediapipe; import pygame; import numpy; print('✓ Tutte le dipendenze installate correttamente!')"
```

---

## 🎮 Come Giocare

### Avviare il Gioco
```bash
python main.py
```

### Controlli

#### Navigazione Menu
- **Mano destra verso il basso**: Sposta selezione in basso
- **Mano destra verso l'alto**: Sposta selezione in alto
- **Pugno chiuso o palmo rivolto in avanti**: Conferma selezione

#### Durante il Gioco
1. **Menu**: Seleziona "GIOCA" per iniziare una nuova partita
2. **Inserimento Nome**: Digita il tuo nome sulla tastiera (minimo 3 lettere)
3. **Gioco**: 
   - Quando appare "Fai il tuo gesto!", forma il gesto con la mano:
     - **Pugno**: Sasso ✊
     - **Palmo aperto**: Carta ✋
     - **Indice e medio aperti**: Forbice ✌️
   - Mantieni il gesto per ~1 secondo finché non viene riconosciuto
   - L'IA gioca automaticamente
4. **Risultato**: Vedi chi ha vinto il round
5. **Vittoria**: Primo a 3 punti vince!

#### Tasti Speciali
- **ESC**: Esci dal gioco
- **ENTER**: Conferma nei menu di testo
- **BACKSPACE**: Cancella carattere durante l'inserimento nome

### Schermate Disponibili

| Schermata | Descrizione |
|-----------|-------------|
| **Menu Principale** | Seleziona: Gioca, Classifica, Impostazioni, Esci |
| **Gioco** | Arena principale con webcam e area di gioco |
| **Classifica** | Top 10 migliori punteggi storici |
| **Impostazioni** | Personalizza feedback camera, FPS, segnali sonori |
| **Fine Partita** | Risultato finale e opzioni next |

---

## 📁 Struttura del Progetto

```
Morra-Cinese-AI/
├── main.py                    # Entry point principale del gioco
├── config.py                  # Configurazione globale (risoluzioni, colori, parametri)
├── requirements.txt           # Dipendenze Python
├── highscores.json           # Database dei punteggi (autogenerato)
├── README.md                 # Questo file
│
├── game/                     # Logica di gioco
│   ├── __init__.py
│   ├── game_logic.py         # Regole sasso-carta-forbice, turni, punteggi
│   ├── game_state.py         # Gestione stati (menu, gioco, pausa, risultati)
│   └── highscore.py          # Gestione classifica e persistenza dati
│
├── gesture/                  # Riconoscimento gesti
│   ├── __init__.py
│   └── hand_detector.py      # MediaPipe hand detection e recognition
│
└── ui/                       # Interfaccia Utente
    ├── __init__.py
    ├── renderer.py           # Rendering grafico con Pygame
    └── screens.py            # Implementazione delle varie schermate
```

### Moduli Principali

#### 🎯 `game/`
- **game_logic.py**: Implementa le regole del gioco (chi vince tra sasso-carta-forbice)
- **game_state.py**: State machine per gestire transizioni (Menu → Gioco → Risultati)
- **highscore.py**: Carica/salva punteggi in JSON, gestisce classifica

#### 👆 `gesture/`
- **hand_detector.py**: Usa MediaPipe per rilevare le mani e riconoscere i gesti in tempo reale

#### 🎨 `ui/`
- **renderer.py**: Disegna elementi grafici (testi, bottoni, particelle, animazioni)
- **screens.py**: Implementa le varie schermate (menu, gioco, classifica, etc.)

#### ⚙️ `config.py`
- Colori, dimensioni schermo, parametri camera
- Testi e messaggi dell'interfaccia
- Impostazioni audio e debug

---

## ⚙️ Configurazione Personalizzata

Modifica `config.py` per personalizzare il gioco:

```python
# Dimensioni schermo
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FULLSCREEN = True  # Avvia a schermo intero

# Camera
CAMERA_INDEX = 0      # Indice webcam (0=default, 1=second camera)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FLIP = True    # Specchia l'immagine orizzontalmente

# Gameplay
ROUNDS_TO_WIN = 3           # Punti per vincere una partita
GESTURE_HOLD_TIME = 1.0     # Secondi per confermare un gesto
COUNTDOWN_TIME = 3          # Countdown secondi

# Visibilità
DEBUG_MODE = False          # Mostra info debug
SHOW_FPS = True            # Mostra FPS in alto a destra
SHOW_HAND_LANDMARKS = True # Mostra punti mano rilevati
```

---

## 🔧 Risoluzione Problemi

### "Camera non trovata"
**Problema**: Il messaggio `Camera non disponibile` appare all'avvio
```
Soluzione:
1. Verificare che la webcam sia collegata
2. Controllare permessi accesso camera (Windows: Impostazioni > Privacy > Fotocamera)
3. Testare con: python -c "import cv2; cap = cv2.VideoCapture(0)"
4. Provare a cambiare CAMERA_INDEX in config.py (es. da 0 a 1)
```

### Riconoscimento gesti impreciso
```
Soluzione:
1. Aumentare la luce ambientale
2. Tenere la mano a 30-60cm dalla webcam
3. Adjustare GESTURE_HOLD_TIME in config.py (aumentare se poco preciso)
4. Assicurarsi che la camera sia stabile e non mossa
```

### Gioco in lag/basso FPS
```
Soluzione:
1. Ridurre la risoluzione camera in config.py (CAMERA_WIDTH, CAMERA_HEIGHT)
2. Chiudere altre applicazioni pesanti
3. Su Raspberry Pi: eseguire `sudo raspi-config` > Performance > GPU Memory: 256MB
```

### Errore "ModuleNotFoundError"
```
Soluzione:
1. Verificare di essere nell'ambiente virtuale attivato
2. Reinstallare: pip install -r requirements.txt
3. Su Raspberry Pi: pip install -r requirements.txt --no-cache-dir
```

---

## 📊 Architettura Software

### Pattern di Design

```
┌─────────────────┐
│   main.py       │ ← Entry point
│ (Game Loop)     │
└────────┬────────┘
         │
    ┌────┴──────┬──────────┬──────────┐
    │            │          │          │
    v            v          v          v
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│ Camera  │ │  Hand   │ │   Game   │ │    UI    │
│ Manager │ │Detector │ │  Logic   │ │ Renderer │
└─────────┘ └─────────┘ └──────────┘ └──────────┘
                             │
                             v
                    ┌──────────────────┐
                    │ State Manager    │
                    │ (Transizioni)    │
                    └──────────────────┘
                             │
                             v
                    ┌──────────────────┐
                    │HighScore Manager │
                    │ (JSON persistence)
                    └──────────────────┘
```

### Flusso di Gioco

1. **Inizializzazione**: Carica config, setup camera, init moduli
2. **Menu Loop**: User seleziona opzione
3. **Game Loop**:
   - Cattura frame da webcam
   - Rileva mani e riconosce gesti
   - State machine gestisce transizioni
   - Renderer disegna frame
4. **Fine Partita**: Salva punteggio
5. **Cleanup**: Rilascia risorse (camera, finestra)

---

## 🎯 Funzionalità Avanzate

### Sistema di Stati Avanzato
- Transizioni smooth tra schermate
- Callback on_enter/on_exit per ogni stato
- State data condiviso tra schermate

### Effetti Visivi
- **Particelle**: Esplosioni quando vinci/perdi
- **Animazioni**: Fade in/out, scaling, rotazioni
- **Glow Effects**: Evidenziazione UI
- **Shake Camera**: Effetto impatto sui risultati

### Riconoscimento Gesti Robusto
- Tracking temporale per evitare falsi positivi
- Soglie di confidenza personalizzabili
- Visualizzazione landmark mani in debug

### Persistenza Dati
- Classifica salvata in JSON
- Data/ora automatica per ogni entry
- Limite automatico Top 10

---

## 🤝 Contribuire

Suggerimenti per contribuire:

1. **Bug Reports**: Apri una issue con:
   - OS e versione Python
   - Messaggio di errore completo
   - Passi per riprodurre

2. **Miglioramenti**:
   - Fork il repository
   - Crea un branch (`git checkout -b feature/miglioramento`)
   - Commit e push
   - Apri una Pull Request

3. **Idee Future**:
   - Multiplayer (2 giocatori locali)
   - Difficoltà progressive
   - Sound effects e musica
   - Tema scuro/chiaro
   - Statistiche dettagliate per giocatore

---

## 📝 Licenza

Questo progetto è distribuito sotto licenza **MIT**. Vedi il file `LICENSE` per dettagli.

---

## 👨‍💻 Autore

**Sviluppato da**: Classe 4a  
**Repository**: [Morra-Cinese-AI](https://github.com/IDanK0/Morra-Cinese-AI)

---

## 🙏 Riconoscimenti

- **MediaPipe**: Framework di Google per computer vision
- **OpenCV**: Elaborazione video e acquisizione camera
- **Pygame**: Framework per il rendering grafico
- **NumPy**: Calcoli numerici e array operations

---

## 📞 Supporto

Per problemi o domande:
1. Controlla la sezione [Risoluzione Problemi](#-risoluzione-problemi)
2. Apri un'issue su GitHub

---

**Buon gioco! 🚀**
