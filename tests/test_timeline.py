"""Places in a song: bars in time, place names, the source map, MIDI excerpts, inspect."""

import json
from fractions import Fraction

import mido
import pytest

from komposoija import Song, bass, comp, drums, playback, render, write_midi
from komposoija.cli import main
from komposoija.render import RenderError
from komposoija.sourcemap import region_at, regions
from komposoija.timeline import bar_at, bars, find_place, place_name, seconds_at

SONG = '''from komposoija import *

song = Song(title="T", key="C major", tempo=120)

verse = song.section("verse", bars=8, chords="<I V vi IV>", lyrics="""
    one line
    two line

    three line
    four line
""")
chorus = song.section("chorus", bars=4, chords="<IV I V I>",
                      tempo=60)
verse.play(bass=bass.roots)
chorus.play(bass=bass.roots,
            keys=comp.whole)
verse2 = song.section("verse2", like=verse)
song.arrange("verse chorus verse2 chorus")
'''


def line_of(needle: str) -> int:
    return next(n for n, ln in enumerate(SONG.splitlines(), 1) if needle in ln)


def song() -> Song:
    s = Song(tempo=120)
    s.section("verse", bars=2, chords="<I V>").play(bass=bass.roots, keys=comp.whole)
    s.section("chorus", bars=2, chords="<IV I>", tempo=60).play(drums=drums.rock, bass=bass.roots)
    s.arrange("verse chorus verse chorus")
    return s


def test_bars_follow_the_tempo():
    r = render(song())
    tl = bars(r)
    assert [b.index for b in tl] == list(range(8))
    assert [b.seconds for b in tl[:5]] == [0.0, 2.0, 4.0, 8.0, 12.0]  # 4/4 at 120, then 60
    assert bar_at(tl, 5.0).index == 2 and bar_at(tl, 12.5).index == 4
    assert bar_at(tl, -1) is None


def test_seconds_through_a_ramp():
    s = Song(tempo=120)
    s.section("a", bars=1, chords="I", tempo=60, tempo_to=120).play(keys=comp.whole)
    s.section("b", bars=1, chords="I").play(keys=comp.whole)
    s.arrange("a b")
    r = render(s)
    assert seconds_at(r, Fraction(4)) == pytest.approx(r.sections[0].seconds)
    assert seconds_at(r, 1) == pytest.approx(1.0)  # the first beat at 60 BPM


def test_place_names():
    r = render(song())
    assert find_place(r, "chorus").index == 2
    assert find_place(r, "chorus.2").index == 6
    assert find_place(r, "chorus.2:2").index == 7
    assert find_place(r, "verse:2").index == 1
    assert find_place(r, "5").index == 4
    assert place_name(r, 3, 1) == "chorus.2:2" and place_name(r, 0) == "verse"
    for bad in ("bridge", "chorus.3", "chorus:3", "9", "0"):
        with pytest.raises(RenderError):
            find_place(r, bad)


def test_source_map():
    found = regions(SONG)
    at = lambda needle: region_at(found, line_of(needle))
    assert at('song.section("verse"').section == "verse"
    assert (at("one line").section, at("one line").bar(8)) == ("verse", 0)
    assert at("three line").bar(8) == 4 and at("four line").bar(8) == 6  # 4 lines in 8 bars
    assert at("tempo=60").section == "chorus"            # the second line of a statement
    assert at("verse.play").section == "verse"
    assert at("keys=comp.whole").section == "chorus"
    assert at("like=verse").section == "verse2"
    assert at("song.arrange") is None and at("song = Song") is None


def test_excerpt_keeps_what_is_in_force(tmp_path):
    r = render(song())
    full = write_midi(r, tmp_path / "s.mid")
    start = find_place(r, "chorus.2")
    cut = playback.excerpt(full, tmp_path / "cut.mid", float(start.beat))
    mid = mido.MidiFile(str(cut))
    assert mid.length == pytest.approx(r.total_seconds - start.seconds, abs=0.05)
    tempos = [m for m in mid.tracks[0] if m.type == "set_tempo"]
    assert len(tempos) == 1 and tempos[0].time == 0 and round(mido.tempo2bpm(tempos[0].tempo)) == 60
    programs = [m for t in mid.tracks for m in t if m.type == "program_change"]
    assert programs and all(m.time == 0 for m in programs[:1])

    # From the middle of the verse's whole note: it sounds again at 0; with an end, it ends.
    middle = playback.excerpt(full, tmp_path / "mid.mid", 2.0, 4.0)
    keys = mido.MidiFile(str(middle)).tracks[-1]
    ons = [m for m in keys if m.type == "note_on" and m.velocity]
    assert ons and ons[0].time == 0
    now, offs = 0, []
    for m in keys:
        now += m.time
        if m.type == "note_off" or (m.type == "note_on" and not m.velocity):
            offs.append(now)
    assert offs and max(offs) <= 2 * 480


def test_inspect_json(tmp_path, capsys):
    f = tmp_path / "s.py"
    f.write_text(SONG)
    assert main(["inspect", str(f), "-o", str(tmp_path / "s.mid")]) == 0
    data = json.loads(capsys.readouterr().out)
    assert [s["place"] for s in data["sections"]] == ["verse", "chorus", "verse2", "chorus.2"]
    assert data["sections"][1]["line"] == line_of('song.section("chorus"')
    assert len(data["bars"]) == 24 and (tmp_path / "s.mid").exists()
    lyric = next(r for r in data["regions"] if r["first"] == line_of("three line"))
    assert (lyric["section"], lyric["bar"], lyric["lyric"]) == ("verse", 4, True)


def test_inspect_reports_errors_at_their_line(tmp_path, capsys):
    f = tmp_path / "s.py"
    f.write_text(SONG.replace('"chorus", bars=4', '"chorus", bars=0'))
    assert main(["inspect", str(f)]) == 1
    data = json.loads(capsys.readouterr().out)
    assert "bars must be >= 1" in data["error"] and data["places"][0]["line"] == line_of('song.section("chorus"')


def test_render_from_writes_an_excerpt_to_play(tmp_path, monkeypatch):
    f = tmp_path / "s.py"
    f.write_text(SONG)
    played = []
    monkeypatch.setattr(playback, "find_soundfont", lambda: tmp_path)
    monkeypatch.setattr(playback, "fluidsynth", lambda: "fluidsynth")
    monkeypatch.setattr(playback, "play", lambda midi, gain: played.append(midi) or _Done())
    assert main(["render", str(f), "-o", str(tmp_path / "s.mid"), "--play", "--from", "chorus.2"]) == 0
    assert played == [tmp_path / "s.from.mid"]
    full, cut = (mido.MidiFile(str(tmp_path / n)) for n in ("s.mid", "s.from.mid"))
    assert cut.length == pytest.approx(4 * 4 * 60 / 60, abs=0.05)  # one 4-bar chorus at 60 BPM
    assert full.length > cut.length


class _Done:
    def wait(self):
        return 0
