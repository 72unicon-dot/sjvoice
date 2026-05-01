@echo off
title OmniVoice TTS Demo
chcp 65001 >nul

echo ============================================================
echo   OmniVoice - Multilingual Zero-Shot TTS
echo ============================================================
echo.

set "BASEDIR=%~dp0"
set "VENV=%BASEDIR%omnivoice_env"
set "PYTHON=%VENV%\Scripts\python.exe"
set "PIP=%VENV%\Scripts\pip.exe"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Install Python 3.10+: https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist "%PYTHON%" (
    echo [Setup] Creating virtual environment...
    python -m venv "%VENV%"
    if errorlevel 1 ( echo [ERROR] venv creation failed & pause & exit /b 1 )

    echo [Setup] Upgrading pip...
    "%PIP%" install --upgrade pip --quiet

    echo [Setup] Installing PyTorch (CUDA 11.8) -- may take 10-20 min...
    "%PIP%" install torch==2.4.0 torchaudio==2.4.0 --index-url https://download.pytorch.org/whl/cu118

    echo [Setup] Installing dependencies...
    "%PIP%" install transformers>=5.3.0 accelerate pydub gradio tensorboardX webdataset numpy soundfile librosa --quiet

    echo [Setup] Installing omnivoice package...
    "%PIP%" install -e "%BASEDIR%" --quiet

    echo [Setup] Done!
    echo.
)

set "MODEL=k2-fsa/OmniVoice"
if not "%~1"=="" set "MODEL=%~1"

echo [Start] Launching OmniVoice...
echo [Info]  Model : %MODEL%
echo [Info]  URL   : http://localhost:7860
echo.

"%PYTHON%" -m omnivoice.cli.demo --model "%MODEL%" %2 %3 %4 %5

if errorlevel 1 ( echo. & echo [ERROR] An error occurred. & pause )
pause
