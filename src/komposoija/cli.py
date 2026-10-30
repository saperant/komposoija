"""Command line: render song files to MIDI, print their arrangement, watch for changes.

    komposoija render songs/example.py                 -> build/example.mid
    komposoija render songs/example.py --sections chorus,chorus
    komposoija render songs/example.py --watch         re-render on every save
    komposoija render songs/example.py --play          ... and play it (FluidSynth)
    komposoija render songs/example.py --wav           ... and write build/example.wav
    komposoija render songs/example.py --mp3           ... and write build/example.mp3
    komposoija show songs/example.py                   arrangement overview
"""

from __future__ import annotations

import argparse
import runpy
import sys
import time
import traceback
from pathlib import Path

from . import playback
from .mini import MiniNotationError
from .render import RenderError, render, summary, write_midi
from .song import Song

ROOT_BUILD = Path("build")


def load_song(path: Path) -> Song:
    """Run a song file and return its `song` variable."""
    if not path.is_file():
        raise SystemExit(f"error: no such song file: {path}")
    namespace = runpy.run_path(str(path), run_name="__komposoija__")
    song = namespace.get("song")
    if not isinstance(song, Song):
        raise SystemExit(f"{path}: define a variable `song = Song(...)`")
    return song


def _render_once(args: argparse.Namespace) -> Path:
    song = load_song(args.song)
    sections = [s.strip() for s in args.sections.split(",")] if args.sections else None
    rendering = render(song, sections)
    out = args.output or ROOT_BUILD / (args.song.stem + ".mid")
    write_midi(rendering, out)
    print(summary(rendering))
    print(f"\nwrote {out}", flush=True)
    if args.wav or args.mp3:
        wav = out.with_suffix(".wav") if args.wav in (True, None) else args.wav
        playback.render_wav(out, wav, args.gain)
        if args.mp3:
            mp3 = out.with_suffix(".mp3") if args.mp3 is True else args.mp3
            print(f"wrote {playback.encode_mp3(wav, mp3, args.bitrate, song.title)}", flush=True)
        if args.wav:
            print(f"wrote {wav}", flush=True)
        else:
            wav.unlink()  # only an intermediate for the MP3
    return out


def cmd_render(args: argparse.Namespace) -> int:
    if args.play:
        playback.find_soundfont()  # fail early, before rendering
        playback.fluidsynth()
    if not args.watch:
        midi = _render_once(args)
        if args.play:
            print("playing (Ctrl-C to stop)", flush=True)
            player = playback.play(midi, args.gain)
            try:
                player.wait()
            except KeyboardInterrupt:
                playback.stop(player)
        return 0

    last, player = None, None
    print(f"watching {args.song} (Ctrl-C to stop)", flush=True)
    try:
        while True:
            mtime = args.song.stat().st_mtime
            if mtime != last:
                last = mtime
                print(f"\n--- {time.strftime('%H:%M:%S')} ---")
                try:
                    midi = _render_once(args)
                    if args.play:  # restart playback with the new version
                        playback.stop(player)
                        player = playback.play(midi, args.gain)
                except Exception:  # keep watching; show the error like a live-coding REPL
                    traceback.print_exc(limit=-3)
                    sys.stderr.flush()
            time.sleep(0.4)
    except KeyboardInterrupt:
        return 0
    finally:
        playback.stop(player)


def cmd_show(args: argparse.Namespace) -> int:
    song = load_song(args.song)
    print(summary(render(song)))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="komposoija", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command", required=True)

    r = sub.add_parser("render", help="render a song file to MIDI")
    r.add_argument("song", type=Path)
    r.add_argument("-o", "--output", type=Path, help="output .mid (default: build/<song>.mid)")
    r.add_argument("--sections", help="comma-separated sections to render instead of the form")
    r.add_argument("-w", "--watch", action="store_true", help="re-render whenever the file changes")
    r.add_argument("-p", "--play", action="store_true",
                   help="play through FluidSynth (with --watch: restart on every save)")
    r.add_argument("--wav", nargs="?", const=True, type=Path, metavar="PATH",
                   help="also render audio (default: next to the .mid)")
    r.add_argument("--mp3", nargs="?", const=True, type=Path, metavar="PATH",
                   help="also render MP3 (default: next to the .mid; needs lame or ffmpeg)")
    r.add_argument("--bitrate", type=int, default=192, help="MP3 bitrate in kbit/s (default 192)")
    r.add_argument("--gain", type=float, default=playback.DEFAULT_GAIN,
                   help=f"FluidSynth master gain (default {playback.DEFAULT_GAIN})")
    r.set_defaults(func=cmd_render)

    sh = sub.add_parser("show", help="print the arrangement")
    sh.add_argument("song", type=Path)
    sh.set_defaults(func=cmd_show)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except (RenderError, MiniNotationError, playback.PlaybackError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
