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

REM Verifica che sia disponibile Python 3.x
py -3 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Python 3 non trovato!
    echo.
    echo Scarica Python 3.8+ da: https://www.python.org/downloads/
    echo Assicurati di spuntare "Add Python to PATH" durante l'installazione.
    echo.
    pause
    exit /b 1
)

echo [OK] Python 3 rilevato
py -3 --version
echo.

REM Verifica che pip sia installato
py -3.12 -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] pip non trovato per Python 3.12!
    pause
    exit /b 1
)

echo [OK] pip trovato per Python 3.12
echo.

REM Aggiorna pip
echo Aggiornamento pip...
py -3.12 -m pip install --upgrade pip
echo.

REM Verifica e crea ambiente virtuale (preferisci .venv)
if not exist ".venv" (
    echo Creazione ambiente virtuale (.venv)...
    py -3 -m venv .venv
    echo [OK] Ambiente virtuale creato
    echo.
)

REM Attiva ambiente virtuale
echo Attivazione ambiente virtuale (.venv)...
call .venv\Scripts\activate.bat
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
echo    py -3.12 main.py
echo.
pause
