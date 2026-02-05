# 📋 Release Checklist - Morra Cinese

Questa checklist guida il processo di rilascio di una nuova versione eseguibile.

---

## Pre-Release

### 1. Preparazione Codice
- [ ] Tutti i test passano
- [ ] Nessun bug critico aperto
- [ ] Codice pulito e commentato
- [ ] `config.py` con valori di default ottimali
- [ ] `DEBUG_MODE = False` in `config.py`

### 2. Versioning
- [ ] Aggiorna numero versione in:
  - `config.py` (se presente variabile VERSION)
  - `README.md`
  - `CHANGELOG.md` (crea se non esiste)

### 3. Documentazione
- [ ] README.md aggiornato
- [ ] BUILD_GUIDE.md aggiornato
- [ ] QUICKSTART.md aggiornato
- [ ] Screenshot/video aggiornati

---

## Build

### 4. Preparazione Build

**Windows** (su macchina Windows):
```bash
# Pulisci build precedenti
rmdir /s /q build dist

# Setup ambiente
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

# Test applicazione
python main.py
```

**Linux** (su macchina Linux):
```bash
# Pulisci build precedenti
rm -rf build dist

# Setup ambiente
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pyinstaller

# Test applicazione
python main.py
```

### 5. Build Eseguibili

- [ ] **Build Windows**:
  ```bash
  build.bat
  # Oppure: pyinstaller --clean --noconfirm MorraCinese.spec
  ```
  
- [ ] **Build Linux**:
  ```bash
  ./build.sh
  # Oppure: pyinstaller --clean --noconfirm MorraCinese.spec
  ```

### 6. Verifica Build

**Windows**:
- [ ] File `dist/MorraCinese.exe` esiste
- [ ] Dimensione ragionevole (~250-350MB)
- [ ] Doppio click avvia senza errori
- [ ] Camera funziona
- [ ] Menu navigabile
- [ ] Gioco giocabile
- [ ] Gesti riconosciuti
- [ ] Salvataggio highscore funziona
- [ ] Chiusura pulita con ESC

**Linux**:
- [ ] File `dist/MorraCinese` esiste
- [ ] Dimensione ragionevole (~240-320MB)
- [ ] `./MorraCinese` avvia senza errori
- [ ] Camera funziona
- [ ] Menu navigabile
- [ ] Gioco giocabile
- [ ] Gesti riconosciuti
- [ ] Salvataggio highscore funziona
- [ ] Chiusura pulita con ESC

---

## Packaging

### 7. Crea Pacchetti Distribuzione

**Windows**:
```bash
# Crea archivio ZIP
cd dist
# Rinomina per chiarezza
rename MorraCinese.exe MorraCinese-v1.0-Windows.exe

# Comprimi con file supplementari
# Includi: exe, QUICKSTART.md, README.md, START.bat
powershell Compress-Archive -Path MorraCinese-v1.0-Windows.exe,../QUICKSTART.md,../README.md,../START.bat -DestinationPath MorraCinese-v1.0-Windows.zip
```

**Linux**:
```bash
# Crea archivio
cd dist
# Rinomina per chiarezza
mv MorraCinese MorraCinese-v1.0-Linux

# Crea tarball con file supplementari
tar -czf MorraCinese-v1.0-Linux.tar.gz \
    MorraCinese-v1.0-Linux \
    ../QUICKSTART.md \
    ../README.md \
    ../START.sh

# Oppure ZIP
zip MorraCinese-v1.0-Linux.zip \
    MorraCinese-v1.0-Linux \
    ../QUICKSTART.md \
    ../README.md \
    ../START.sh
```

### 8. Calcola Checksum

**Windows** (PowerShell):
```powershell
Get-FileHash MorraCinese-v1.0-Windows.zip -Algorithm SHA256
Get-FileHash MorraCinese-v1.0-Windows.exe -Algorithm SHA256
```

**Linux**:
```bash
sha256sum MorraCinese-v1.0-Linux.tar.gz > checksums.txt
sha256sum MorraCinese-v1.0-Linux >> checksums.txt
```

---

## Testing Finale

### 9. Test su Macchina Pulita

- [ ] **Windows**: Test su VM Windows pulita senza Python
  - Download e estrazione
  - Avvio eseguibile
  - Gioco completo
  - Nessun errore
  
- [ ] **Linux**: Test su VM Linux pulita
  - Download e estrazione
  - `chmod +x` e avvio
  - Gioco completo
  - Nessun errore

### 10. Test Antivirus (Opzionale ma consigliato)

- [ ] Upload su [VirusTotal](https://www.virustotal.com)
- [ ] Controlla detection rate
- [ ] Se > 2 detection, investiga e considera firma codice

---

## Release su GitHub

### 11. Prepara Release Notes

Crea file `RELEASE_NOTES_v1.0.md`:

```markdown
# Morra Cinese v1.0 - Release Notes

## 🎉 Nuove Funzionalità
- Feature 1
- Feature 2

## 🐛 Bug Fix
- Fix 1
- Fix 2

## 📦 Download

### Windows
- **File**: `MorraCinese-v1.0-Windows.zip`
- **Dimensione**: ~XXX MB
- **SHA256**: `<checksum>`

### Linux
- **File**: `MorraCinese-v1.0-Linux.tar.gz`
- **Dimensione**: ~XXX MB
- **SHA256**: `<checksum>`

## 📋 Requisiti
- Webcam
- Windows 10+ / Linux moderno
- 2GB RAM minimo

## 🚀 Quick Start
1. Scarica il file per il tuo OS
2. Estrai l'archivio
3. Avvia l'eseguibile
4. Gioca!

Per dettagli: vedi `QUICKSTART.md`
```

### 12. Crea GitHub Release

1. [ ] Vai su GitHub → Releases → Draft a new release
2. [ ] Tag version: `v1.0`
3. [ ] Release title: `Morra Cinese v1.0 - Prima Release Portatile`
4. [ ] Descrizione: Copia da `RELEASE_NOTES_v1.0.md`
5. [ ] Allega file:
   - `MorraCinese-v1.0-Windows.zip`
   - `MorraCinese-v1.0-Linux.tar.gz`
   - `checksums.txt`
   - `QUICKSTART.md`
6. [ ] Se pre-release, spunta "This is a pre-release"
7. [ ] Pubblica!

---

## Post-Release

### 13. Comunicazione

- [ ] Annuncia su README principale
- [ ] Post su social media (se applicabile)
- [ ] Notifica contributor/community
- [ ] Aggiorna documentazione wiki (se presente)

### 14. Monitoring

Nei primi giorni dopo il rilascio:

- [ ] Monitora issue su GitHub
- [ ] Rispondi a domande utenti
- [ ] Raccogli feedback
- [ ] Documenta problemi comuni
- [ ] Pianifica hotfix se necessario

### 15. Cleanup

- [ ] Archivia build files locali
- [ ] Tag git correttamente
- [ ] Aggiorna milestone/project board
- [ ] Pianifica prossima release

---

## Checklist Rapida Release

Per release successive, checklist veloce:

```
[ ] Testa codice
[ ] Aggiorna versione
[ ] Build Windows
[ ] Build Linux
[ ] Test build
[ ] Package con docs
[ ] Calcola checksum
[ ] Test VM pulita
[ ] Prepara release notes
[ ] GitHub Release
[ ] Comunica release
```

---

## Template Comunicazione Release

### GitHub Release
```
🎮 Morra Cinese v1.0 è disponibile!

Gioca a Sasso-Carta-Forbice con riconoscimento gesti!

✨ Highlights:
- Eseguibile standalone (no Python)
- Riconoscimento gesti real-time
- Interfaccia moderna
- Classifica Top 10

📥 Download per Windows e Linux disponibili.
📖 Leggi QUICKSTART.md per iniziare!

Grazie a tutti i contributor! 🙏
```

### Social Media
```
🎉 Release Alert! 🎉

Morra Cinese v1.0 è uscito!

🎮 Gioco di Sasso-Carta-Forbice
👋 Con riconoscimento gesti webcam
💾 Eseguibile standalone
🆓 Open source

Scarica ora: [link]

#GameDev #Python #OpenSource #AI
```

---

## Note Importanti

### Firma del Codice (Opzionale)
Per distribuzioni professionali, considera:
- Certificato code signing
- Riduce warning antivirus
- Aumenta fiducia utenti

### Automazione CI/CD
Per automatizzare, considera GitHub Actions:
- Build automatico su push tag
- Test automatici
- Deploy automatico su Releases

---

**Buona release! 🚀**
