"""
OmniVoice Launcher
Bootstraps the environment and launches the Gradio demo.
"""
import sys
import os
import subprocess
import argparse
import shutil

# When frozen by PyInstaller, sys.executable is the .exe itself.
# We need to locate a real Python interpreter separately.
IS_FROZEN = getattr(sys, "frozen", False)
BASE_DIR = os.path.dirname(sys.executable) if IS_FROZEN else os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "omnivoice_env")


def find_system_python():
    """Return a path to a usable Python 3.10+ interpreter (not this exe)."""
    # When frozen, sys.executable is OmniVoice.exe — we must find a real python.
    candidates = ["python", "python3", "py"]
    for name in candidates:
        path = shutil.which(name)
        if path and os.path.normcase(path) != os.path.normcase(sys.executable):
            try:
                result = subprocess.run(
                    [path, "-c", "import sys; print(sys.version_info[:2])"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    ver = eval(result.stdout.strip())
                    if ver >= (3, 10):
                        return path
            except Exception:
                continue
    return None


def get_venv_python():
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def get_venv_pip():
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    return os.path.join(VENV_DIR, "bin", "pip")


def venv_exists():
    return os.path.isfile(get_venv_python())


def create_venv(system_python):
    print("[OmniVoice] Creating virtual environment at:", VENV_DIR)
    subprocess.check_call([system_python, "-m", "venv", VENV_DIR])
    print("[OmniVoice] Virtual environment created.")


def install_packages():
    pip = get_venv_pip()
    print("[OmniVoice] Upgrading pip...")
    subprocess.check_call([pip, "install", "--upgrade", "pip"])

    print("[OmniVoice] Installing PyTorch (CUDA 11.8) — may take 10-20 min...")
    subprocess.check_call([
        pip, "install",
        "torch==2.4.0", "torchaudio==2.4.0",
        "--index-url", "https://download.pytorch.org/whl/cu118",
    ])

    print("[OmniVoice] Installing dependencies...")
    subprocess.check_call([
        pip, "install",
        "transformers>=5.3.0", "accelerate", "pydub", "gradio",
        "tensorboardX", "webdataset", "numpy", "soundfile", "librosa",
    ])

    print("[OmniVoice] Installing omnivoice package...")
    subprocess.check_call([pip, "install", "-e", BASE_DIR])
    print("[OmniVoice] All packages installed successfully.")


def launch_demo(args):
    python = get_venv_python()
    cmd = [python, "-m", "omnivoice.cli.demo",
           "--model", args.model,
           "--port", str(args.port)]
    if args.device:
        cmd += ["--device", args.device]
    if args.share:
        cmd.append("--share")
    if args.no_asr:
        cmd.append("--no-asr")

    print(f"[OmniVoice] Starting demo — open http://localhost:{args.port}")
    print(f"[OmniVoice] Command: {' '.join(cmd)}")
    # Use subprocess.run instead of os.execv — execv is unreliable on Windows
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        prog="OmniVoice",
        description="OmniVoice Launcher: sets up environment and starts the Gradio demo.",
    )
    parser.add_argument("--model", default="k2-fsa/OmniVoice",
                        help="Model checkpoint path or HuggingFace repo id.")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--device", default=None)
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--no-asr", action="store_true")
    parser.add_argument("--reinstall", action="store_true",
                        help="Force reinstall all packages")
    args = parser.parse_args()

    print("=" * 60)
    print("  OmniVoice - Multilingual Zero-Shot TTS")
    print("=" * 60)
    print(f"  Base dir : {BASE_DIR}")
    print(f"  Venv dir : {VENV_DIR}")
    print()

    if not venv_exists() or args.reinstall:
        system_python = find_system_python()
        if system_python is None:
            print("[ERROR] Python 3.10+ not found on this system.")
            print("        Install from https://www.python.org/downloads/")
            input("Press Enter to exit...")
            return 1

        print(f"[OmniVoice] Using system Python: {system_python}")

        if not venv_exists():
            create_venv(system_python)
        install_packages()
        print()

    try:
        rc = launch_demo(args)
    except KeyboardInterrupt:
        print("\n[OmniVoice] Stopped.")
        rc = 0
    except Exception as e:
        print(f"\n[ERROR] {e}")
        input("Press Enter to exit...")
        rc = 1

    if rc != 0:
        input(f"\n[OmniVoice] Exited with code {rc}. Press Enter to close...")
    return rc


if __name__ == "__main__":
    sys.exit(main())
