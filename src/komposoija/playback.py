"""Audio via FluidSynth + a General MIDI SoundFont: render to WAV/MP3 or play live.

The SoundFont is taken from $KOMPOSOIJA_SOUNDFONT, else the first of the usual
system locations that exists. The audio driver for live playback is
$KOMPOSOIJA_AUDIO_DRIVER (default: pulseaudio, which PipeWire also serves).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

SOUNDFONT_CANDIDATES = [
    "/usr/share/sounds/sf2/default-GM.sf2",
    "/usr/share/sounds/sf2/FluidR3_GM.sf2",
    "/usr/share/soundfonts/default.sf2",
    "/usr/share/soundfonts/FluidR3_GM.sf2",
    "/usr/share/soundfonts/FluidR3_GM2-2.sf2",
]

# 0.3 keeps the example arrangement's loudest choruses below 0 dBFS (peak ~0.7).
DEFAULT_GAIN = 0.3


class PlaybackError(RuntimeError):
    pass


def fluidsynth() -> str:
    exe = shutil.which("fluidsynth")
    if not exe:
        raise PlaybackError("fluidsynth not found; install it (Ubuntu: sudo apt install fluidsynth "
                            "fluid-soundfont-gm, Fedora: sudo dnf install fluidsynth fluid-soundfont-gm)")
    return exe


def find_soundfont() -> Path:
    env = os.environ.get("KOMPOSOIJA_SOUNDFONT")
    if env:
        path = Path(env).expanduser()
        if not path.is_file():
            raise PlaybackError(f"KOMPOSOIJA_SOUNDFONT points to a missing file: {path}")
        return path
    for candidate in SOUNDFONT_CANDIDATES:
        if Path(candidate).is_file():
            return Path(candidate)
    raise PlaybackError("no General MIDI SoundFont found; install fluid-soundfont-gm or set "
                        "KOMPOSOIJA_SOUNDFONT=/path/to/soundfont.sf2")


def render_wav(midi: Path, wav: Path, gain: float = DEFAULT_GAIN, sample_rate: int = 44100) -> Path:
    wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [fluidsynth(), "-ni", "-q", "-g", str(gain), "-r", str(sample_rate),
           "-F", str(wav), str(find_soundfont()), str(midi)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not wav.is_file():
        raise PlaybackError(f"fluidsynth failed: {result.stderr.strip() or result.stdout.strip()}")
    return wav


def encode_mp3(wav: Path, mp3: Path, bitrate: int = 192, title: str | None = None) -> Path:
    """Encode a WAV file to MP3 with lame (or ffmpeg if lame is missing)."""
    mp3.parent.mkdir(parents=True, exist_ok=True)
    if lame := shutil.which("lame"):
        cmd = [lame, "--quiet", "-b", str(bitrate)] + (["--tt", title] if title else []) + [str(wav), str(mp3)]
    elif ffmpeg := shutil.which("ffmpeg"):
        cmd = [ffmpeg, "-y", "-loglevel", "error", "-i", str(wav), "-b:a", f"{bitrate}k"] \
            + (["-metadata", f"title={title}"] if title else []) + [str(mp3)]
    else:
        raise PlaybackError("no MP3 encoder found; install lame (Ubuntu/Fedora: lame) or ffmpeg")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 or not mp3.is_file():
        raise PlaybackError(f"MP3 encoding failed: {result.stderr.strip() or result.stdout.strip()}")
    return mp3


def play(midi: Path, gain: float = DEFAULT_GAIN) -> subprocess.Popen:
    """Start playing in the background; the caller may wait() on or terminate() the process."""
    driver = os.environ.get("KOMPOSOIJA_AUDIO_DRIVER", "pulseaudio")
    cmd = [fluidsynth(), "-ni", "-q", "-g", str(gain), "-a", driver, str(find_soundfont()), str(midi)]
    return subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)


def stop(process: subprocess.Popen | None) -> None:
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
