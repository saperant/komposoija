# Music Theory Study Material — Western Pop/Rock Focus

This folder is a self-contained study guide to the music theory needed to understand, analyse
and eventually **generate** pop/rock songs automatically. Each chapter explains concepts in
plain musical terms first, then adds a short **"For the pipeline"** section that shows how the
concept can be represented in data or turned into rules.

## Reading order

| #  | Chapter | What you'll learn |
|----|---------|-------------------|
| 01 | [Notes and pitch](01-notes-and-pitch.md) | Note names, octaves, sharps/flats, MIDI numbers, frequency |
| 02 | [Intervals](02-intervals.md) | Distances between notes, consonance/dissonance, inversion |
| 03 | [Rhythm, meter and breaks](03-rhythm-meter-breaks.md) | Beats, time signatures, subdivisions, syncopation, rests, fills, breaks, breakdowns |
| 04 | [Scales](04-scales.md) | Major, minor (3 kinds), pentatonic, blues, chromatic |
| 05 | [Keys and the circle of fifths](05-keys-circle-of-fifths.md) | Key signatures, relative/parallel keys, modulation |
| 06 | [Modes](06-modes.md) | Ionian → Locrian, characteristic notes, modal songs |
| 07 | [Chords and harmony](07-chords-harmony.md) | Triads, sevenths, extensions, inversions, voicing, diatonic chords, function |
| 08 | [Chord progressions](08-chord-progressions.md) | The common pop/rock progressions, cadences, borrowed chords |
| 09 | [Melody and hooks](09-melody-hooks.md) | Contour, phrasing, chord-tone targeting, motifs, hooks |
| 10 | [Song structure](10-song-structure.md) | Intro/verse/pre-chorus/chorus/bridge, forms, section lengths |
| 11 | [Drums and percussion](11-drums-percussion.md) | Kit pieces, core grooves, fills, groove feel, dynamics |
| 12 | [Bass](12-bass.md) | Role of bass, root/fifth patterns, locking with the kick, walking, pedals |
| 13 | [Arrangement and dynamics](13-arrangement-dynamics.md) | Energy curves, layering, frequency roles, builds and drops |
| 14 | [Musical styles](14-styles.md) | Essential features of rock, pop, punk, blues, funk, metal, EDM-pop, ballads etc. |
| 15 | [From theory to a composition pipeline](15-composition-pipeline.md) | Data models, generation order, rule sets, evaluation |
| 16 | [Jazz](16-jazz.md) | Swing, seventh-chord harmony, ii–V–I, substitutions, voicings, walking bass, forms |
| 17 | [Blues](17-blues.md) | 12-bar and other forms, blue notes, shuffle and 12/8 grooves, AAB lyrics, stop-time |
| 18 | [Funk](18-funk.md) | The one, 16th-note grid, interlocking parts, ghost notes, slap bass, vamps and breakdowns |
| 19 | [Reggae](19-reggae.md) | Ska to dancehall, one drop/rockers/steppers, skank, riddim bass, dub arranging |
| 20 | [Heavy metal](20-heavy-metal.md) | Power chords, down-tuning, riff types, modal harmony, metal drumming, subgenres |
| —  | [Glossary](glossary.md) | Quick definitions |
| —  | [Song DSL reference](song-dsl.md) | The backing-tracks-as-code tool built on this material: mini-notation, presets, CLI |

## Conventions used throughout

- **Pitch classes** are numbered 0–11 with C = 0 (C=0, C♯/D♭=1, D=2 … B=11).
- **Scale degrees** are written with carets in prose (^1, ^2, … ^7) and as integers in code.
- **Roman numerals**: upper case = major chord (I, IV, V), lower case = minor (ii, iii, vi),
  ° = diminished (vii°), + = augmented. `♭VII` means a major chord built on the lowered 7th degree.
- **MIDI note numbers**: middle C (C4) = 60, A4 (440 Hz) = 69.
- **Durations** are given in beats (quarter note = 1 beat in 4/4) or in "ticks" when talking
  about code (e.g. 480 ticks per quarter note, a common MIDI resolution).
- **BPM** = beats per minute.

## How to study with this

1. Read chapters 01–08 in order; they build on each other.
2. After each chapter, try the exercises at the end on a keyboard/guitar or in a DAW.
3. Chapters 09–14 can be read in any order once the basics are solid; the genre chapters
   16–20 build on 14 and can be read in any order.
4. Chapter 15 ties everything to the software; section 15.8 describes what is built so far.
5. To hear the concepts, write them as code: `songs/example.py` and the
   [Song DSL reference](song-dsl.md) show how keys, progressions, grooves and fills are
   expressed and rendered to MIDI/MP3.

## Building a PDF

```bash
scripts/build-docs-pdf.sh                # -> build/music-theory.pdf
scripts/build-docs-pdf.sh --paper letter
scripts/build-docs-pdf.sh --html-only    # -> build/music-theory.html (no WeasyPrint needed)
```

The first run creates `.venv-docs/` with the dependencies from `requirements-docs.txt`.
Styling lives in `docs/pdf/style.css`.
