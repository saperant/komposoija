# 18 — Funk

Funk emerged in the mid-1960s from soul and R&B, above all from James Brown's band, and
spread through Sly & the Family Stone, The Meters, Parliament-Funkadelic, Tower of Power,
Earth, Wind & Fire and Prince. It also shaped disco, hip-hop and modern pop. Funk is music
of **rhythm first**: simple harmony, a **16th-note grid**, heavy emphasis on **"the one"**,
and many small syncopated parts that **interlock** like gears.

## 18.1 The core ideas

- **The one**: the downbeat of the bar is the strongest, most "landed" moment. Bass, kick and
  horns often hit it together; everything else in the bar can float around it.
- **16th-note grid**: parts are written and felt in 16ths at 90–115 BPM. A slight 16th swing
  (≈ 0.53–0.57) gives the "greasy" feel; some funk is dead straight.
- **Interlocking parts**: each instrument plays a short, repeating, syncopated figure that
  fills gaps left by the others. No part is complete alone; together they make one rhythm.
- **Space**: rests are as important as notes. If a part is busy, another part lays out.
- **Tight timing, dynamic contrast**: accented notes against very soft ghost notes.

## 18.2 Harmony

Funk harmony is deliberately static so the rhythm can carry the music.

| Harmony | Example (in E) | Notes |
|---|---|---|
| **One-chord vamp** on a dominant | E9 for 16 bars | dominant 9th/13th chords; Mixolydian |
| **Minor vamp** (Dorian) | Em7 (… A9) | the major IV (A9) is the Dorian colour (chapter 06) |
| **Two-chord vamp** | E9 – A9 | I–IV, both dominants |
| **The bridge** | A9 → B9 (IV → V) or a ♭VII–IV move | gives relief from the vamp, then back "to the one" |
| **7♯9** | E7♯9 | the "Hendrix chord" is common in funk too |

Chord *voicings* are small: three- or four-note 9th/13th shapes on the top strings of the
guitar or in the middle of the clavinet, so they cut through without muddying the bass.

## 18.3 The instruments

### Drums

- 16th-note hi-hat with accents (strong on the beats or on the "&"s), open hi-hat on chosen
  off-beats for lift.
- Backbeat on 2 and 4, surrounded by **ghost notes** (very soft snare 16ths).
- **Syncopated kick** on 16th off-beats, but a solid kick on the one.
- **Linear drumming** (David Garibaldi, Tower of Power): only one limb plays at a time, which
  makes a dense but clear pattern.
- Breakbeats ("Funky Drummer"–type drum breaks) became the foundation of hip-hop sampling.

### Bass

- Syncopated 16th lines that leave space and lock with the kick; a big note on the one.
- **Ghost notes** (muted, percussive), **octave jumps**, hammer-ons, slides.
- **Slap and pop** (Larry Graham, Bootsy Collins, Marcus Miller): thumb slaps the low string,
  fingers pop the octave — a percussive octave pattern.
- **Fingerstyle 16ths** (Rocco Prestia) for a continuous, muted pulse.
- Lines often sit on the root and the ♭7, 5th and octave, rarely moving far.

### Guitar

- **Chicken scratch / chank**: muted strings strummed in continuous 16ths, letting only a
  few accented strums sound as chords.
- Short 9th-chord **stabs** on off-beats.
- **Single-note riffs** muted with the palm (Jimmy Nolen, Catfish Collins).
- Two guitars often split the job: one scratches, one plays single-note riffs.

### Keys

- **Clavinet**: percussive, syncopated chord-and-bass-note riffs (Stevie Wonder).
- Hammond organ stabs and swells; Fender Rhodes for softer funk/soul; synth bass in 80s funk.

### Horns

- Short unison or harmonised **stabs** on syncopated 16ths, **hits** with the drums,
  and composed lines (Tower of Power, The JB Horns).

## 18.4 Arrangement and form

Funk songs are often built from **vamp sections** rather than verse–chorus harmony changes:

```
intro (drums or guitar alone) → groove A (vamp, vocals) → groove A → bridge (IV–V) →
groove A → breakdown (drums + bass, instruments re-enter one by one) → groove A →
ending hits
```

- **Breakdowns**: strip to drums and bass, then layer instruments back in.
- **Hits / stops**: the whole band plays the same syncopated figure; space between hits.
- **Cues**: the bandleader calls changes ("take it to the bridge!") — in a fixed arrangement,
  this becomes a planned section change.
- Vocals are rhythmic and chant-like; call and response with backing vocals or horns.

## 18.5 Substyles

| Style | Features | Artists |
|---|---|---|
| JB funk | the one, chicken scratch, horn stabs, minimal harmony | James Brown |
| New Orleans funk | second-line syncopation, sparse, loose | The Meters |
| P-funk | synthesizers, slow heavy grooves, big ensembles | Parliament-Funkadelic |
| Horn funk | linear drums, complex horn charts, 16th bass | Tower of Power |
| Disco-funk | four-on-the-floor, octave bass, strings | Chic |
| Minneapolis | drum machines, synth bass and stabs | Prince |
| Funk rock / modern | distorted guitars, slap bass / retro-revival | Red Hot Chili Peppers, Vulfpeck, Jamiroquai |

## 18.6 In komposoija

```python
# style="funk": 16th swing 0.54, clav, horns
song = Song(title="...", key="E dorian", tempo=104, style="funk")
vamp = song.section("vamp", bars=8, chords=funk.progressions.dorian_vamp)
vamp.play(drums=funk.drums.groove, bass=funk.bass.ghosts,
          guitar=funk.comp.scratch, keys=funk.comp.clav, horns=funk.comp.horn_hits)
```

| Palette | Contents |
|---|---|
| `funk.drums` | `groove the_one open_hat linear` |
| `funk.bass` | `syncopated octave_pops ghosts the_one` |
| `funk.comp` | `scratch chank clav horn_hits horn_stab_one` |
| `funk.progressions` | `vamp dorian_vamp two_chord bridge minor_groove` |

The funk style profile swings **16ths** (`swing_unit=16`), puts the guitar and clavinet high
in the register so they stay clear of the bass, and adds a `horns` track. Accents and ghost
notes are velocity patterns (`.velocity("115 35 ~ 90 ...")`). For a breakdown where parts
re-enter, filter a pattern by time: `funk.comp.scratch.filter(lambda ev: ev.begin >= 4)`.
See `songs/funk_example.py`.

## Exercises

1. Program a one-bar groove, then mute each part in turn and notice what disappears.
2. Write a bass line that plays the one, rests for two beats, and fills the end of the bar.
3. Arrange a breakdown in which the instruments come back one every two bars.
