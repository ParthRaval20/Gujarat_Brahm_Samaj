@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo   Gujarat Brahm Samaj - Professional Installer Builder
echo ========================================================
echo.

:: 1. Check Python virtual environment
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv\Scripts\python.exe!
    pause
    exit /b 1
)

:: 2. Ensure PyInstaller is installed
echo [1/4] Checking requirements & PyInstaller...
.venv\Scripts\python.exe -m pip install pyinstaller --quiet

:: 3. Generate App Icon from Logo if missing
echo [2/4] Verifying application icon...
.venv\Scripts\python.exe -c "import os; from PIL import Image; os.makedirs('assets/icons', exist_ok=True); img = Image.open('assets/images/logo.png'); img.save('assets/icons/app_icon.ico', format='ICO', sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])"

:: 4. Build Executable with PyInstaller
echo [3/4] Compiling GujaratBrahmSamaj.exe with PyInstaller...
.venv\Scripts\pyinstaller.exe --noconfirm GujaratBrahmSamaj.spec
if %ERRORLEVEL% neq 0 (
    echo [ERROR] PyInstaller compilation failed!
    pause
    exit /b %ERRORLEVEL%
)

:: 5. Compile Installer with Inno Setup
echo [4/4] Compiling Windows Setup Installer with Inno Setup...
set "ISCC_PATH="
if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_PATH=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"

if not defined ISCC_PATH (
    where iscc >nul 2>&1
    if %ERRORLEVEL% equ 0 set "ISCC_PATH=iscc"
)

if not defined ISCC_PATH (
    echo [WARNING] Inno Setup Compiler (ISCC.exe) not found in standard paths.
    echo Please install Inno Setup 6 or run: winget install JRSoftware.InnoSetup
    echo The standalone executable is ready in: dist\GujaratBrahmSamaj\GujaratBrahmSamaj.exe
    pause
    exit /b 0
)

"%ISCC_PATH%" installer.iss
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Inno Setup compilation failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================================
echo   BUILD SUCCESSFUL!
echo   Installer ready at:
echo   dist_installer\GujaratBrahmSamaj_Setup_v1.0.exe
echo ========================================================
echo.
pause
