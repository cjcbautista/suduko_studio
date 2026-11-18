# Windows setup and run guide

## Requirements

- Windows 10 or Windows 11
- Python 3.11+ from <https://www.python.org/downloads/>
- Microsoft Edge, Chrome, or Firefox

During Python installation, enable **Add python.exe to PATH**. Git and Node.js are not required.

## Recommended: two double-click files

1. Extract the project ZIP. Do not run it from inside the ZIP preview.
2. Open the extracted `sudoku-studio` folder.
3. Double-click `setup_windows.bat`.
   - It finds `py` or `python`.
   - It creates the isolated `.venv` environment.
   - It upgrades pip and installs Flask, Waitress, pytest, and pytest-cov.
4. After setup completes, double-click `run_windows.bat`.
5. Use <http://127.0.0.1:5000> if your browser does not open automatically.
6. Press **Ctrl+C** in the server window to stop it.

Your Top 10 and theme are stored in the browser, not in the project folder.

## Manual setup in PowerShell

From the extracted folder:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python app.py
```

Run tests:

```powershell
python -m pytest
```

## Manual setup in Command Prompt

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python app.py
```

## Troubleshooting

### “Python was not found”

Install Python 3.11+ and select **Add python.exe to PATH**, then close and reopen Command Prompt. Check with:

```bat
py --version
```

### PowerShell blocks Activate.ps1

Use the project batch files, or run this before activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

This changes policy only for the current PowerShell process.

### Port 5000 is already in use

Stop the other process, or run on another port:

```powershell
.\.venv\Scripts\Activate.ps1
python -m flask --app app run --port 5050
```

Then open <http://127.0.0.1:5050>.

### The page opens but a puzzle does not load

Keep the Command Prompt server window open. Refresh once. If an error remains, stop with Ctrl+C, then run:

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements-dev.txt
python -m pytest
```

### Reset scores or theme

Use the app's **Clear** button for scores. To reset all app data, clear site data for `127.0.0.1` in your browser settings.

## Optional production-style local server

The included Waitress server can serve the app without Flask's development warning:

```bat
.venv\Scripts\activate.bat
waitress-serve --listen=127.0.0.1:5000 app:app
```
