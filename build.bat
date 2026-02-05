@echo off
REM ============================================================
REM Build Script per Morra Cinese - Portatile Interattiva
REM Crea un eseguibile standalone per Windows
REM ============================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   BUILD MORRA CINESE - ESEGUIBILE
echo ========================================
echo.

REM Verifica se l'ambiente virtuale esiste, altrimenti usa Python sistema
if exist "venv" (
    echo Attivazione ambiente virtuale...
    call venv\Scripts\activate.bat
    echo [OK] Ambiente virtuale attivato
    echo.
) else (
    echo [ATTENZIONE] Ambiente virtuale non trovato, uso Python di sistema
    echo.
)

REM Verifica che PyInstaller sia installato
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] PyInstaller non trovato!
    echo.
    echo Installazione di PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo [ERRORE] Impossibile installare PyInstaller!
        pause
        exit /b 1
    )
)

echo [OK] PyInstaller trovato
echo.

REM Pulizia build precedenti
if exist "build" (
    echo Pulizia directory build precedente...
    rmdir /s /q build
)
if exist "dist" (
    echo Pulizia directory dist precedente...
    rmdir /s /q dist
)

echo.
echo Creazione eseguibile in corso...
echo Questo processo può richiedere alcuni minuti...
echo.

REM Esegui PyInstaller con il file spec
pyinstaller --clean --noconfirm MorraCinese.spec

if %errorlevel% neq 0 (
    echo.
    echo [ERRORE] Build fallita!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   BUILD COMPLETATO CON SUCCESSO!
echo ========================================
echo.
echo L'eseguibile si trova in: dist\MorraCinese.exe
echo.
echo Dimensione eseguibile:
dir dist\MorraCinese.exe | find "MorraCinese.exe"
echo.
echo Puoi distribuire il file MorraCinese.exe
echo senza necessità di installare dipendenze!
echo.
echo Note:
echo - Assicurati che il destinatario abbia una webcam
echo - Il primo avvio potrebbe richiedere qualche secondo
echo.
pause
