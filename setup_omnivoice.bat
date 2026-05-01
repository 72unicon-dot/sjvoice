@echo off
title OmniVoice Setup
chcp 65001 >nul

echo ============================================================
echo   OmniVoice Setup Helper
echo ============================================================
echo.

set "BASEDIR=%~dp0"
set "VENV=%BASEDIR%omnivoice_env"
set "PYTHON=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://www.python.org/downloads/
    pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo [OK] Python %PYVER% detected.

if exist "%VENV%" (
    echo.
    echo [Info] Existing environment found: %VENV%
    set /p "REINSTALL=Reinstall? (y/N): "
    if /i "%REINSTALL%"=="y" (
        echo Removing old environment...
        rmdir /s /q "%VENV%"
    ) else (
        echo Skipping installation.
        goto :done
    )
)

echo.
echo [1/5] Creating virtual environment...
python -m venv "%VENV%"
if errorlevel 1 ( echo [ERROR] venv failed & pause & exit /b 1 )

echo [2/5] Upgrading pip...
"%PIP%" install --upgrade pip

echo.
echo [3/5] Installing PyTorch (CUDA 11.8)...
echo       This may take 10-20 minutes depending on your connection.
"%PIP%" install torch==2.4.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu118
if errorlevel 1 ( echo [ERROR] PyTorch install failed & pause & exit /b 1 )

echo.
echo [4/5] Installing dependencies...
"%PIP%" install transformers>=5.3.0 accelerate pydub gradio tensorboardX webdataset numpy soundfile librosa
if errorlevel 1 ( echo [ERROR] Dependency install failed & pause & exit /b 1 )

echo.
echo [5/5] Installing omnivoice package...
"%PIP%" install -e "%BASEDIR%"
if errorlevel 1 ( echo [ERROR] omnivoice install failed & pause & exit /b 1 )

:done
echo.
echo ============================================================
echo   Setup complete! Run run_omnivoice.bat to start.
echo ============================================================
echo.
pause
