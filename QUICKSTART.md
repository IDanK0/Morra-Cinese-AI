# 🚀 Quick Start - Morra Cinese Portatile

**Benvenuto!** Questa guida rapida ti aiuterà ad iniziare a giocare in pochi minuti.

---

## 📥 Download

### Scarica l'eseguibile per il tuo sistema:

- **Windows**: `MorraCinese.exe` 
- **Linux**: `MorraCinese`

> 💡 Gli eseguibili sono disponibili nella sezione [Releases](https://github.com/IDanK0/Morra-Cinese-AI/releases) di GitHub

---

## ⚙️ Requisiti Minimi

Prima di iniziare, assicurati di avere:

✅ **Webcam** funzionante (integrata o USB)  
✅ **RAM**: Almeno 2GB  
✅ **Sistema**: Windows 10+ o Linux moderno  
✅ **Permessi**: Accesso alla webcam

❌ **NON** serve Python  
❌ **NON** serve installare dipendenze  
❌ **NON** serve setup complicato

---

## 🎮 Primi Passi

### Windows

1. **Scarica** `MorraCinese.exe`
2. **Doppio click** sul file
3. Se appare un avviso di sicurezza:
   - Click su "Ulteriori informazioni"
   - Click su "Esegui comunque"
4. **Concedi permessi** alla webcam quando richiesto
5. **Gioca!** 🎉

### Linux

```bash
# 1. Scarica il file MorraCinese

# 2. Rendi il file eseguibile
chmod +x MorraCinese

# 3. Avvia il gioco
./MorraCinese
```

Se richiesto, concedi i permessi alla webcam.

---

## 🎯 Come Giocare

### Navigazione Menu

Usa i **gesti della mano** per navigare:

- **Mano in basso** → Scorri verso il basso
- **Mano in alto** → Scorri verso l'alto  
- **Pugno chiuso** o **Palmo** → Conferma selezione

### Durante il Gioco

1. **Seleziona "GIOCA"** dal menu
2. **Digita il tuo nome** (usa tastiera, minimo 3 caratteri)
3. Quando appare **"Fai il tuo gesto!"**, mostra:
   - **Pugno chiuso** = Sasso ✊
   - **Palmo aperto** = Carta ✋
   - **Indice + Medio** = Forbice ✌️
4. Mantieni il gesto per ~1 secondo
5. **Vinci** arrivando per primo a 3 punti!

### Tasti Rapidi

- **ESC** → Esci
- **ENTER** → Conferma (menu testo)
- **BACKSPACE** → Cancella carattere

---

## 🎥 Consigli per il Riconoscimento

Per un'esperienza migliore:

✨ **Illuminazione**: Usa una stanza ben illuminata  
✨ **Distanza**: Tieni la mano a 30-60cm dalla webcam  
✨ **Posizione**: Centra la mano nell'inquadratura  
✨ **Stabilità**: Mantieni il gesto fermo per ~1 secondo  
✨ **Sfondo**: Evita sfondi troppo complessi o simili al colore della pelle

---

## ❓ Problemi Comuni

### Il gioco non si avvia

**Windows**:
- Installa [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- Controlla l'antivirus (potrebbe bloccare il file)

**Linux**:
```bash
# Verifica dipendenze sistema (rare)
sudo apt install libsdl2-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-ttf-2.0-0
```

### "Camera non trovata"

1. Verifica che la webcam sia collegata
2. Controlla i permessi:
   - **Windows**: Impostazioni > Privacy > Fotocamera
   - **Linux**: 
     ```bash
     sudo usermod -a -G video $USER
     # Riavvia il sistema
     ```
3. Chiudi altre app che usano la webcam (Zoom, Teams, ecc.)

### Gesti non riconosciuti

- ✋ Aumenta l'illuminazione
- 👌 Avvicina/allontana la mano dalla camera
- 🖐️ Assicurati che tutta la mano sia visibile
- 💡 Prova gesti più marcati ed esagerati

### Antivirus blocca il file

Questo è un **falso positivo** comune per eseguibili PyInstaller.

**Soluzioni**:
1. Aggiungi eccezione nell'antivirus
2. Scarica da fonte ufficiale (GitHub Releases)
3. Controlla il file su [VirusTotal](https://www.virustotal.com)

---

## 🎨 Personalizzazione

Vuoi personalizzare il gioco? Il file di configurazione si trova in:

- **Windows**: Stessa cartella di `MorraCinese.exe` → `config.py`
- **Linux**: Stessa cartella di `MorraCinese` → `config.py`

Dopo la prima esecuzione, puoi modificare:
- Risoluzione schermo
- Indice webcam
- Sensibilità gesti
- Colori e temi

---

## 📞 Supporto

Hai bisogno di aiuto?

1. Leggi la [documentazione completa](README.md)
2. Controlla i [problemi comuni](#-problemi-comuni)
3. Apri un'[issue su GitHub](https://github.com/IDanK0/Morra-Cinese-AI/issues)

---

## 🎉 Divertiti!

Ora sei pronto per giocare! Buona fortuna e che vinca il migliore! 🏆

---

**Versione Portatile** - Nessuna installazione richiesta • Pronto all'uso • 100% standalone

Made with ❤️ by the Morra Cinese team
