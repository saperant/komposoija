"""komposoija's myrcp plugin (src/komposoija/ui/plugins/komposoija) over myrcp's plugin protocol:
songs found, the form, the start mark following the editor, playing from it (with a
stand-in fluidsynth), render errors at their line. Skipped without the myrcp SDK."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
from myrcp_peer import PLUGINS_DIR, SDK, Peer

sys.path.insert(0, str(PLUGINS_DIR / "komposoija"))
from myrcp_komposoija.songs import find_songs  # noqa: E402

# This venv has komposoija; the plugin host runs in it, with the SDK on its path.
KOMPOSOIJA_PYTHON = sys.executable
need_myrcp = pytest.mark.skipif(SDK is None, reason="no myrcp SDK (pip install -e '.[dev]', MYRCP_SDK, or ../myrcp)")

SONG = '''from komposoija import *

song = Song(title="Lanterns", key="G major", tempo=120)

verse = song.section("verse", bars=8, chords="<I V vi IV>", lyrics="""
    one line
    two line
    three line
    four line
""")
chorus = song.section("chorus", bars=4, chords="<IV I V I>")
verse.play(bass=bass.roots, keys=comp.whole)
chorus.play(drums=drums.rock, bass=bass.roots)
song.arrange("verse chorus verse chorus")
'''

# Records its arguments and the excerpt it was given, then plays "for a while".
FAKE_FLUIDSYNTH = """#!/bin/sh
for a in "$@"; do last="$a"; done
n=$(ls "$FAKE_LOG" 2>/dev/null | wc -l)
cp "$last" "$FAKE_LOG/play$n.mid"
exec sleep 30
"""


def line_of(needle: str) -> int:
    return next(n for n, line in enumerate(SONG.splitlines(), 1) if needle in line)


def find_node(node, node_id):
    if isinstance(node, dict):
        if node.get("id") == node_id:
            return node
        node = list(node.values())
    if isinstance(node, list):
        for child in node:
            if found := find_node(child, node_id):
                return found
    return None


def text_of(update) -> str:
    return json.dumps(update["tree"], ensure_ascii=False)


def test_finding_songs(tmp_path):
    (tmp_path / "songs").mkdir()
    (tmp_path / "songs" / "a.py").write_text(SONG)
    (tmp_path / "songs" / "helper.py").write_text("import komposoija\n")
    (tmp_path / "songs" / "test_a.py").write_text(SONG)
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "b.py").write_text(SONG)
    assert find_songs([tmp_path]) == [(tmp_path / "songs" / "a.py").resolve()]


@pytest.fixture
def song_peer(tmp_path):
    bin_dir, log = tmp_path / "bin", tmp_path / "played"
    bin_dir.mkdir()
    log.mkdir()
    fake = bin_dir / "fluidsynth"
    fake.write_text(FAKE_FLUIDSYNTH)
    fake.chmod(0o755)
    soundfont = tmp_path / "gm.sf2"
    soundfont.write_bytes(b"")
    env = {
        "MYRCP_HOST_PLUGINS": "komposoija",
        "KOMPOSOIJA_SONGS": str(tmp_path / "songs"),
        "KOMPOSOIJA_SOUNDFONT": str(soundfont),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "FAKE_LOG": str(log),
    }
    (tmp_path / "songs").mkdir()
    song = tmp_path / "songs" / "lanterns.py"
    song.write_text(SONG)
    p = Peer(tmp_path, python=KOMPOSOIJA_PYTHON, env=env)
    p.request("initialize", {"protocol": 1})
    yield p, song, log
    log_text = p.close()
    assert "Traceback" not in log_text, log_text


class Midi:
    def __init__(self, path: Path) -> None:
        self.path = path

    @property
    def length(self) -> float:
        """In seconds, by komposoija's mido."""
        code = "import mido, sys; print(mido.MidiFile(sys.argv[1]).length)"
        out = subprocess.run([KOMPOSOIJA_PYTHON, "-c", code, str(self.path)], capture_output=True, text=True, check=True)
        return float(out.stdout)


def played(log: Path, n: int, timeout: float = 10.0) -> Midi:
    """The n-th excerpt handed to fluidsynth (0-based), once it is there."""
    deadline = time.monotonic() + timeout
    while not (log / f"play{n}.mid").exists():
        assert time.monotonic() < deadline, f"fluidsynth was started {len(list(log.iterdir()))} time(s)"
        time.sleep(0.05)
    time.sleep(0.1)
    return Midi(log / f"play{n}.mid")


@need_myrcp
def test_song_view_follows_the_editor_and_plays_from_the_mark(song_peer):
    p, song, log = song_peer
    view = f"komposoija.song#{song}"

    def editor_at(needle):
        item = {"type": "file", "label": song.name, "path": str(song), "line": line_of(needle)}
        p.notify("selection.changed", {"view": "Neovim", "title": "Neovim", "items": [item]})

    p.request("view.open", {"view": view})
    u = p.wait_notify("view.update", lambda u: u["view"] == view and "chorus.2" in text_of(u), timeout=60)
    form = find_node(u["tree"], "form")
    assert [r["cells"][1]["text"] for r in form["rows"]] == ["verse", "chorus", "verse.2", "chorus.2"]

    # A lyric line: the verse, at the bar the line starts (4 lines in 8 bars: bar 5).
    editor_at("three line")
    p.wait_notify("view.update", lambda u: "verse:5" in text_of(u) and "▸G" in text_of(u))
    editor_at("chorus.play")
    u = p.wait_notify("view.update", lambda u: (find_node(u["tree"], "form") or {}).get("cursor", [0])[0] == 1)

    # space plays from the mark: the first chorus, 4 bars of 4/4 at 120 BPM into the song's 24 bars.
    p.notify("command.run", {"command": "komposoija.play", "view": view})
    assert played(log, 0).length == pytest.approx((24 - 8) * 2.0, abs=0.05)
    p.wait_notify("view.update", lambda u: "chorus  bar 1/4" in text_of(u))

    # While playing, the mark following the editor restarts playback there.
    editor_at("four line")
    assert played(log, 1).length == pytest.approx((24 - 6) * 2.0, abs=0.05)

    # A save renders again and plays the new version from the mark.
    song.write_text(SONG.replace('"<I V vi IV>"', '"<I IV vi V>"'))
    assert played(log, 2, timeout=20).length == pytest.approx((24 - 6) * 2.0, abs=0.05)

    # Loop: the section being played, from the mark to its end.
    p.notify("command.run", {"command": "komposoija.loop", "view": view})
    assert played(log, 3).length == pytest.approx(2 * 2.0, abs=0.05)

    p.notify("command.run", {"command": "komposoija.play", "view": view})  # stop
    p.wait_notify("view.update", lambda u: "■" in text_of(u))


@need_myrcp
def test_f9_opens_the_song_the_editor_is_in_and_plays(song_peer):
    p, song, log = song_peer
    item = {"type": "file", "label": song.name, "path": str(song), "line": line_of("two line")}
    p.notify("selection.changed", {"view": "Neovim", "title": "Neovim", "items": [item]})
    p.notify("command.run", {"command": "komposoija.play_at_cursor", "view": ""})
    show = p.wait_notify("view.show")
    assert show["view"] == f"komposoija.song#{song}"
    p.request("view.open", {"view": show["view"]})
    assert played(log, 0, timeout=60).length == pytest.approx((24 - 2) * 2.0, abs=0.05)  # verse bar 3


@need_myrcp
def test_render_errors_are_problems_at_their_line(song_peer):
    p, song, log = song_peer
    song.write_text(SONG.replace('"chorus", bars=4', '"chorus", bars=0'))
    view = f"komposoija.song#{song}"
    p.request("view.open", {"view": view})
    m = p.wait_notify("markers.set", lambda m: m["markers"], timeout=60)
    assert m["markers"][0]["line"] == line_of('song.section("chorus"')
    assert "bars must be >= 1" in m["markers"][0]["message"]
    song.write_text(SONG)
    p.wait_notify("markers.set", lambda m: not m["markers"], timeout=20)
