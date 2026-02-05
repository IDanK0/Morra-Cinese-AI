#!/bin/bash
# ============================================================
# Build Script per Morra Cinese - Portatile Interattiva
# Crea un eseguibile standalone per Linux
# ============================================================

set -e

echo ""
echo "========================================"
echo "  BUILD MORRA CINESE - ESEGUIBILE"
echo "========================================"
echo ""

# Vai alla directory dello script
cd "$(dirname "$0")"

# Verifica se l'ambiente virtuale esiste
if [ -d "venv" ]; then
    echo "Attivazione ambiente virtuale..."
    source venv/bin/activate
    echo "[OK] Ambiente virtuale attivato"
    echo ""
else
    echo "[ATTENZIONE] Ambiente virtuale non trovato, uso Python di sistema"
    echo ""
fi

# Verifica che PyInstaller sia installato
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[ERRORE] PyInstaller non trovato!"
    echo ""
    echo "Installazione di PyInstaller..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "[ERRORE] Impossibile installare PyInstaller!"
        exit 1
    fi
fi

echo "[OK] PyInstaller trovato"
echo ""

# Pulizia build precedenti
if [ -d "build" ]; then
    echo "Pulizia directory build precedente..."
    rm -rf build
fi

if [ -d "dist" ]; then
    echo "Pulizia directory dist precedente..."
    rm -rf dist
fi

echo ""
echo "Creazione eseguibile in corso..."
echo "Questo processo può richiedere alcuni minuti..."
echo ""

# Esegui PyInstaller con il file spec
pyinstaller --clean --noconfirm MorraCinese.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERRORE] Build fallita!"
    echo ""
    exit 1
fi

echo ""
echo "========================================"
echo "  BUILD COMPLETATO CON SUCCESSO!"
echo "========================================"
echo ""
echo "L'eseguibile si trova in: dist/MorraCinese"
echo ""
echo "Dimensione eseguibile:"
ls -lh dist/MorraCinese | awk '{print $5, $9}'
echo ""
echo "Puoi distribuire il file MorraCinese"
echo "senza necessità di installare dipendenze!"
echo ""
echo "Note:"
echo "- Assicurati che il destinatario abbia una webcam"
echo "- Potrebbero essere necessari permessi di esecuzione:"
echo "  chmod +x dist/MorraCinese"
echo "- Il primo avvio potrebbe richiedere qualche secondo"
echo ""
