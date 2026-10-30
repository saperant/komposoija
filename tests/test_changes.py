"""Meter, key and tempo changes between sections."""

import mido
import pytest

from komposoija import Song, bass, n, render, s, write_midi
from komposoija.theory import parse_key, resolve_key


def conductor(path):
    out, t = [], 0
    for msg in mido.MidiFile(path).tracks[0]:
        t += msg.time
        out.append((t / 480, msg))
    return out


def test_section_meter_sets_bar_length_and_time_signature(tmp_path):
    song = Song(tempo=120)
    song.section("a", bars=1, chords="I").play(bass=n("0*4"))
    song.section("b", bars=2, chords="I", meter="7/8").play(bass=n("0*7"))
    song.arrange("a b a")
    r = render(song)
    assert [float(x.start_beat) for x in r.sections] == [0, 4, 11]
    assert r.total_beats == 15
    starts = sorted(x.start for x in r.notes if 4 <= x.start < 11)
    assert starts[:3] == [4.0, 4.5, 5.0] and len(starts) == 14
    sigs = [(t, (m.numerator, m.denominator)) for t, m in conductor(write_midi(r, tmp_path / "m.mid"))
            if m.type == "time_signature"]
    assert sigs == [(0, (4, 4)), (4, (7, 8)), (11, (4, 4))]


def test_bad_meter_is_a_clear_error():
    with pytest.raises(ValueError, match="unit"):
        Song().section("x", bars=1, meter="4/3")


def test_relative_key_transposes_the_song_key():
    assert resolve_key("+1", parse_key("E major")).name == "F major"
    assert resolve_key("-2", parse_key("A minor")).name == "G minor"
    assert resolve_key("+3 minor", parse_key("C major")).name == "Eb minor"
    assert resolve_key("D dorian", parse_key("C major")).name == "D dorian"


def test_truck_driver_modulation_renders_chorus_a_step_up():
    song = Song(key="C major")
    chorus = song.section("chorus", bars=1, chords="I").play(bass=bass.roots)
    song.section("last", like=chorus, key="+2")
    song.arrange("chorus last")
    r = render(song)
    assert [x.key.name for x in r.sections] == ["C major", "D major"]
    assert [x.chords_by_bar for x in r.sections] == [[["C"]], [["D"]]]
    first = [x.pitch % 12 for x in r.notes if x.track == "bass"]
    assert first[0] == 0 and first[-1] == 2


def test_walking_bass_leads_into_relative_key_of_next_section():
    from komposoija import walk
    song = Song(key="C major", style="jazz")
    song.section("a", bars=1, chords="I").play(bass=walk())
    song.section("b", bars=1, chords="I", key="+1").play(bass=walk())
    song.arrange("a b")
    line = [x.pitch for x in render(song).notes if x.track == "bass"]
    assert abs(line[3] - line[4]) == 1 and line[4] % 12 == 1


def test_tempo_ramp(tmp_path):
    song = Song(tempo=120)
    song.section("a", bars=1, chords="I").play(bass=n("0*4"))
    song.section("rit", bars=1, chords="I", tempo=120, tempo_to=60).play(bass=n("0*4"))
    song.arrange("a rit")
    r = render(song)
    # 4 beats at 120 + beats at 120, 100, 80, 60
    assert r.total_seconds == pytest.approx(2 + 0.5 + 0.6 + 0.75 + 1.0)
    tempos = [(t, round(mido.tempo2bpm(m.tempo))) for t, m in
              conductor(write_midi(r, tmp_path / "t.mid")) if m.type == "set_tempo"]
    assert tempos == [(0, 120), (5, 100), (6, 80), (7, 60)]
    assert "120→60 BPM" in __import__("komposoija").summary(r)


def test_swing_grid_counts_from_section_start_after_odd_bar():
    song = Song(swing=2 / 3)
    song.section("odd", bars=1, meter="7/8").play(drums=s("hh*7"))
    song.section("a", bars=1).play(drums=s("hh*8"))
    song.arrange("odd a")
    hats = sorted(x.start for x in render(song).notes if x.pitch == 42)
    assert hats[:2] == [0.0, 0.5]              # 7/8 is played straight
    assert hats[7:9] == [3.5, pytest.approx(3.5 + 2 / 3)]
