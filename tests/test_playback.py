import shutil
import wave

import pytest

from komposoija import Song, drums, playback, render, strum, write_midi

pytestmark = pytest.mark.skipif(shutil.which("fluidsynth") is None, reason="fluidsynth not installed")


def test_render_wav(tmp_path):
    try:
        playback.find_soundfont()
    except playback.PlaybackError:
        pytest.skip("no SoundFont installed")
    song = Song(tempo=120)
    song.section("a", bars=1, chords="I").play(drums=drums.rock, keys=strum("x"))
    song.arrange("a")
    midi = write_midi(render(song), tmp_path / "a.mid")
    wav = playback.render_wav(midi, tmp_path / "a.wav")
    with wave.open(str(wav)) as w:
        assert w.getnframes() / w.getframerate() >= 2.0   # one bar at 120 BPM, plus release


@pytest.mark.skipif(not (shutil.which("lame") or shutil.which("ffmpeg")), reason="no MP3 encoder")
def test_cli_mp3_without_wav_keeps_only_mp3(tmp_path):
    from komposoija.cli import main
    song_file = tmp_path / "s.py"
    song_file.write_text('from komposoija import *\nsong = Song(title="T")\n'
                         'song.section("a", bars=1, chords="I").play(keys=strum("x"))\nsong.arrange("a")\n')
    assert main(["render", str(song_file), "-o", str(tmp_path / "s.mid"), "--mp3"]) == 0
    assert (tmp_path / "s.mp3").stat().st_size > 1000
    assert not (tmp_path / "s.wav").exists()


def test_missing_soundfont_is_reported(monkeypatch):
    monkeypatch.setenv("KOMPOSOIJA_SOUNDFONT", "/no/such.sf2")
    with pytest.raises(playback.PlaybackError, match="missing file"):
        playback.find_soundfont()
