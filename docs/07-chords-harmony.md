# 07 — Chords and Harmony

A **chord** is three or more notes sounding together (two-note "power chords" are treated
as chords in rock too). **Harmony** is how chords are built and how they move.

## 7.1 Triads

Stack two 3rds on a **root**:

| Triad | Formula | Semitones | C example | Symbol | Sound |
|---|---|---|---|---|---|
| Major | 1 3 5 | 0 4 7 | C E G | C | bright, stable |
| Minor | 1 ♭3 5 | 0 3 7 | C E♭ G | Cm | dark, stable |
| Diminished | 1 ♭3 ♭5 | 0 3 6 | C E♭ G♭ | C° / Cdim | tense, unstable |
| Augmented | 1 3 ♯5 | 0 4 8 | C E G♯ | C+ / Caug | eerie, suspenseful |

### Suspended and power chords

| Chord | Formula | C example | Use |
|---|---|---|---|
| sus2 | 1 2 5 | C D G | Open, ambiguous; very common in pop/rock guitar and synth pads |
| sus4 | 1 4 5 | C F G | Tension that resolves 4→3 ("Pinball Wizard", "Free Fallin'") |
| **Power chord (5)** | 1 5 (8) | C G C | The rock and metal chord. No 3rd ⇒ neither major nor minor; distortion-friendly |
| add9 | 1 3 5 9 | C E G D | Pop sparkle, ballads |

## 7.2 Seventh chords

Add a 7th above the root:

| Chord | Formula | Semitones | C example | Symbol | Where |
|---|---|---|---|---|---|
| Major 7 | 1 3 5 7 | 0 4 7 11 | C E G B | Cmaj7 / CΔ7 | Soft pop, soul, jazz, dreamy ballads |
| Dominant 7 | 1 3 5 ♭7 | 0 4 7 10 | C E G B♭ | C7 | Blues (every chord!), V7 resolving to I, funk, rock'n'roll |
| Minor 7 | 1 ♭3 5 ♭7 | 0 3 7 10 | C E♭ G B♭ | Cm7 / C-7 | Funk, soul, R&B, smooth pop |
| Minor 7♭5 (half-dim) | 1 ♭3 ♭5 ♭7 | 0 3 6 10 | C E♭ G♭ B♭ | Cm7♭5 / Cø | ii in minor keys, jazz |
| Diminished 7 | 1 ♭3 ♭5 𝄫7 | 0 3 6 9 | C E♭ G♭ B𝄫(A) | C°7 | Passing chord, drama |
| Minor-major 7 | 1 ♭3 5 7 | 0 3 7 11 | C E♭ G B | Cm(maj7) | Spy/noir, descending lines ("Stairway"-type clichés) |
| 6 | 1 3 5 6 | 0 4 7 9 | C E G A | C6 | Retro pop, rock'n'roll, swing |
| Minor 6 | 1 ♭3 5 6 | 0 3 7 9 | C E♭ G A | Cm6 | Dorian colour, bossa |

## 7.3 Extensions and alterations

Beyond the 7th, keep stacking 3rds: **9 (= 2), 11 (= 4), 13 (= 6)**.

- C9 = C E G B♭ D; Cmaj9 = C E G B D; Cm9 = C E♭ G B♭ D
- C11 often omits the 3rd; C13 often omits the 11th (and 5th)
- Altered dominants (C7♯9 — the **"Hendrix chord"** from "Purple Haze", C7♭9, C7♯5) add
  spice in funk, rock and jazz.
- **"add"** means add without the 7th (Cadd9 ≠ C9).

Pop uses extensions as **colour**: maj7 and add9 for a soft, modern sound; m7 and m9 for
R&B/neo-soul; dominant 9 and 13 for funk.

## 7.4 Inversions and slash chords

The **bass note** doesn't have to be the root.

| Position | Bass note | C example | Symbol |
|---|---|---|---|
| Root position | root | C–E–G | C |
| 1st inversion | 3rd | E–G–C | C/E |
| 2nd inversion | 5th | G–C–E | C/G |
| 3rd inversion (7th chords) | 7th | B♭–C–E–G | C7/B♭ |

**Slash chords** (X/Y = chord X over bass note Y) are also used for non-chord bass notes:
D/F♯, G/B, Am/G, F/G (a soft dominant, "gospel sus"), C/B♭.

Inversions let the bass line move **stepwise** — the descending bass line
`C – G/B – Am – Am/G – F` is a pop/rock staple ("Whiter Shade of Pale", "Let It Be"-family,
"Hallelujah", countless ballads).

## 7.5 Voicing and voice leading

- **Voicing** — which octave each chord tone is in, which are doubled or omitted.
  - **Close voicing**: notes within an octave. **Open/spread**: wider, fuller.
  - In a band, avoid stacking 3rds low (below ~C3) — it gets muddy. Low register: root and 5th.
  - Leave the **root to the bass**; keys/guitar can play rootless voicings.
- **Voice leading** — move each voice to the nearest note of the next chord.
  - Keep **common tones**.
  - Move other voices by **step** where possible.
  - Resolve tendency tones: 7th of a chord falls by step; the leading tone rises to the tonic.

Example — smooth C → Am → F → G in close voicing:

```
C:  C4 E4 G4
Am: C4 E4 A4     (two common tones)
F:  C4 F4 A4     (two common tones)
G:  B3 D4 G4     (all step moves)
```

## 7.6 Diatonic chords: the chords in a key

Build a triad on each scale degree using only notes of the scale.

### Major key (C major)

| Degree | I | ii | iii | IV | V | vi | vii° |
|---|---|---|---|---|---|---|---|
| Triad | C | Dm | Em | F | G | Am | B° |
| 7th chord | Cmaj7 | Dm7 | Em7 | Fmaj7 | G7 | Am7 | Bm7♭5 |

Pattern: **Maj, min, min, Maj, Maj, min, dim**.

### Natural minor key (A minor)

| Degree | i | ii° | ♭III | iv | v | ♭VI | ♭VII |
|---|---|---|---|---|---|---|---|
| Triad | Am | B° | C | Dm | Em | F | G |
| 7th chord | Am7 | Bm7♭5 | Cmaj7 | Dm7 | Em7 | Fmaj7 | G7 |

Pattern: **min, dim, Maj, min, min, Maj, Maj**. With harmonic minor the **v becomes V (E/E7)**.

## 7.7 Harmonic function

Chords group into three **functions**:

| Function | Major-key chords | Feeling |
|---|---|---|
| **Tonic (T)** | I, vi, (iii) | Home, rest |
| **Subdominant / pre-dominant (S)** | IV, ii, (♭VI, iv borrowed) | Moving away, lift |
| **Dominant (D)** | V, V7, vii°, (♭VII in rock) | Tension, wants to return home |

The fundamental cycle **T → S → D → T** underlies most progressions (C → F → G → C).
Pop/rock frequently does **T → D → S → T** too (C → G → F → C, "retrogression"), and
cycles that never fully cadence (loops), which is a key difference from classical practice.

### Substitution

Chords of the same function can replace each other: vi for I (deceptive cadence V → vi),
ii for IV, iii for I. That's the basis of reharmonisation.

### Secondary dominants

The V of any diatonic chord can be borrowed to point at it: **V/V** (D or D7 in C, leading
to G), **V/vi** (E or E7 → Am), **V/ii** (A7 → Dm), **V/IV** (C7 → F). They add a major
chord with a note outside the key, e.g. E major in C has G♯. Very common in Beatles-era
pop, soul and ballads.

## 7.8 Chord symbols cheat sheet

```
C        major             Cm / C-   minor            C7       dominant 7th
Cmaj7    major 7th         Cm7       minor 7th        Cdim/C°  diminished
Cm7b5/Cø half-diminished   Cdim7/C°7 diminished 7th   Caug/C+  augmented
Csus2    1 2 5             Csus4     1 4 5            C5       power chord
Cadd9    1 3 5 9           C6        1 3 5 6          C9       1 3 5 b7 9
C/E      C over E bass     N.C.      no chord
```

## For the pipeline

```python
CHORD_QUALITIES = {
    "maj":  [0, 4, 7],      "min":  [0, 3, 7],      "dim":  [0, 3, 6],
    "aug":  [0, 4, 8],      "sus2": [0, 2, 7],      "sus4": [0, 5, 7],
    "5":    [0, 7],         "add9": [0, 4, 7, 14],  "6":    [0, 4, 7, 9],
    "maj7": [0, 4, 7, 11],  "7":    [0, 4, 7, 10],  "min7": [0, 3, 7, 10],
    "m7b5": [0, 3, 6, 10],  "dim7": [0, 3, 6, 9],   "9":    [0, 4, 7, 10, 14],
    "maj9": [0, 4, 7, 11, 14], "min9": [0, 3, 7, 10, 14],
}

def diatonic_triads(scale: list[int]) -> list[list[int]]:
    """Stack scale-degree thirds: degree k -> [k, k+2, k+4]."""
    n = len(scale)
    return [[scale[(k + s) % n] + 12 * ((k + s) // n) for s in (0, 2, 4)] for k in range(n)]
```

- Represent a chord as `(root_pc, quality, bass_pc | None)`; keep the Roman numeral and
  function as metadata for the progression model.
- Voice-leading cost between two voicings = sum of absolute semitone movements
  (after optimal matching); choose voicings that minimise it within a register window.
- Style determines **chord vocabulary**: punk ≈ power chords; pop ≈ triads + sus/add9;
  R&B ≈ 7ths/9ths; blues ≈ dominant 7ths everywhere.

## Exercises

1. Build all diatonic triads and sevenths in G major and E minor.
2. Play C–Am–F–G with smooth voice leading (≤ 2 semitones per voice per change).
3. Play C – G/B – Am – Am/G – F and listen to the bass line.
