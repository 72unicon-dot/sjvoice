"""
OmniVoice Launcher
Bootstraps the environment and launches the Gradio demo.
"""
import sys
import os
import subprocess
import argparse
import shutil

IS_FROZEN = getattr(sys, "frozen", False)

if IS_FROZEN:
    BASE_DIR = os.path.dirname(sys.executable)
    _parent = os.path.dirname(BASE_DIR)
    OMNIVOICE_SRC = _parent if os.path.isfile(os.path.join(_parent, "pyproject.toml")) else BASE_DIR
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    OMNIVOICE_SRC = BASE_DIR

VENV_DIR = os.path.join(BASE_DIR, "omnivoice_env")
INSTALL_MARKER = os.path.join(VENV_DIR, ".omnivoice_installed")


def find_system_python():
    """Return a real Python 3.10+ interpreter, skipping Windows Store stubs."""
    candidates = ["python", "python3", "py"]
    for name in candidates:
        path = shutil.which(name)
        if not path:
            continue
        # Skip this launcher exe
        if os.path.normcase(path) == os.path.normcase(sys.executable):
            continue
        # Skip Windows Store stub (it's an AppExecutionAlias, not a real interpreter)
        if "WindowsApps" in path:
            continue
        try:
            r = subprocess.run(
                [path, "-c", "import sys; print(sys.version_info[:2])"],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0 and eval(r.stdout.strip()) >= (3, 10):
                return path
        except Exception:
            continue

    # Second pass: allow WindowsApps path only if it actually responds
    # (some systems only have the Store version installed for real)
    for name in candidates:
        path = shutil.which(name)
        if not path:
            continue
        if os.path.normcase(path) == os.path.normcase(sys.executable):
            continue
        try:
            r = subprocess.run(
                [path, "-c", "import sys; print(sys.version_info[:2])"],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0 and eval(r.stdout.strip()) >= (3, 10):
                return path
        except Exception:
            continue

    return None


def get_venv_python():
    if sys.platform == "win32":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def pip_run(args):
    """Run pip via 'python -m pip' to avoid Windows Store pip.exe issues."""
    python = get_venv_python()
    subprocess.check_call([python, "-m", "pip"] + args)


def is_setup_complete():
    return os.path.isfile(INSTALL_MARKER)


def pause(msg="Press Enter to close..."):
    try:
        input(msg)
    except EOFError:
        pass


def create_venv(system_python):
    if os.path.isdir(VENV_DIR):
        print("[OmniVoice] Removing old/incomplete venv...")
        shutil.rmtree(VENV_DIR)
    print("[OmniVoice] Creating virtual environment at:", VENV_DIR)
    subprocess.check_call([system_python, "-m", "venv", VENV_DIR])
    print("[OmniVoice] Virtual environment created.")


def install_packages():
    print("[OmniVoice] Upgrading pip...")
    pip_run(["install", "--upgrade", "pip"])

    print("[OmniVoice] Installing PyTorch (CUDA 12.8) - may take 10-20 min...")
    pip_run([
        "install",
        "torch>=2.4", "torchaudio>=2.4",
        "--index-url", "https://download.pytorch.org/whl/cu128",
    ])

    print("[OmniVoice] Installing dependencies...")
    pip_run([
        "install",
        "transformers>=5.3.0", "accelerate", "pydub", "gradio",
        "tensorboardX", "webdataset", "numpy", "soundfile", "librosa",
    ])

    if os.path.isfile(os.path.join(OMNIVOICE_SRC, "pyproject.toml")):
        print("[OmniVoice] Installing omnivoice from:", OMNIVOICE_SRC)
        pip_run(["install", "-e", OMNIVOICE_SRC])
    else:
        print("[WARNING] omnivoice source not found at:", OMNIVOICE_SRC)

    open(INSTALL_MARKER, "w").close()
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

    print("[OmniVoice] Starting demo - open http://localhost:" + str(args.port))
    print("[OmniVoice] Command:", " ".join(cmd))
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
    print("  Exe dir  :", BASE_DIR)
    print("  Src dir  :", OMNIVOICE_SRC)
    print("  Venv dir :", VENV_DIR)
    print()

    try:
        if not is_setup_complete() or args.reinstall:
            system_python = find_system_python()
            if system_python is None:
                print("[ERROR] Python 3.10+ not found.")
                print("        Install from https://www.python.org/downloads/")
                pause()
                return 1

            print("[OmniVoice] Using system Python:", system_python)
            create_venv(system_python)
            install_packages()
            print()

        rc = launch_demo(args)

    except KeyboardInterrupt:
        print("\n[OmniVoice] Stopped.")
        rc = 0
    except Exception as e:
        import traceback
        print("\n" + "=" * 60)
        print("[ERROR] An error occurred:")
        traceback.print_exc()
        print("=" * 60)
        pause("\nPress Enter to close...")
        rc = 1

    if rc not in (0, None):
        pause("\n[OmniVoice] Exited with code " + str(rc) + ". Press Enter to close...")
    return rc or 0


if __name__ == "__main__":
    sys.exit(main())
