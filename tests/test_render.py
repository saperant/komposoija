import mido
import pytest

from komposoija import RenderError, Song, bass, ct, drums, fill, render, s, strum, write_midi


def tiny_song(**kw) -> Song:
    song = Song(title="t", key="C major", tempo=120, **kw)
    a = song.section("a", bars=2, chords="<I V>")
    a.play(drums=drums.rock, bass=bass.roots, keys=strum("x"))
    b = song.section("b", bars=1, chords="vi")
    b.play(drums=drums.rock, bass=ct("0 ~ ~ a"))
    song.arrange("a b")
    return song


def notes_of(r, track):
    return [n for n in r.notes if n.track == track]


def test_bass_plays_chord_roots_in_register():
    r = render(tiny_song())
    roots = [(n.start, n.pitch) for n in notes_of(r, "bass")]
    assert roots[:2] == [(0.0, 36), (4.0, 31)]          # C2, then G1 (register starts at E1)
    assert all(28 <= p <= 52 for _, p in roots)


def test_approach_note_targets_next_chord():
    song = tiny_song()
    song.sections["b"].chords = __import__("komposoija").chords("<vi>")
    r = render(song, ["b"])
    approach = notes_of(r, "bass")[-1]
    assert approach.start == 3.0 and approach.pitch == 32   # a semitone below A1 (33)


def test_crash_on_section_start_but_not_song_start():
    r = render(tiny_song())
    crashes = [n.start for n in notes_of(r, "drums") if n.pitch == 49]
    assert crashes == [8.0]


def test_fill_replaces_last_bar_only():
    song = tiny_song()
    song.sections["a"].fill(drums=fill(drums.rock, "two_beats"))
    r = render(song, ["a"])
    toms = [n for n in notes_of(r, "drums") if n.pitch in (43, 47)]
    assert toms and all(n.start >= 6.0 for n in toms)


def test_swing_delays_offbeat_eighths():
    r = render(tiny_song(swing=2 / 3), ["a"])
    hats = sorted(n.start for n in notes_of(r, "drums") if n.pitch == 42)
    assert hats[:2] == [0.0, pytest.approx(2 / 3)]


def test_missing_chords_is_a_clear_error():
    song = Song()
    song.section("x", bars=1).play(bass=bass.roots)
    song.arrange("x")
    with pytest.raises(RenderError, match="no chord"):
        render(song)


def test_unknown_track_is_a_clear_error():
    song = Song()
    song.section("x", bars=1, chords="I").play(cello=bass.roots)
    song.arrange("x")
    with pytest.raises(RenderError, match="unknown track 'cello'"):
        render(song)


def test_midi_file_structure(tmp_path):
    path = write_midi(render(tiny_song()), tmp_path / "t.mid")
    m = mido.MidiFile(path)
    names = [t.name for t in m.tracks]
    assert names == ["t", "drums", "bass", "keys"]
    meta = [msg for msg in m.tracks[0] if msg.is_meta]
    assert [x.text for x in meta if x.type == "marker"] == ["a", "b"]
    assert [x.text for x in meta if x.type == "text"] == ["C", "G", "Am"]
    assert {msg.channel for msg in m.tracks[1] if msg.type == "note_on"} == {9}
    assert m.length == pytest.approx(6.0)   # 3 bars of 4/4 at 120 BPM


def test_section_variant_copies_parts():
    song = tiny_song()
    v = song.section("a2", like="a")
    v.play(bass=None)
    assert "bass" in song.sections["a"].parts and "bass" not in v.parts


