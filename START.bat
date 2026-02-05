@echo off
REM ============================================================
REM Launcher per MorraCinese.exe
REM Questo script mostra informazioni prima di avviare il gioco
REM ============================================================

setlocal
cd /d "%~dp0"

echo.
echo ========================================
echo   MORRA CINESE - PORTATILE INTERATTIVA
echo ========================================
echo.
echo Benvenuto nel gioco Sasso-Carta-Forbice
echo con riconoscimento gesti in tempo reale!
echo.
echo REQUISITI:
echo [*] Webcam funzionante
echo [*] Permessi accesso camera
echo.
echo CONTROLLI:
echo [*] Gesti mano per menu e gioco
echo [*] ESC per uscire
echo [*] Tastiera per nome giocatore
echo.
echo GESTI GIOCO:
echo [*] Pugno chiuso = Sasso
echo [*] Palmo aperto = Carta
echo [*] Indice + Medio = Forbice
echo.
echo ========================================
echo.
echo Avvio del gioco in 3 secondi...
echo Premi CTRL+C per annullare
echo.

timeout /t 3 /nobreak >nul

if exist "MorraCinese.exe" (
    start "" "MorraCinese.exe"
    echo.
    echo Gioco avviato!
    echo.
    echo Se riscontri problemi:
    echo - Leggi QUICKSTART.md
    echo - Controlla README.md
    echo.
) else (
    echo.
    echo [ERRORE] MorraCinese.exe non trovato!
    echo.
    echo Assicurati di aver scaricato l'eseguibile
    echo dalla pagina GitHub Releases.
    echo.
    pause
    exit /b 1
)

timeout /t 2 >nul
