#!/bin/bash
# ============================================================
# Launcher per MorraCinese
# Questo script mostra informazioni prima di avviare il gioco
# ============================================================

clear

echo ""
echo "========================================"
echo "  MORRA CINESE - PORTATILE INTERATTIVA"
echo "========================================"
echo ""
echo "Benvenuto nel gioco Sasso-Carta-Forbice"
echo "con riconoscimento gesti in tempo reale!"
echo ""
echo "REQUISITI:"
echo "[*] Webcam funzionante"
echo "[*] Permessi accesso camera"
echo ""
echo "CONTROLLI:"
echo "[*] Gesti mano per menu e gioco"
echo "[*] ESC per uscire"
echo "[*] Tastiera per nome giocatore"
echo ""
echo "GESTI GIOCO:"
echo "[*] Pugno chiuso = Sasso"
echo "[*] Palmo aperto = Carta"
echo "[*] Indice + Medio = Forbice"
echo ""
echo "========================================"
echo ""
echo "Avvio del gioco in 3 secondi..."
echo "Premi CTRL+C per annullare"
echo ""

sleep 3

# Vai alla directory dello script
cd "$(dirname "$0")"

if [ -f "MorraCinese" ]; then
    # Assicurati che sia eseguibile
    chmod +x MorraCinese 2>/dev/null
    
    # Avvia il gioco
    ./MorraCinese
    
    echo ""
    echo "Gioco terminato."
    echo ""
    echo "Se hai riscontrato problemi:"
    echo "- Leggi QUICKSTART.md"
    echo "- Controlla README.md"
    echo ""
else
    echo ""
    echo "[ERRORE] MorraCinese non trovato!"
    echo ""
    echo "Assicurati di aver scaricato l'eseguibile"
    echo "dalla pagina GitHub Releases."
    echo ""
    exit 1
fi
