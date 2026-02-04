@echo off
REM ============================================================
REM Avvio Morra Cinese - Portatile Interattiva
REM ============================================================
REM Questo script avvia il gioco con le configurazioni
REM di base. Assicurati di aver eseguito setup.bat prima.
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   MORRA CINESE - PORTATILE INTERATTIVA
echo ========================================
echo.

REM Verifica se l'ambiente virtuale esiste
if exist "venv" (
    echo Attivazione ambiente virtuale...
    call venv\Scripts\activate.bat
    echo [OK] Ambiente attivato
    echo.
) else (
    echo [ATTENZIONE] Ambiente virtuale non trovato!
    echo Eseguire setup.bat prima di avviare il gioco.
    echo.
    pause
    exit /b 1
)

REM Verifica che main.py esista
if not exist "main.py" (
    echo [ERRORE] main.py non trovato!
    echo.
    pause
    exit /b 1
)

REM Avvia il gioco
echo Avvio gioco Morra Cinese...
echo.
echo Controlli:
echo - Gesti della mano per navigazione e gioco
echo - ESC per uscire
echo - Tastiera per inserire nome
echo.
echo Assicurati che la webcam sia collegata!
echo.
echo ========================================
echo.

py -3.12 main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Il gioco si è chiuso con errore!
    echo Codice errore: %errorlevel%
    echo.
    pause
    exit /b 1
)

echo.
echo Grazie per aver giocato a Morra Cinese!
echo.
pause
