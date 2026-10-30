# 09 — Melody and Hooks

Melody is what people sing back. In pop, the **vocal melody** (and especially the chorus
**hook**) is the most important element of the song.

## 9.1 Melodic building blocks

- **Pitch content** — which scale/notes (chapter 04). Pop vocals are heavily pentatonic
  with passing tones.
- **Contour** — the shape: rising, falling, arch, inverted arch, wave, flat.
- **Range** — distance from lowest to highest note. Verses ~ a 5th to an octave; choruses
  often reach a 3rd–5th higher than the verse's peak.
- **Rhythm** — the durations and placement of the notes; the rhythm of a melody is often
  more memorable than its pitches.
- **Intervals** — mostly steps and small leaps (chapter 02).

## 9.2 Chord tones and non-chord tones

Every melody note relates to the chord under it:

- **Chord tones** (root, 3rd, 5th, 7th) — stable; favoured on **strong beats** (1 and 3)
  and **long notes**.
- **Non-chord tones** — add motion:
  - **Passing tone** — steps between two chord tones (C–D–E over C).
  - **Neighbour tone** — steps away and back (E–F–E).
  - **Suspension** — a note held over from the previous chord, then resolving down by step.
  - **Appoggiatura** — a leap to a non-chord tone on a strong beat, resolving by step.
    Very emotional; ballad climaxes ("Someone Like You").
  - **Anticipation** — a note of the next chord arriving early (syncopation).

A common heuristic: **strong beat → chord tone; weak beat → anything in the scale**.
Pop also sustains **colour tones** (9th, 6th, maj7, sus4) on strong beats for a modern,
"floating" sound.

## 9.3 Motif, phrase and period

- **Motif** — a short melodic-rhythmic idea (2–6 notes). Development by **repetition,
  sequence (same shape at a different pitch), inversion, rhythmic variation, extension,
  truncation**.
- **Phrase** — a musical "sentence", typically 2 or 4 bars, often one lyric line.
- **Period** — two phrases in question–answer: the first (antecedent) ends unresolved,
  the second (consequent) ends resolved.

Typical pop phrase structures over 4 lines:

| Pattern | Description | Effect |
|---|---|---|
| **AAAA** | same melody four times (with lyric changes) | Hypnotic, simple (verses) |
| **AABA** | repeat, contrast, return | Classic, satisfying |
| **ABAB** | alternate two ideas | Balanced |
| **AAAB** / **AABB** | build then release | Good for choruses |
| **ABAC** | same start, different endings | Question/answer |

The "**sentence**" form (short idea, repeated, then a longer continuation:
`1 bar + 1 bar + 2 bars`) is especially common in hooks.

## 9.4 Rhythm of melody and lyrics

- Melody rhythm follows **natural speech stress**: stressed syllables on strong beats or
  syncopated accents.
- **Start points** vary the feel: starting on beat 1 sounds direct; starting on a
  **pickup** (before the bar) or **late** (beat 2, the "& of 1") sounds conversational and
  modern. Contrast the verse and chorus start points.
- **Note density** contrasts between sections: busy, syllabic verses vs. longer, sustained
  chorus notes (or vice versa for a rap-sung chorus).
- **Rests** between phrases let the singer breathe and give space for instrumental answers.

## 9.5 Hooks

A **hook** is the most memorable musical idea — usually the chorus melody + title lyric,
but also riffs, synth lines, vocal ad-libs, drum patterns.

Properties of strong hooks:

1. **Short** (1–2 bars) and **repeated** (often 2–4 times in the chorus).
2. **Simple rhythm**, often syncopated, fitting the title lyric.
3. **Narrow pitch set** (3–5 notes, often pentatonic) with **one distinctive feature**
   (a leap, a held high note, a rhythmic quirk).
4. **High point** — the chorus usually reaches the song's highest sustained notes.
5. **Contrast** with the verse in register, rhythm and density.
6. **Lands on a strong chord tone** at the end of the line.

Types of hooks in a pop arrangement:

- **Melodic hook** (vocal chorus line)
- **Riff hook** (guitar/synth: "Seven Nation Army", "Smoke on the Water", "Sweet Child o' Mine")
- **Post-chorus hook** (wordless "oh-oh", vocal chop, synth drop)
- **Rhythmic hook** (clap/drum pattern: "We Will Rock You")
- **Lyrical hook** (catch-phrase title)

## 9.6 Melodic contrast between sections

| Section | Register | Rhythm | Range |
|---|---|---|---|
| Verse | Lower–middle | More syllables, conversational | Narrower (5th–octave) |
| Pre-chorus | Rising | Building, often shorter repeated phrases | Climbing |
| Chorus | Highest | Longer notes, simpler, repeated hook | Widest/highest |
| Bridge | Different (new notes, new contour) | Contrasting | Variable |

## 9.7 Riffs

A **riff** is a short, repeated instrumental figure — the hook of rock. Riffs are
usually built from **minor pentatonic / blues scale** notes, played in the low-mid
register, often doubled by bass, and **rhythmically distinctive** (syncopation, rests).
Rock riff songs often have the riff replace a chord progression entirely (the riff *is*
the harmony).

## For the pipeline

A workable melody generation order:

1. Take the **chord progression and section plan** as given.
2. Generate a **rhythm** first (per phrase), from a style-dependent library of rhythmic
   cells, aligned to lyric syllables if available.
3. Assign pitches: strong beats → chord tones (weighted by stability), weak beats → scale
   tones by step; constrain by **range** and **target contour** per section.
4. Apply **motif development**: phrase 2 = phrase 1 (maybe transposed), phrase 4 = varied
   ending landing on ^1/^3/^5 for resolution.
5. Score candidates: singability (step ratio, max leap, range), chord-tone fit, contour match,
   repetition/novelty balance; keep the best.

```python
def note_weight(pc, chord_pcs, scale_pcs, strong_beat):
    if pc in chord_pcs:
        return 3.0 if strong_beat else 1.5
    if pc in scale_pcs:
        return 0.4 if strong_beat else 1.0
    return 0.05   # chromatic — only as passing tones
```

## Exercises

1. Write a 4-bar melody over C–G–Am–F using only chord tones on beats 1 and 3.
2. Take a 2-bar motif and develop it into an 8-bar AABA melody.
3. Analyse the chorus of a favourite song: range, highest note, repetition pattern.
