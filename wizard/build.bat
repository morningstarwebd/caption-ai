@echo off
setlocal

cd /d "%~dp0\.."
echo Building Caption AI Setup Wizard...

pip install pyinstaller
if errorlevel 1 (
    echo Failed to install pyinstaller.
    pause
    exit /b 1
)

set ICON_ARG=
if exist "wizard\icon.ico" (
    set ICON_ARG=--icon "wizard/icon.ico"
)

pyinstaller --onefile --windowed --name "Caption AI Setup" %ICON_ARG% wizard/wizard.py
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo Done. Executable is in the dist folder.
pause
