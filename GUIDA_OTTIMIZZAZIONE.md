# 🎯 Suggerimenti per Ottimizzazione Fine-Tuning

## Parametri da Regolare in base al Tuo Setup

### 1. Se il Pugno NON viene Riconosciuto Facilmente

**Sintomo**: Devi chiudere molto forte la mano per far riconoscere il sasso

**Soluzione**: Aumenta `fist_closure_threshold` in `config.py`

```python
GESTURE_DETECTION = {
    # ...
    'fist_closure_threshold': 2.0,  # Era 1.8, aumenta a 2.0 o 2.2
    # ...
}
```

**Valori consigliati**:
- Mani piccole: `2.2 - 2.5`
- Mani medie: `1.8 - 2.0` (default)
- Mani grandi: `1.5 - 1.8`

---

### 2. Se le Forbici NON vengono Riconosciute

**Sintomo**: Fai la V ma viene riconosciuto altro o "none"

**Soluzione**: Riduci le soglie della V in `config.py`

```python
GESTURE_DETECTION = {
    # ...
    'scissors_v_ratio_excellent': 1.2,  # Era 1.3
    'scissors_v_ratio_good': 1.0,       # Era 1.1
    # ...
}
```

**Suggerimenti**:
- Se fai V strette: riduci entrambi i valori di 0.1-0.2
- Se fai V larghe: mantieni default o aumenta leggermente

---

### 3. Se ci Sono Troppi Falsi Positivi

**Sintomo**: Il sistema riconosce gesti quando non vuoi o cambia frequentemente

**Soluzione A - Aumenta confidenza minima**:
```python
GESTURE_DETECTION = {
    'min_detection_confidence': 0.8,  # Era 0.7
    'min_tracking_confidence': 0.8,   # Era 0.7
    # ...
}
```

**Soluzione B - Aumenta smoothing temporale**:
```python
GESTURE_DETECTION = {
    # ...
    'temporal_smoothing_frames': 7,  # Era 5, più frame = più stabile
    # ...
}
```

---

### 4. Se il Riconoscimento è Troppo Lento

**Sintomo**: Devi mantenere il gesto troppo a lungo prima che venga riconosciuto

**Soluzione A - Riduci smoothing**:
```python
GESTURE_DETECTION = {
    # ...
    'temporal_smoothing_frames': 3,  # Era 5, meno frame = più veloce
    # ...
}
```

**Soluzione B - Riduci hold time** in `config.py` (riga ~24):
```python
GESTURE_HOLD_TIME = 0.5  # Era 1.0 secondi
```

---

### 5. Se le Dita NON vengono Riconosciute Correttamente

**Sintomo**: Carta non riconosciuta, o forbici confuse

**Soluzione**: Regola margini estensione dita

```python
GESTURE_DETECTION = {
    # ...
    'finger_extension_margin': 0.015,  # Era 0.02, riduci per dita più facili
    'finger_extension_distance_ratio': 1.1,  # Era 1.15
    # ...
}
```

**Effetti**:
- ↓ `finger_extension_margin` → Dita riconosciute più facilmente come estese
- ↓ `finger_extension_distance_ratio` → Riconoscimento più permissivo

---

## Preset Consigliati

### Preset: ALTA PRECISIONE (gioco competitivo)
```python
GESTURE_DETECTION = {
    'min_detection_confidence': 0.8,
    'min_tracking_confidence': 0.8,
    'temporal_smoothing_frames': 7,
    'fist_closure_threshold': 1.7,
    'scissors_v_ratio_excellent': 1.4,
    'scissors_v_ratio_good': 1.2,
    'finger_extension_margin': 0.025,
    'finger_extension_distance_ratio': 1.2,
}
```
**Caratteristiche**: Pochi falsi positivi, richiede gesti precisi

---

### Preset: ALTA VELOCITÀ (gioco casual)
```python
GESTURE_DETECTION = {
    'min_detection_confidence': 0.6,
    'min_tracking_confidence': 0.6,
    'temporal_smoothing_frames': 3,
    'fist_closure_threshold': 2.0,
    'scissors_v_ratio_excellent': 1.2,
    'scissors_v_ratio_good': 1.0,
    'finger_extension_margin': 0.015,
    'finger_extension_distance_ratio': 1.1,
}
```
**Caratteristiche**: Risposta veloce, più tollerante, possibili falsi positivi

---

### Preset: BILANCIATO (default consigliato)
```python
GESTURE_DETECTION = {
    'min_detection_confidence': 0.7,
    'min_tracking_confidence': 0.7,
    'temporal_smoothing_frames': 5,
    'fist_closure_threshold': 1.8,
    'scissors_v_ratio_excellent': 1.3,
    'scissors_v_ratio_good': 1.1,
    'finger_extension_margin': 0.02,
    'finger_extension_distance_ratio': 1.15,
}
```
**Caratteristiche**: Buon compromesso velocità/precisione

---

## Ottimizzazione per Condizioni Specifiche

### Illuminazione Scarsa
```python
GESTURE_DETECTION = {
    'min_detection_confidence': 0.6,  # Riduci per compensare
    'min_tracking_confidence': 0.6,
    'temporal_smoothing_frames': 7,   # Aumenta per stabilità
    # ... resto default
}
```

### Webcam di Bassa Qualità
```python
GESTURE_DETECTION = {
    'min_detection_confidence': 0.65,
    'min_tracking_confidence': 0.65,
    'temporal_smoothing_frames': 6,
    'finger_extension_margin': 0.025,  # Più tollerante
    # ... resto default
}
```

### Raspberry Pi (prestazioni limitate)
```python
# In config.py, riduci anche la risoluzione:
CAMERA_WIDTH = 480   # Era 640
CAMERA_HEIGHT = 360  # Era 480
FPS = 30  # Era 60

GESTURE_DETECTION = {
    'min_detection_confidence': 0.65,
    'min_tracking_confidence': 0.65,
    'temporal_smoothing_frames': 4,  # Ridotto per performance
    # ... resto default
}
```

---

## Calibrazione Interattiva

### Procedura Consigliata

1. **Esegui test_gestures.py**
   ```bash
   python test_gestures.py
   ```

2. **Osserva i valori di confidenza**
   - Sasso: dovrebbe essere > 0.85
   - Carta: dovrebbe essere > 0.80
   - Forbici: dovrebbe essere > 0.75

3. **Regola parametri in base ai risultati**
   - Se confidenza troppo bassa → parametri più permissivi
   - Se troppi falsi positivi → parametri più restrittivi

4. **Itera fino a risultati ottimali**

---

## Metriche Target per Calibrazione Ottimale

| Metrica | Valore Target | Come Misurare |
|---------|---------------|---------------|
| Confidenza Sasso | > 0.90 | test_gestures.py |
| Confidenza Carta | > 0.85 | test_gestures.py |
| Confidenza Forbici | > 0.80 | test_gestures.py |
| Stabilità (frames) | > 10 | Mantieni gesto fermo |
| Falsi positivi | < 5% | Conta gesti sbagliati su 100 frame |
| Tempo riconoscimento | < 1.0s | Dal gesto alla conferma |

---

## Diagnostica Problemi Comuni

### ❓ "Il pugno viene riconosciuto con un dito leggermente aperto"

**Causa**: Threshold chiusura pugno troppo alto  
**Soluzione**: Riduci `fist_closure_threshold` a 1.6-1.7

---

### ❓ "Le forbici vengono confuse con 'none' o altri gesti"

**Causa**: Soglia V troppo alta  
**Soluzione**: Riduci `scissors_v_ratio_good` a 1.0 o 0.9

---

### ❓ "Il gesto 'sfarfalla' continuamente tra due opzioni"

**Causa**: Smoothing insufficiente  
**Soluzione**: Aumenta `temporal_smoothing_frames` a 7-9

---

### ❓ "Carta riconosciuta anche con 4 dita"

**Causa**: Normale - è intenzionale per tolleranza  
**Soluzione**: Se vuoi 5 dita obbligatorie, modifica `recognize_gesture` in hand_detector.py:
```python
# Riga ~230 circa
if extended_count == 5:  # Cambia da >= 4 a == 5
    # ...
```

---

### ❓ "Gesti di navigazione non funzionano"

**Causa**: Potrebbero essere filtrati dal smoothing  
**Soluzione**: Riduci `temporal_smoothing_frames` a 3 per navigazione più reattiva

---

## Log e Debug

### Abilitare Log Dettagliati

Aggiungi in `main.py` nella funzione `_update_gesture_detection`:

```python
# Dopo la riga che ottiene gesture e confidence:
if DEBUG_MODE:
    print(f"Gesto: {gesture:15s} | Conf: {confidence:.2f} | Smooth: {self.current_gesture:15s} | Conf.S: {self.current_gesture_confidence:.2f}")
```

### Visualizzare Confidenza su Schermo

Modifica `ui/renderer.py` per mostrare la confidenza durante il gioco (opzionale).

---

## Backup della Configurazione

**Prima di modificare**, salva il file originale:

```bash
copy config.py config.py.backup
```

Per ripristinare:
```bash
copy config.py.backup config.py
```

---

## Conclusioni

- Inizia con il **preset BILANCIATO** (default)
- Usa **test_gestures.py** per validare
- Modifica **un parametro alla volta**
- Annota i risultati per ogni modifica
- Trova il tuo **sweet spot** personale

**Ricorda**: Non esiste una configurazione perfetta per tutti - dipende da:
- Dimensione delle tue mani
- Tipo di webcam
- Condizioni di illuminazione
- Preferenze personali (velocità vs precisione)

Buon fine-tuning! 🎮✨
