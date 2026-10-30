# 15 — From Theory to an Automatic Composition Pipeline

This chapter connects the theory to software design. It is a starting point for
discussion, not a final architecture.

## 15.1 Design principles

1. **Hierarchical, top-down generation** — songs are hierarchical (form → sections →
   phrases → bars → beats → notes). Decide the big things first.
2. **Symbolic first** — generate in a symbolic domain (MIDI-like events) and render audio
   separately. Symbolic data is inspectable, editable and testable.
3. **Relative representations** — store harmony as Roman numerals and melody as scale
   degrees relative to the key; transposition and style changes become trivial.
4. **Repetition with variation** — reuse material across repeated sections and vary it
   deliberately. Generating every bar independently produces music that doesn't sound like
   a song.
5. **Rules + data** — start with explicit theory rules (this documentation), then replace
   or augment parts with statistical/ML models trained on corpora. Rules double as
   **constraints and evaluators** for ML outputs.
6. **Every stage is overridable** — a user (or a test) can pin key, progression, melody etc.

## 15.2 Pipeline stages

```
 ┌──────────────┐
 │ 0. Brief     │  style, mood, tempo range, length, key/vocal range, seed
 └──────┬───────┘
 ┌──────▼───────┐
 │ 1. Global    │  tempo, meter, key, mode, feel (swing, half-time)        ch. 03, 05, 06
 └──────┬───────┘
 ┌──────▼───────┐
 │ 2. Form      │  section list, bar counts, energy curve, transitions      ch. 10, 13
 └──────┬───────┘
 ┌──────▼───────┐
 │ 3. Harmony   │  progression per section (numerals), harmonic rhythm,     ch. 07, 08
 │              │  cadences, borrowed chords, modulations
 └──────┬───────┘
 ┌──────▼───────┐
 │ 4. Melody    │  hook first (chorus), then verse/pre/bridge melodies;     ch. 09
 │              │  rhythm → pitch; motif development
 └──────┬───────┘
 ┌──────▼───────┐
 │ 5. Rhythm    │  drum patterns per section/energy, fills, crashes         ch. 03, 11
 │   section    │  bass from chords + kick pattern                          ch. 12
 └──────┬───────┘
 ┌──────▼───────┐
 │ 6. Arrange   │  instrument roster, voicings, comping patterns,           ch. 07, 13
 │              │  counter-lines, activation by energy, builds/drops
 └──────┬───────┘
 ┌──────▼───────┐
 │ 7. Humanize  │  timing/velocity variation, swing, articulation           ch. 11
 └──────┬───────┘
 ┌──────▼───────┐
 │ 8. Evaluate  │  rule checks + scores; regenerate weak parts
 └──────┬───────┘
 ┌──────▼───────┐
 │ 9. Render    │  MIDI file export → synth/sampler → audio (mix/master)
 └──────────────┘
```

**Why the hook first?** In songwriting practice the chorus is usually written first and the
rest is built to set it up. Generating the chorus melody before the verse lets us ensure
the verse contrasts with it (lower register, different rhythm).

## 15.3 Core data model (sketch)

```python
from dataclasses import dataclass, field

@dataclass
class Key:
    tonic_pc: int            # 0..11
    mode: str                # "ionian", "aeolian", ...

@dataclass
class ChordEvent:
    start_beat: float
    duration_beats: float
    numeral: str             # "I", "bVII", "V/vi", ...
    root_pc: int
    quality: str             # "maj", "min7", ...
    bass_pc: int | None = None

@dataclass
class Note:
    start_beat: float
    duration_beats: float
    pitch: int               # MIDI
    velocity: int            # 1..127

@dataclass
class Track:
    instrument: str          # "drums", "bass", "rhythm_guitar", "vocal", ...
    role: str                # "foundation", "low_end", "harmony", "lead", ...
    notes: list[Note] = field(default_factory=list)

@dataclass
class SectionPlan:
    kind: str
    bars: int
    energy: float
    key: Key
    chords: list[ChordEvent]
    ends_with: str           # "fill", "stop", "riser", "dropout", "none"
    source: str | None = None  # name of a previous section this one repeats/varies

@dataclass
class Song:
    tempo_bpm: float
    meter: tuple[int, int]
    style: str
    sections: list[SectionPlan]
    tracks: list[Track]
```

Key idea: **`SectionPlan.source`** points to an earlier section so verse 2 / chorus 2 are
generated as *variations* of the originals instead of from scratch.

## 15.4 Approaches per stage

| Stage | Rule-based start | Data-driven upgrade |
|---|---|---|
| Form | Templates from ch. 10 with style weights | Learn form distributions from annotated datasets (e.g. SALAMI, Harmonix Set) |
| Harmony | Templates + Markov transitions + cadence constraints | n-gram / transformer on chord datasets (McGill Billboard, Hooktheory, Chordonomicon) |
| Melody | Rhythm cells + weighted pitch choice + contour targets | Sequence model conditioned on chords (Lakh MIDI, POP909) |
| Drums | Pattern library + fill rules | Groove models (Magenta Groove MIDI Dataset) |
| Bass | Rule-based from chords + kick | Conditioned sequence model |
| Arrangement | Energy thresholds + register rules | Learned instrument activation per section |
| Humanize | Random jitter + swing | Learned micro-timing (GMD) |

Dataset names above are suggestions to verify (licence, availability) before use.

## 15.5 Evaluation: rule checks derived from the theory

Hard constraints (reject/repair):
- All notes inside instrument ranges (ch. 01).
- Melody strong-beat notes are chord tones or approved colour tones (ch. 09).
- No sustained minor-2nd / tritone clashes between melody and chords unless intentional
  (ch. 02).
- Bass is the lowest voice; bass plays the chord root (or the specified slash bass) on
  chord-change downbeats (ch. 12).
- Section lengths are multiples of 2/4 bars unless the style allows otherwise (ch. 03).
- Drum fill at the end of each section; crash on the first downbeat of the next (ch. 11).

Soft scores (rank candidates):
- **Singability**: step ratio, max leap, range, tessitura.
- **Hook strength**: repetition of a 1–2 bar motif in the chorus, rhythmic distinctiveness.
- **Contrast**: verse vs. chorus differ in register, density, harmonic rhythm.
- **Coherence**: repeated sections share material; motif reuse across sections.
- **Energy curve match**: computed density/velocity per section vs. the planned curve.
- **Voice-leading smoothness** of harmony parts (ch. 07).
- **Style conformity**: tempo, patterns, chord vocabulary within the style profile (ch. 14).

## 15.6 Suggested implementation milestones

1. **Theory core library** — pitch, interval, scale, mode, chord, key, Roman-numeral
   parsing and realisation, with unit tests based on the examples in these docs.
2. **MIDI export** of a hard-coded song (form + chords + simple drums + bass) to verify
   the end-to-end path.
3. **Rule-based generators** for each stage with style profiles (pop-rock first).
4. **Evaluator** implementing the checks in 15.5; generate N candidates, keep the best.
5. **Melody generator** with hook-first workflow and motif development.
6. **Arrangement & humanisation** for convincing playback.
7. **Data-driven models** replacing individual stages, evaluated against the rule-based
   baseline.
8. **Audio rendering** (soundfonts/samplers, then mixing), optional lyrics/vocal synthesis.

## 15.7 Project decisions and open questions

Decided:

- **Output**: MIDI as the primary format (scores via notation software, playback via
  SoundFonts), plus rendered WAV/MP3 audio.
- **Lyrics**: user-supplied; they drive the structure stage.
- **Interaction**: human in the loop at every stage. The song is code that the user and
  an AI agent edit together, re-rendering after each change.

Still open:

- Which further styles are needed beyond pop-rock, jazz, blues, funk, reggae and metal?
- Notation output: MusicXML export from the tool, or MIDI import into MuseScore?
- Licensing constraints on any training data.

## 15.8 Current state: backing tracks as code

The first milestone implements the backing-track part of the pipeline as a code-first
tool, in the spirit of the live-coding environment Strudel. The full reference is the
[Song DSL reference](song-dsl.md); the user-facing flow is:

```
lyrics -> structure (agent + human) -> mood (keys, chords, grooves) -> details -> MIDI
```

How the stages of 15.2 are covered:

| Stage | Status | Where |
|---|---|---|
| 0. Brief | conversation with the agent (`CLAUDE.md` workflow) | — |
| 1. Global | `Song(key, tempo, meter, swing)`; per-section key (absolute or `"+1"`), tempo, ritardando/accelerando (`tempo_to`) and meter | `song.py`, `render.py` |
| 2. Form | sections with lyrics and bar counts, `arrange()`, variants | `song.py` |
| 3. Harmony | Roman numerals/chord symbols in mini-notation; secondary dominants, borrowed chords | `theory.py`, `notation.py` |
| 4. Melody | hand-written (`n(...)`, `note(...)`); no generator yet | — |
| 5. Rhythm section | drum, fill and bass presets from ch. 11–12; genre palettes for jazz, blues, funk, reggae and metal (ch. 16–20); chord-tone bass with approach notes; generated walking bass | `presets.py`, `genres.py`, `render.py` |
| 6. Arrange | comping presets, voice-led close/open/power/shell/rootless voicings, style profiles (instruments, registers, feel), per-section parts, automatic crashes | `presets.py`, `genres.py`, `styles.py`, `theory.py` |
| 7. Humanize | swing (8th or 16th, off in 8th-based meters such as 6/8 and 7/8), per-track timing/velocity jitter set by style | `render.py`, `styles.py` |
| 8. Evaluate | rule checks not implemented; the render summary supports review by eye | — |
| 9. Render | MIDI writer; FluidSynth playback, WAV and MP3 | `render.py`, `playback.py` |

Against the milestones in 15.6: (1) the theory core and (2) MIDI export are done; parts of
(3), (6) and (8) exist as presets, humanisation and audio rendering. The natural next
steps are a melody generator aligned to lyric syllables (ch. 09), the rule-based evaluator
of 15.5, and score export.
