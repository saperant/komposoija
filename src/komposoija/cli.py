"""Command line: render song files to MIDI, print their arrangement, watch for changes.

    komposoija render songs/example.py                 -> build/example.mid
    komposoija render songs/example.py --sections chorus,chorus
    komposoija render songs/example.py --watch         re-render on every save
    komposoija render songs/example.py --play          ... and play it (FluidSynth)
    komposoija render songs/example.py --play --from chorus.2:5   ... from bar 5 of the 2nd chorus
    komposoija render songs/example.py --wav           ... and write build/example.wav
    komposoija render songs/example.py --mp3           ... and write build/example.mp3
    komposoija show songs/example.py                   arrangement overview
    komposoija inspect songs/example.py                the timeline as JSON (for editors, myrcp)
"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
import time
import traceback
from pathlib import Path

from . import playback, sourcemap, timeline
from .mini import MiniNotationError
from .render import Rendering, RenderError, render, summary, write_midi
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
    """Render, write the files asked for; return the MIDI file to play."""
    song = load_song(args.song)
    sections = [s.strip() for s in args.sections.split(",")] if args.sections else None
    rendering = render(song, sections)
    out = args.output or ROOT_BUILD / (args.song.stem + ".mid")
    start = timeline.find_place(rendering, args.start) if args.start else None
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
    if start is not None and args.play:
        print(f"playing from {timeline.place_name(rendering, start.section, start.bar)} "
              f"(bar {start.index + 1}, {_clock(start.seconds)})", flush=True)
        return playback.excerpt(out, out.with_suffix(".from.mid"), float(start.beat))
    return out


def _clock(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


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


def timeline_data(path: Path, r: Rendering) -> dict:
    """The song as the myrcp companion (and other front-ends) see it: the form with
    each bar's place in time, and which section each line of the file is about."""
    song = r.song
    bars = timeline.bars(r)
    try:
        regions = sourcemap.regions(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        regions = []
    made: dict[str, int] = {}
    for reg in regions:
        if reg.lyric is None:
            made.setdefault(reg.section, reg.first)
    return {
        "title": song.title,
        "key": song.key.name,
        "tempo": song.tempo,
        "meter": f"{song.meter[0]}/{song.meter[1]}",
        "style": song.style,
        "seconds": r.total_seconds,
        "notes": len(r.notes),
        "sections": [
            {
                "name": s.name,
                "occurrence": timeline.occurrence(r, i),
                "place": timeline.place_name(r, i),
                "start_bar": s.start_bar,
                "bars": s.bars,
                "start_beat": float(s.start_beat),
                "start_seconds": s.start_seconds,
                "seconds": s.seconds,
                "tempo": s.tempo,
                "tempo_to": s.tempo_to,
                "key": s.key.name,
                "meter": f"{s.meter[0]}/{s.meter[1]}",
                "chords": [" ".join(c) if c else "%" for c in s.chords_by_bar],
                "tracks": s.tracks,
                "lyrics": song.sections[s.name].lyrics or "",
                "line": made.get(s.name, 0),
            }
            for i, s in enumerate(r.sections)
        ],
        "bars": [{"section": b.section, "bar": b.bar, "beat": float(b.beat), "seconds": b.seconds}
                 for b in bars],
        "end_beat": float(r.total_beats),
        "regions": [
            {"first": reg.first, "last": reg.last, "section": reg.section,
             "bar": reg.bar(song.sections[reg.section].bars) if reg.section in song.sections else 0,
             "lyric": reg.lyric is not None}
            for reg in regions
        ],
    }


def cmd_inspect(args: argparse.Namespace) -> int:
    """Print the timeline as JSON (and write the MIDI with -o). A song that does not
    load or render gives {"error", "traceback", "places": [{file, line}]} and exit 1."""
    try:
        song = load_song(args.song)
        rendering = render(song)
        data = timeline_data(args.song, rendering)
        if args.output:
            data["midi"] = str(write_midi(rendering, args.output).resolve())
    except (Exception, SystemExit) as e:  # noqa: BLE001 - the song is user code
        message = str(e) if isinstance(e, SystemExit) else f"{type(e).__name__}: {e}"
        song_file = args.song.resolve()
        places = []
        for frame in traceback.extract_tb(e.__traceback__):
            if Path(frame.filename).resolve() == song_file and frame.lineno:
                places.append({"file": str(song_file), "line": frame.lineno})
        if isinstance(e, SyntaxError) and e.lineno:
            places.append({"file": str(song_file), "line": e.lineno, "col": e.offset or 0})
        print(json.dumps({"error": message.removeprefix(f"{song_file}: "),
                          "traceback": "".join(traceback.format_exception(e)),
                          "places": places[-1:]}))
        return 1
    print(json.dumps(data))
    return 0


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
    r.add_argument("--from", dest="start", metavar="PLACE",
                   help="with --play: start at a place, e.g. chorus, chorus.2, chorus.2:5, or bar 33")
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

    ins = sub.add_parser("inspect", help="print the timeline and source map as JSON")
    ins.add_argument("song", type=Path)
    ins.add_argument("-o", "--output", type=Path, help="also write the MIDI file here")
    ins.set_defaults(func=cmd_inspect)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except (RenderError, MiniNotationError, playback.PlaybackError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
