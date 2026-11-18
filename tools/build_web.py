#!/usr/bin/env python3
"""Build the browser version into build/web/ with pygbag (https://pygame-web.github.io).

1. Composes every song once into web_music/<song>.ogg (composing takes seconds even on a PC
   and a browser can't do it in the background).
2. Runs pygbag, which packs the game folder into build/web/.

Needs: pygame, pygbag (python3 -m pip install pygbag) and ffmpeg on PATH (or FFMPEG=/path).
"""
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from array import array

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

from mathfighter import audio  # noqa: E402


def compose_songs(ffmpeg):
    out = os.path.join(ROOT, "web_music")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    with tempfile.TemporaryDirectory() as tmp:
        for key in audio.ORDER:
            samples = audio.compose(audio.SONGS[key], key)
            wav = os.path.join(tmp, f"{key}.wav")
            with wave.open(wav, "wb") as handle:
                handle.setnchannels(1)
                handle.setsampwidth(2)
                handle.setframerate(audio.RATE)
                handle.writeframes(array("h", (int(x * 32000) for x in samples)).tobytes())
            subprocess.run([ffmpeg, "-loglevel", "error", "-y", "-i", wav, "-c:a", "libvorbis", "-q:a", "4",
                            os.path.join(out, f"{key}.ogg")], check=True)
    size = sum(os.path.getsize(os.path.join(out, f)) for f in os.listdir(out))
    print(f"web_music: {len(audio.ORDER)} songs, {size // 1024} KB")


ffmpeg = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
if not ffmpeg:
    sys.exit("ffmpeg not found (set FFMPEG=/path/to/ffmpeg)")
compose_songs(ffmpeg)
env = dict(os.environ, PATH=os.path.dirname(os.path.abspath(ffmpeg)) + os.pathsep + os.environ.get("PATH", ""))
icon = [a for a in ("assets/icon.png", "assets/icon-256.png") if os.path.exists(os.path.join(ROOT, a))]
subprocess.run([sys.executable, "-m", "pygbag", "--build", "--title", "Math Fighter", "--app_name", "math-fighter"]
               + (["--icon", icon[0]] if icon else []) + ["."],
               cwd=ROOT, env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
if not os.path.exists(os.path.join(ROOT, "build", "web", "index.html")):
    sys.exit("pygbag did not write build/web/index.html")
print("build/web ready: upload the folder as-is")

# pygbag sometimes sizes the canvas before the game has opened its window, squeezing the game
# into a square: add a small script that keeps it the game's shape (tools/web_canvas_fix.py).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import web_canvas_fix  # noqa: E402

web_canvas_fix.apply(os.path.join(ROOT, "build", "web", "index.html"))
