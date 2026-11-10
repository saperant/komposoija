"""komposoija's song companion in myrcp: write the song in your editor, hear it here.

- komposoija.songs: the song files under $KOMPOSOIJA_SONGS (or the cwd).
- komposoija.song#<file>: one song, rendered again whenever the file is saved. Its form
  is a table (each time a section is played: its bars, where it starts, its chords),
  with a playhead while it plays; render errors are problems at their line.

Where playing starts is the start mark. The editor's cursor sets it: the section the
line is about (its song.section(...), its .play(...), .chords = ...), and on a lyric
line the bar where that line starts. space plays from the mark and stops; F9 does the
same from anywhere, the editor included (Ctrl+\\ F9 in a terminal tab). While it plays,
a save renders the song again and plays the new version from the mark, and the mark
moving with the editor's cursor restarts playback there (f turns that off). l loops
the section being played.
"""

from __future__ import annotations

import bisect
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

from komposoija import playback

from myrcp import Context, Item, Job, Marker, Plugin, Selection, View, ui

from .songs import find_songs, is_song, relative

plugin = Plugin()

_views: dict[Path, SongView] = {}  # the open songs
_last: list[SongView] = []  # the song played or shown last, for F9 outside a song
_autoplay: set[Path] = set()  # songs F9 opened, to play once they are rendered
_TITLE = re.compile(r"""Song\([^)]*?title\s*=\s*(["'])(.+?)\1""", re.DOTALL)


def song_roots(rcp: Any) -> list[Path]:
    """The preference komposoija.songs (which $KOMPOSOIJA_SONGS overrides), else the cwd."""
    paths = rcp.pref("komposoija.songs")
    if paths is None:  # a workbench without preferences
        paths = os.environ.get("KOMPOSOIJA_SONGS", "").split(os.pathsep)
    roots = [Path(p).expanduser() for p in paths if p]
    return roots or [Path.cwd()]


def cache_dir() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache")
    path = base / "myrcp" / "komposoija"
    path.mkdir(parents=True, exist_ok=True)
    return path


def inspect(path: Path, midi: Path) -> dict[str, Any]:
    """`komposoija inspect`: the song's timeline and source map, from a process of its
    own (a song file is user code); the MIDI goes to `midi`."""
    out = subprocess.run(
        [sys.executable, "-m", "komposoija", "inspect", str(path), "-o", str(midi)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    try:
        return json.loads(out.stdout)
    except ValueError:
        err = out.stderr.strip()
        raise RuntimeError(err.splitlines()[-1] if err else "komposoija inspect failed") from None


def clock(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def hints(*pairs: str) -> ui.Node:
    spans: list[Any] = []
    for k, what in zip(pairs[::2], pairs[1::2], strict=True):
        spans += [(k, "accent"), f" {what}   "]
    return ui.text(spans, "dim")


class Player:
    """One FluidSynth for the host: starting a song stops the one playing."""

    def __init__(self) -> None:
        self.proc: subprocess.Popen | None = None
        self.owner: SongView | None = None
        self.t0 = 0.0
        self.offset = 0.0  # the song's time at t0

    def start(self, owner: SongView, midi: Path, beat: float, seconds: float,
              end_beat: float | None, gain: float) -> None:
        self.stop()
        cut = midi.with_name(midi.stem + ".play.mid")
        playback.excerpt(midi, cut, beat, end_beat)
        self.proc = playback.play(cut, gain)
        self.owner, self.t0, self.offset = owner, time.monotonic(), seconds

    def stop(self) -> None:
        playback.stop(self.proc)
        self.proc, self.owner = None, None

    def position(self) -> float | None:
        """Where in the song it is, in seconds (None: not playing)."""
        return None if self.proc is None else self.offset + time.monotonic() - self.t0

    def died(self) -> int | None:
        """FluidSynth's exit status when it exited (it stays a few seconds past the end
        of the music for the notes' release, so this is a failure, not the end)."""
        return None if self.proc is None else self.proc.poll()


player = Player()


@plugin.command("komposoija.play_at_cursor")
def play_at_cursor(rcp: Context) -> None:
    """F9: play the song the editor is in from its cursor; stop when it plays."""
    if player.owner is not None:
        player.owner.stop()
        return
    for item in rcp.selection.items:
        if item.type in ("file", "problem") and item.path:
            path = Path(item.path).resolve()
            if path in _views:
                _views[path].on_selection(rcp.selection, force=True)
                _views[path].play()
                return
            if is_song(path):
                _autoplay.add(path)
                rcp.open_view("komposoija.song", str(path))
                return
    if _last:
        _last[-1].play()
    else:
        rcp.status("F9 plays the song the editor is in: open a song file", "error")


# ---------------------------------------------------------------------------------
# the list of songs


@plugin.view("komposoija.songs")
class Songs(View):
    def setup(self) -> None:
        self.paths: list[Path] = []
        self.titles: dict[Path, str] = {}
        self.scanning = False
        self.reload()

    @plugin.command("komposoija.songs.reload")
    def reload(self) -> None:
        if self.scanning:
            return
        self.scanning = True
        roots = song_roots(self.rcp)

        def work(job: Job) -> tuple[list[Path], dict[Path, str]]:
            paths = find_songs(roots)
            titles = {}
            for p in paths:
                m = _TITLE.search(p.read_text(encoding="utf-8", errors="replace"))
                titles[p] = m.group(2) if m else ""
            return paths, titles

        self.rcp.run_job("Find komposoija songs", work, on_done=self._found)

    def _found(self, job: Job) -> None:
        self.scanning = False
        if job.ok:
            self.paths, self.titles = job.result

    def on_preferences(self, changed: frozenset[str]) -> None:
        if "komposoija.songs" in changed:
            self.reload()

    def render(self) -> ui.Node:
        cwd = Path.cwd()
        rows = [
            ui.row(
                str(p),
                [relative(p, cwd), self.titles.get(p) or "",
                 time.strftime("%Y-%m-%d %H:%M", time.localtime(p.stat().st_mtime)) if p.exists() else ""],
                selection=Item("komposoija.song", relative(p, cwd), p,
                               props={"Title": self.titles.get(p) or "—"}),
            )
            for p in self.paths
        ]
        roots = ", ".join(str(r) for r in song_roots(self.rcp))
        return ui.vbox(
            ui.text([("komposoija songs under ", "dim"), (roots, "bold")]),
            ui.text(""),
            ui.table(
                "songs",
                [ui.column("File", grow=2), ui.column("Title", grow=2), ui.column("Saved", width=17)],
                rows,
                autofocus=True,
                sortable=True,
                empty="Looking for songs…" if self.scanning else "No komposoija songs here (KOMPOSOIJA_SONGS).",
                on_activate=lambda key: self.rcp.open_view("komposoija.song", key),
            ),
            hints("Enter", "open", "r", "find again"),
        )


# ---------------------------------------------------------------------------------
# a song


@plugin.view("komposoija.song")
class SongView(View):
    def setup(self) -> None:
        if not self.arg:
            raise ValueError("open a song from the komposoija view")
        self.path = Path(self.arg).resolve()
        if not self.path.is_file():
            raise ValueError(f"no such song file: {self.path}")
        digest = hashlib.sha1(str(self.path).encode()).hexdigest()[:10]
        self.midi = cache_dir() / f"{self.path.stem}-{digest}.mid"
        self.data: dict[str, Any] | None = None
        self.error = ""
        self.error_places: list[dict[str, Any]] = []
        self.rendering = False
        self.pending = False
        self.mark = (0, 0)  # the start mark: (index in the form, 0-based bar in it)
        self.loop = False
        self.follow = True
        self.cursor = ui.CursorRequest()
        self.ended = False
        self.seen = self._mtime()
        self.stop_event = threading.Event()
        _views[self.path] = self
        threading.Thread(target=self._watch, daemon=True).start()
        self.render_song()

    def title(self) -> str:
        name = (self.data or {}).get("title") or self.path.stem
        return f"{'▶' if player.owner is self else '♪'} {name}"

    def dispose(self) -> None:
        self.stop_event.set()
        if player.owner is self:
            player.stop()
        if _views.get(self.path) is self:
            del _views[self.path]
        if self in _last:
            _last.remove(self)
        self.rcp.set_markers(self._marker_set(), [])

    # -- rendering the song ------------------------------------------------------------
    def _mtime(self) -> float:
        try:
            return self.path.stat().st_mtime
        except OSError:
            return 0.0

    def _watch(self) -> None:
        """Render again when the file is saved (in any editor); move the playhead."""
        shown, n = None, 0
        while not self.stop_event.wait(0.1):
            n += 1
            if n % 5 == 0 and (m := self._mtime()) != self.seen:
                self.seen = m
                self.rcp.call_soon(self.render_song)
            if player.owner is self:
                self.rcp.call_soon(self._tick)
                pos = player.position() or 0.0
                now = (self._at(pos), int(pos))  # the playhead's bar and the clock
                if now != shown:
                    shown = now
                    self.invalidate()

    @plugin.command("komposoija.render")
    def render_song(self) -> None:
        if self.rendering:
            self.pending = True
            return
        self.rendering = True
        self.rcp.run_job(f"Render {self.path.name}", lambda job: inspect(self.path, self.midi),
                         on_done=self._rendered)

    def _rendered(self, job: Job) -> None:
        self.rendering = False
        first = self.data is None
        if not job.ok:
            self.error, self.error_places = str(job.error), []
        elif "error" in job.result:
            self.error = job.result["error"]
            self.error_places = job.result.get("places", [])
            self.rcp.status(f"{self.path.name}: {self.error}", "error")
        else:
            old, self.data = self.data, job.result
            self.error, self.error_places = "", []
            self.mark = self._same_place(old, self.mark)
            d = self.data
            self.rcp.status(f"{d['title']}: {len(d['bars'])} bars, {clock(d['seconds'])}", "ok")
            if first:
                self.on_selection(self.rcp.selection)
            if self.path in _autoplay:
                _autoplay.discard(self.path)
                self.play()
            elif player.owner is self:  # you hear the new version from the mark
                self._start()
        self._publish()
        if self.pending:
            self.pending = False
            self.render_song()

    def _same_place(self, old: dict[str, Any] | None, mark: tuple[int, int]) -> tuple[int, int]:
        """The mark in a new rendering: the same section and time it is played, else the start."""
        assert self.data is not None
        sections = self.data["sections"]
        if old is not None and mark[0] < len(old["sections"]):
            place = old["sections"][mark[0]]["place"]
            for i, s in enumerate(sections):
                if s["place"] == place:
                    return i, min(mark[1], s["bars"] - 1)
        return (0, 0) if sections else mark

    # -- the start mark ----------------------------------------------------------------
    def on_selection(self, selection: Selection, force: bool = False) -> None:
        """A line of the song file (the editor's cursor, a problem): the mark goes to the
        section it is about; on a lyric line, to the bar the line starts."""
        if self.data is None or (selection.view == self.view_id and not force):
            return
        for item in selection.items:
            if item.type not in ("file", "problem") or not item.path or item.line <= 0:
                continue
            if Path(item.path).resolve() != self.path:
                return
            holding = [r for r in self.data["regions"] if r["first"] <= item.line <= r["last"]]
            if not holding:
                return
            region = min(holding, key=lambda r: (r["last"] - r["first"], not r["lyric"]))
            sections = self.data["sections"]
            played = [i for i, s in enumerate(sections) if s["name"] == region["section"]]
            if not played:
                self.rcp.status(f"{region['section']} is not in the form (song.arrange)")
                return
            at = self.mark[0] if self.mark[0] in played else played[0]
            self._set_mark(at, region["bar"], by_editor=True)
            return

    def _set_mark(self, section: int, bar: int, by_editor: bool = False) -> None:
        assert self.data is not None
        mark = (section, max(0, min(bar, self.data["sections"][section]["bars"] - 1)))
        if mark == self.mark:
            return
        self.mark = mark
        self.cursor.move(section)
        if player.owner is self and (self.follow or not by_editor):
            self._start()

    def _select_row(self, key: str) -> None:
        if self.data is not None and int(key) != self.mark[0]:
            self.mark = (int(key), 0)

    @plugin.command("komposoija.earlier")
    def earlier(self) -> None:
        self._step(-1)

    @plugin.command("komposoija.later")
    def later(self) -> None:
        self._step(1)

    def _step(self, by: int) -> None:
        if self.data is None:
            return
        bars = self.data["bars"]
        n = max(0, min(len(bars) - 1, self._bar_index(self.mark) + by))
        self._set_mark(bars[n]["section"], bars[n]["bar"])

    def _bar_index(self, mark: tuple[int, int]) -> int:
        assert self.data is not None
        return self.data["sections"][mark[0]]["start_bar"] + mark[1]

    # -- playing -----------------------------------------------------------------------
    @plugin.command("komposoija.play")
    def play(self) -> None:
        """Play from the mark; stop when this song plays."""
        if player.owner is self:
            self.stop()
        elif self.data is None:
            self.rcp.status(self.error or "Rendering…", "error" if self.error else "normal")
        else:
            self._start()

    def stop(self) -> None:
        player.stop()
        self.invalidate()

    def _start(self) -> None:
        assert self.data is not None
        d = self.data
        start = d["bars"][self._bar_index(self.mark)]
        end = self._loop_end() if self.loop else None
        try:
            gain = (self.rcp.pref("komposoija.gain") or 30) / 100
            player.start(self, self.midi, start["beat"], start["seconds"], end, gain)
        except (playback.PlaybackError, OSError) as e:
            self.rcp.status(str(e), "error")
            return
        self.ended = False
        if self in _last:
            _last.remove(self)
        _last.append(self)
        self.invalidate()

    def _loop_end(self) -> float:
        """The beat where the mark's section ends."""
        assert self.data is not None
        sections = self.data["sections"]
        i = self.mark[0]
        return sections[i + 1]["start_beat"] if i + 1 < len(sections) else self.data["end_beat"]

    def _tick(self) -> None:
        """While playing: loop, see the end, notice FluidSynth failing."""
        if player.owner is not self or self.data is None:
            return
        pos = player.position() or 0.0
        if (status := player.died()) is not None and status != 0:
            player.stop()
            self.rcp.status(f"Playback stopped: fluidsynth exited with {status} "
                            "(KOMPOSOIJA_AUDIO_DRIVER, KOMPOSOIJA_SOUNDFONT)", "error")
        elif self.loop:
            s = self.data["sections"][self.mark[0]]
            if pos >= s["start_seconds"] + s["seconds"]:
                self._start()
        elif pos >= self.data["seconds"]:
            player.owner = None  # its release rings out; the process exits by itself
            self.ended = True
            self.invalidate()

    @plugin.command("komposoija.loop")
    def toggle_loop(self) -> None:
        self.loop = not self.loop
        self.rcp.status(f"Loop {'on: the section being played, again and again' if self.loop else 'off'}")
        if player.owner is self:
            self._start()

    @plugin.command("komposoija.follow")
    def toggle_follow(self) -> None:
        self.follow = not self.follow
        self.rcp.status("While playing, the editor's cursor " + (
            "restarts playback where it moves" if self.follow else "only moves the start mark"))

    def _at(self, seconds: float) -> tuple[int, int] | None:
        """(section, bar) sounding at this time of the song."""
        if self.data is None or not self.data["bars"]:
            return None
        bars = self.data["bars"]
        i = max(0, bisect.bisect_right([b["seconds"] for b in bars], seconds) - 1)
        return bars[i]["section"], bars[i]["bar"]

    # -- problems and editing ------------------------------------------------------------
    def _marker_set(self) -> str:
        return f"komposoija:{self.path}"

    def _publish(self) -> None:
        markers = []
        if self.error:
            view = f"komposoija.song#{self.path}"
            places = self.error_places or [{"file": str(self.path), "line": 1}]
            markers = [Marker(self.error, p["file"], p["line"], p.get("col", 0), "error", "komposoija", view)
                       for p in places]
        self.rcp.set_markers(self._marker_set(), markers)

    @plugin.command("komposoija.edit")
    def edit(self) -> None:
        line = 0
        if self.data is not None:
            line = self.data["sections"][self.mark[0]]["line"]
        self.rcp.open_in_editor(self.path, line or None,
                                on_close=lambda waited: self.render_song() if waited else None)

    def _goto_row(self, key: str) -> None:
        """Enter on a row: play from there (from the mark when it is in that row)."""
        if self.data is None:
            return
        i = int(key)
        self._set_mark(i, self.mark[1] if i == self.mark[0] else 0)
        if player.owner is not self:
            self._start()

    # -- the view ----------------------------------------------------------------------
    def _transport(self) -> ui.Node:
        assert self.data is not None
        d = self.data
        sections = d["sections"]
        mark = sections[self.mark[0]]
        mark_bar = d["bars"][self._bar_index(self.mark)]
        place = mark["place"] + (f":{self.mark[1] + 1}" if self.mark[1] else "")
        spans: list[Any]
        if player.owner is self and (pos := player.position()) is not None:
            at = self._at(pos) or (0, 0)
            s = sections[at[0]]
            spans = [("▶ ", "ok"), (f"{s['place']}  bar {at[1] + 1}/{s['bars']}", "bold"),
                     f"   {clock(pos)} / {clock(d['seconds'])}"]
        else:
            spans = [("■ ", "dim"), ("stopped" if not self.ended else "played to the end", "dim")]
        spans += ["    start mark ", (place, "accent"),
                  (f"  bar {mark_bar_no(d, self.mark)}, {clock(mark_bar['seconds'])}", "dim"),
                  "    loop ", ("on" if self.loop else "off", "accent" if self.loop else "dim"),
                  "  follow ", ("on" if self.follow else "off", "accent" if self.follow else "dim")]
        return ui.text(spans)

    def _bars_strip(self) -> ui.Node:
        """The chords of the mark's section, bar by bar: the mark and the playhead."""
        assert self.data is not None
        i = self.mark[0]
        s = self.data["sections"][i]
        playing = None
        if player.owner is self and (pos := player.position()) is not None:
            playing = self._at(pos)
        spans: list[Any] = [(f"{s['place']}  ", "bold"), ("|", "dim")]
        for b, chord in enumerate(s["chords"]):
            style = "ok" if playing == (i, b) else ("accent" if b == self.mark[1] else "normal")
            text = f"▸{chord}" if b == self.mark[1] else f" {chord}"
            spans += [(f"{text} ", style), ("|", "dim")]
        return ui.text(spans, wrap=True)

    def _lyrics(self) -> list[ui.Node]:
        assert self.data is not None
        s = self.data["sections"][self.mark[0]]
        lines = [ln.strip() for ln in s["lyrics"].splitlines() if ln.strip()]
        out = []
        for k, ln in enumerate(lines):
            starts = min(s["bars"] - 1, k * s["bars"] // len(lines))
            out.append(ui.text([(f"  bar {starts + 1:>2}  ", "dim"),
                                (ln, "accent" if starts == self.mark[1] else "normal")]))
        return out

    def _form(self) -> ui.Node:
        assert self.data is not None
        d = self.data
        playing = None
        if player.owner is self and (pos := player.position()) is not None:
            playing = (self._at(pos) or (None,))[0]
        rows = []
        for i, s in enumerate(d["sections"]):
            flag = "▶" if i == playing else ("◆" if i == self.mark[0] else "")
            extra = []
            if s["tempo_to"]:
                extra.append(f"{s['tempo']:g}→{s['tempo_to']:g} BPM")
            elif s["tempo"] != d["tempo"]:
                extra.append(f"{s['tempo']:g} BPM")
            if s["key"] != d["key"]:
                extra.append(s["key"])
            if s["meter"] != d["meter"]:
                extra.append(s["meter"])
            lyric = next((ln.strip() for ln in s["lyrics"].splitlines() if ln.strip()), "")
            rows.append(ui.row(
                str(i),
                [
                    {"text": flag, "style": "ok" if flag == "▶" else "accent"},
                    {"text": s["place"], "style": "bold"},
                    str(s["bars"]),
                    {"text": f"{s['start_bar'] + 1}", "style": "dim"},
                    clock(s["start_seconds"]),
                    " | ".join(s["chords"]),
                    {"text": ", ".join(extra), "style": "warning"} if extra else "",
                    {"text": ", ".join(s["tracks"]) or "—", "style": "dim"},
                ],
                "accent" if i == playing else None,
                selection=Item("komposoija.section", s["place"], self.path, s["line"], props={
                    "Section": s["name"],
                    "Played": f"time {s['occurrence']}",
                    "Bars": s["bars"],
                    "Starts": f"bar {s['start_bar'] + 1}, {clock(s['start_seconds'])}",
                    "Key": s["key"],
                    "Tempo": f"{s['tempo']:g}" + (f"→{s['tempo_to']:g}" if s["tempo_to"] else "") + " BPM",
                    "Meter": s["meter"],
                    "Chords": " | ".join(s["chords"]),
                    "Tracks": ", ".join(s["tracks"]) or "—",
                    "Lyrics": lyric or "—",
                }),
            ))
        return ui.table(
            "form",
            [
                ui.column("", width=1),
                ui.column("Section", width=max(8, *(len(s["place"]) for s in d["sections"])) + 1),
                ui.column("Bars", width=4, align="right"),
                ui.column("Bar", width=4, align="right"),
                ui.column("At", width=5, align="right"),
                ui.column("Chords", grow=3),
                ui.column("Changes", grow=1),
                ui.column("Tracks", grow=2),
            ],
            rows,
            cursor=self.cursor,
            autofocus=True,
            empty="The form is empty: song.arrange(...)",
            on_select=self._select_row,
            on_activate=self._goto_row,
            grow=1,
        )

    def render(self) -> ui.Node:
        d = self.data
        head: list[Any] = [((d or {}).get("title") or self.path.stem, "bold")]
        if d:
            head.append((f"   {d['key']}, {d['tempo']:g} BPM, {d['meter']}, {d['style']}"
                         f"   {len(d['bars'])} bars, {clock(d['seconds'])}", "dim"))
        head.append(("   " + relative(self.path, Path.cwd()), "dim"))
        if self.rendering:
            head.append(("   rendering…", "accent"))
        if self.error:
            head.append(("   " + self.error, "error"))
        if d is None:
            return ui.vbox(
                ui.text(head),
                ui.text("Rendering the song…" if self.rendering else (self.error or "Not rendered."),
                        "error" if self.error and not self.rendering else "dim", wrap=True),
                hints("c", "render again", "e", "edit"),
            )
        return ui.vbox(
            ui.text(head),
            self._transport(),
            self._form(),
            self._bars_strip(),
            *self._lyrics(),
            hints("space/F9", "play from the mark / stop", "Enter", "play this section",
                  "[ ]", "mark a bar earlier/later", "l", "loop", "f", "follow the editor",
                  "e", "edit", "c", "render"),
        )


def mark_bar_no(data: dict[str, Any], mark: tuple[int, int]) -> int:
    """The song's bar number (1-based) of a mark."""
    return data["sections"][mark[0]]["start_bar"] + mark[1] + 1
