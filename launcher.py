"""
OmniVoice Launcher
Bootstraps the environment and launches the Gradio demo.
"""
import sys
import os
import subprocess
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)

VENV_DIR = os.path.join(BASE_DIR, "omnivoice_env")


def get_python():
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def get_pip():
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    return os.path.join(VENV_DIR, "bin", "pip")


def venv_exists():
    return os.path.isfile(get_python())


def create_venv():
    print("[OmniVoice] Creating Python virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_DIR])
    print("[OmniVoice] Virtual environment created.")


def install_packages():
    pip = get_pip()
    print("[OmniVoice] Upgrading pip...")
    subprocess.check_call([pip, "install", "--upgrade", "pip"])

    print("[OmniVoice] Installing PyTorch (CUDA 11.8)...")
    subprocess.check_call([
        pip, "install",
        "torch==2.4.0", "torchaudio==2.4.0",
        "--index-url", "https://download.pytorch.org/whl/cu118",
    ])

    print("[OmniVoice] Installing OmniVoice and dependencies...")
    subprocess.check_call([
        pip, "install",
        "transformers>=5.3.0",
        "accelerate",
        "pydub",
        "gradio",
        "tensorboardX",
        "webdataset",
        "numpy",
        "soundfile",
        "librosa",
    ])

    print("[OmniVoice] Installing omnivoice package...")
    subprocess.check_call([pip, "install", "-e", BASE_DIR])
    print("[OmniVoice] All packages installed.")


def launch_demo(args):
    python = get_python()
    cmd = [python, "-m", "omnivoice.cli.demo"]
    if args.model:
        cmd += ["--model", args.model]
    if args.port:
        cmd += ["--port", str(args.port)]
    if args.device:
        cmd += ["--device", args.device]
    if args.share:
        cmd.append("--share")
    if args.no_asr:
        cmd.append("--no-asr")

    print(f"[OmniVoice] Launching: {' '.join(cmd)}")
    os.execv(python, cmd)


def main():
    parser = argparse.ArgumentParser(
        prog="OmniVoice",
        description="OmniVoice Launcher — sets up environment and starts the Gradio demo.",
    )
    parser.add_argument("--model", default="k2-fsa/OmniVoice",
                        help="Model checkpoint or HuggingFace repo id.")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--device", default=None)
    parser.add_argument("--share", action="store_true")
    parser.add_argument("--no-asr", action="store_true")
    parser.add_argument("--reinstall", action="store_true",
                        help="Force reinstall all packages")
    args = parser.parse_args()

    if not venv_exists() or args.reinstall:
        if not venv_exists():
            create_venv()
        install_packages()

    launch_demo(args)


if __name__ == "__main__":
    main()
