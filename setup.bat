@echo off
REM ============================================================
REM Setup Morra Cinese - Portatile Interattiva
REM ============================================================
REM Questo script configura l'ambiente Python e installa
REM tutte le dipendenze necessarie per eseguire il gioco.
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   SETUP MORRA CINESE - PORTATILE
echo ========================================
echo.

REM Verifica che Python sia installato
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Python non trovato!
    echo.
    echo Scarica Python da: https://www.python.org/downloads/
    echo Assicurati di spuntare "Add Python to PATH" durante l'installazione.
    echo.
    pause
    exit /b 1
)

echo [OK] Python trovato
python --version
echo.

REM Verifica che pip sia installato
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] pip non trovato!
    pause
    exit /b 1
)

echo [OK] pip trovato
echo.

REM Aggiorna pip
echo Aggiornamento pip...
python -m pip install --upgrade pip
echo.

REM Verifica e crea ambiente virtuale (opzionale)
if not exist "venv" (
    echo Creazione ambiente virtuale...
    python -m venv venv
    echo [OK] Ambiente virtuale creato
    echo.
)

REM Attiva ambiente virtuale
echo Attivazione ambiente virtuale...
call venv\Scripts\activate.bat
echo [OK] Ambiente virtuale attivato
echo.

REM Installa dipendenze
echo Installazione dipendenze...
echo.
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Installazione dipendenze fallita!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   SETUP COMPLETATO CON SUCCESSO!
echo ========================================
echo.
echo Prossimi step:
echo 1. Esegui: run.bat
echo 2. Oppure esegui manualmente:
echo    python main.py
echo.
pause
