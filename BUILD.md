# Windows Build (EXE)

This guide produces a Windows 10/11 x64 distributable that runs without Python.

## Prerequisites

- Windows 10/11 x64
- Python 3.12.0 (64-bit). MediaPipe often fails to build on 3.12.
- A clean virtual environment (recommended)

## Build Steps (PowerShell or CMD)

1) Create and activate a virtual environment:

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate
```

2) Install runtime dependencies and PyInstaller:

```bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

3) Build (onefile or onedir):

- Onefile (single EXE):

```bat
python -m PyInstaller --noconsole --onefile --name MorraCinese --collect-all mediapipe --collect-all cv2 --collect-all pygame main.py
```

- Onedir (portable folder):

```bat
python -m PyInstaller --noconsole --name MorraCinese --collect-all mediapipe --collect-all cv2 --collect-all pygame main.py
```

Outputs:
- Onefile: dist\MorraCinese.exe
- Onedir: dist\MorraCinese\MorraCinese.exe

## Runtime Notes

- The highscore file is created in the user AppData folder:
	- `%LOCALAPPDATA%\MorraCinese\highscores.json` (fallback: `%APPDATA%` or user home)

## Clean Machine Test (Suggested)

Use Windows Sandbox or another clean Windows VM:

1) Copy the dist output (EXE or folder) into the sandbox.
2) Run MorraCinese.exe.
3) Verify the window opens, camera feed shows, and you can exit.
4) Finish a short game to confirm highscores.json is created.

If the EXE fails to start due to missing VC++ runtime:
- Install Microsoft Visual C++ Redistributable 2015-2022 (x64).

## Troubleshooting

- MediaPipe errors on build: ensure Python 3.12.0 x64 and reinstall dependencies.
- Camera not detected: enable camera access in Windows privacy settings.
- Pygame DLL errors: rebuild using a clean venv and rerun PyInstaller.
