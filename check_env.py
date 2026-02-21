import sys
import importlib

checks = [
    ('python', sys.version.splitlines()[0]),
    ('pygame', 'pygame'),
    ('opencv', 'cv2'),
    ('numpy', 'numpy'),
    ('mediapipe', 'mediapipe'),
]

print('Environment diagnostic')
print('Python:', sys.executable)
print(sys.version)
print('')

for name, mod in checks[1:]:
    try:
        m = importlib.import_module(mod)
        # Special check for mediapipe solutions
        if mod == 'mediapipe':
            has_solutions = hasattr(m, 'solutions')
            print(f'{name}: installed (has solutions: {has_solutions})')
        else:
            print(f'{name}: installed')
    except Exception as e:
        print(f'{name}: NOT installed or import error -> {e}')

print('\nSuggested fixes:')
print('- Create and activate a virtualenv:')
print('  python -m venv .venv')
print('  .\\.venv\\Scripts\\Activate.ps1  (PowerShell)')
print('- Install dependencies: pip install -r requirements.txt')
print("- If MediaPipe raises 'module mediapipe has no attribute solutions', install a compatible version:\n  pip install 'mediapipe==0.8.10'  (or check project README for recommended version)")
print('\nRun: python check_env.py')
