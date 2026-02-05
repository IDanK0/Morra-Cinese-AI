# 📦 Guida alla Compilazione - Morra Cinese Portatile

Questa guida spiega come compilare il progetto Morra Cinese in un **eseguibile standalone** per facilitare la distribuzione senza dipendenze.

---

## 🎯 Obiettivo

Creare un **singolo file eseguibile** che:
- ✅ Non richiede l'installazione di Python
- ✅ Include tutte le dipendenze necessarie
- ✅ Funziona immediatamente su qualsiasi sistema compatibile
- ✅ È facilmente distribuibile

---

## 📋 Prerequisiti per la Compilazione

### Software Richiesto
- **Python 3.8+** (consigliato 3.12)
- **pip** (gestore pacchetti Python)
- **PyInstaller** (verrà installato automaticamente dagli script di build)

### Sistema Operativo
- **Windows**: Windows 10/11
- **Linux**: Ubuntu, Debian, o distribuzioni compatibili
- **macOS**: (supporto teorico, non testato)

---

## 🔨 Compilazione

### Metodo 1: Script Automatici (Consigliato)

#### Windows
```bash
# 1. Installa le dipendenze (prima volta)
setup.bat

# 2. Compila l'eseguibile
build.bat
```

#### Linux
```bash
# 1. Installa le dipendenze (prima volta)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Compila l'eseguibile
chmod +x build.sh
./build.sh
```

### Metodo 2: Manuale

```bash
# 1. Installa PyInstaller
pip install pyinstaller

# 2. Esegui la compilazione
pyinstaller --clean --noconfirm MorraCinese.spec
```

---

## 📂 Struttura Output

Dopo la compilazione, troverai:

```
Morra-Cinese-AI/
├── dist/
│   └── MorraCinese       # ← ESEGUIBILE STANDALONE (Linux)
│   └── MorraCinese.exe   # ← ESEGUIBILE STANDALONE (Windows)
│
├── build/                # Directory temporanea (può essere eliminata)
└── MorraCinese.spec      # File di configurazione PyInstaller
```

### Dimensioni
- **Windows**: ~280-350 MB
- **Linux**: ~270-320 MB

Le dimensioni includono:
- Python runtime
- OpenCV
- MediaPipe + modelli ML
- Pygame
- NumPy e dipendenze

---

## 🚀 Distribuzione

### Cosa Distribuire
**Solo il file eseguibile** dalla cartella `dist/`:
- Windows: `MorraCinese.exe`
- Linux: `MorraCinese`

### Come Distribuire

#### 1. Comprimi l'eseguibile
```bash
# Windows (PowerShell)
Compress-Archive -Path dist\MorraCinese.exe -DestinationPath MorraCinese-Windows.zip

# Linux
zip MorraCinese-Linux.zip dist/MorraCinese
# oppure
tar -czf MorraCinese-Linux.tar.gz dist/MorraCinese
```

#### 2. Condividi il file
- Upload su GitHub Releases
- Condivisione via cloud storage (Google Drive, Dropbox)
- Distribuzione su USB

---

## ✅ Utilizzo dell'Eseguibile

### Windows
1. Doppio click su `MorraCinese.exe`
2. (Opzionale) Crea una shortcut sul desktop

### Linux
```bash
# Rendi eseguibile (se necessario)
chmod +x MorraCinese

# Avvia
./MorraCinese
```

### Requisiti Sistema Destinatario
- **Webcam** funzionante
- **RAM**: Minimo 2GB
- **CPU**: Processore moderno (Intel i3/AMD Ryzen 3 o superiore)
- **Display**: 800x600 minimo
- **Permessi**: Accesso alla webcam
- ⚠️ **NO** Python richiesto
- ⚠️ **NO** pip richiesto
- ⚠️ **NO** dipendenze da installare

---

## 🔧 Personalizzazione Build

### Modificare il File Spec

Il file `MorraCinese.spec` controlla come PyInstaller crea l'eseguibile:

```python
# Esempio personalizzazioni

# 1. Cambiare nome eseguibile
name='MioCognoMorra'

# 2. Mostrare console per debug
console=True

# 3. Aggiungere un'icona (Windows)
icon='path/to/icon.ico'

# 4. Disabilitare compressione UPX (build più veloce ma file più grande)
upx=False

# 5. Escludere moduli non necessari
excludes=[
    'tkinter',
    'matplotlib.tests',
    'unittest',
]
```

### Build per Debug

Per creare un eseguibile che mostra errori:

```bash
# Modifica in MorraCinese.spec
console=True  # Mostra finestra console
debug=True    # Abilita debug PyInstaller
```

Poi ricompila:
```bash
pyinstaller --clean --noconfirm MorraCinese.spec
```

---

## 🐛 Risoluzione Problemi

### Problema: "Build fallita - Modulo non trovato"

**Soluzione**:
```bash
# Reinstalla dipendenze
pip install -r requirements.txt --force-reinstall

# Pulisci e ricompila
rm -rf build dist
pyinstaller --clean --noconfirm MorraCinese.spec
```

### Problema: "Eseguibile troppo grande"

**Soluzioni**:
1. Usa `opencv-python-headless` invece di `opencv-python` (già fatto)
2. Escludi moduli test in `MorraCinese.spec`
3. Disabilita UPX se causa problemi

### Problema: "Errore all'avvio - DLL mancante" (Windows)

**Soluzione**:
- Installa Visual C++ Redistributable
- Link: https://aka.ms/vs/17/release/vc_redist.x64.exe

### Problema: "Camera non trovata" nell'eseguibile

**Causa**: Permessi camera negati

**Soluzione**:
- Windows: Impostazioni > Privacy > Fotocamera
- Linux: Aggiungi utente al gruppo `video`
  ```bash
  sudo usermod -a -G video $USER
  ```

### Problema: "L'eseguibile è lento ad avviarsi"

**Normale**: Il primo avvio può richiedere 5-10 secondi perché:
- Estrae librerie temporanee
- Carica modelli ML di MediaPipe
- Inizializza componenti grafici

Avvii successivi sono più veloci.

---

## 📊 Confronto Metodi Distribuzione

| Metodo | Dimensione | Setup Utente | Portabilità |
|--------|------------|--------------|-------------|
| **Eseguibile** | ~280MB | Zero | ⭐⭐⭐⭐⭐ |
| **Script + Installer** | ~50MB | Medio | ⭐⭐⭐ |
| **Solo Script** | ~10KB | Complesso | ⭐ |

---

## 🔐 Sicurezza

### Antivirus False Positive

Alcuni antivirus potrebbero segnalare l'eseguibile come sospetto:

**Perché?**
- PyInstaller crea eseguibili "packed"
- Comportamento simile a packer malware

**Soluzioni**:
1. **Firma il codice** (richiede certificato)
2. **Segnala come false positive** all'antivirus
3. **Compila su macchina pulita** per ridurre flag

### VirusTotal

Dopo la compilazione, puoi testare su VirusTotal:
```bash
# Upload su https://www.virustotal.com
```

---

## 📈 Build Ottimizzate

### Build Release (Produzione)

```bash
# File spec ottimizzato per release
console=False    # Nessuna console
debug=False      # Nessun debug
strip=False      # Mantieni simboli per crash report
upx=True         # Comprimi con UPX
```

### Build Debug (Sviluppo)

```bash
console=True     # Mostra console
debug=True       # Debug attivo
strip=False      # Mantieni simboli
upx=False        # Nessuna compressione (build veloce)
```

---

## 🎓 Risorse Aggiuntive

### Documentazione
- **PyInstaller**: https://pyinstaller.org/en/stable/
- **Spec Files**: https://pyinstaller.org/en/stable/spec-files.html
- **Hooks**: https://pyinstaller.org/en/stable/hooks.html

### Comandi Utili

```bash
# Info moduli inclusi
pyi-archive_viewer dist/MorraCinese

# Analizza dipendenze
pyi-makespec main.py --onefile

# Log dettagliato
pyinstaller --log-level=DEBUG MorraCinese.spec
```

---

## ✨ Automazione CI/CD

Per build automatiche su GitHub Actions:

```yaml
# .github/workflows/build.yml
name: Build Executables

on: [push, release]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install -r requirements.txt pyinstaller
      - name: Build
        run: pyinstaller --clean --noconfirm MorraCinese.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: MorraCinese-Windows
          path: dist/MorraCinese.exe

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt pyinstaller
      - name: Build
        run: pyinstaller --clean --noconfirm MorraCinese.spec
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: MorraCinese-Linux
          path: dist/MorraCinese
```

---

## 📝 Note Finali

### Vantaggi
✅ Distribuzione immediata  
✅ Nessuna configurazione utente  
✅ Funziona ovunque  
✅ Professional  

### Svantaggi
⚠️ File grande (inevitabile con ML)  
⚠️ Possibili false positive antivirus  
⚠️ Build separata per ogni OS  

### Raccomandazioni
1. Testa l'eseguibile su macchina pulita
2. Includi README con requisiti sistema
3. Fornisci supporto per problemi camera/permessi
4. Considera firma del codice per distribuzioni enterprise

---

**Build completata con successo! 🎉**

Per supporto, apri un'issue su GitHub.
