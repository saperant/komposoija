# 04 — Scales

A **scale** is an ordered set of pitches within an octave, defined by its pattern of
intervals. A scale gives a song its "palette" of notes. The first note is the **tonic**
(home note, scale degree ^1).

Abbreviations: **W** = whole step (2 semitones), **H** = half step (1 semitone),
**W+H** = augmented 2nd (3 semitones).

## 4.1 The major scale

```
Pattern:     W   W   H   W   W   W   H
Degrees:   1   2   3   4   5   6   7   8(1)
C major:   C   D   E   F   G   A   B   C
Semitones: 0   2   4   5   7   9  11  12
```

The major scale is the reference for almost all theory: chords, modes, and intervals are
described relative to it. It sounds bright, resolved and "happy".

### Scale-degree names and tendencies

| Degree | Name | Tendency in a major key |
|---|---|---|
| ^1 | Tonic | Home, total rest |
| ^2 | Supertonic | Passing tone; tends to fall to ^1 or rise to ^3 |
| ^3 | Mediant | Stable (chord tone of I) — defines major/minor |
| ^4 | Subdominant | Tends to fall to ^3 |
| ^5 | Dominant | Stable, strong; second "home" |
| ^6 | Submediant | Tends to fall to ^5 |
| ^7 | Leading tone | Strongly wants to rise to ^1 |

**Stable tones** of a major key: ^1, ^3, ^5 (the tonic triad). Others are **tendency tones**.
Melodies that end on ^1 sound finished; ending on ^3 or ^5 is softer; ending on ^2 or ^7
sounds like a question.

## 4.2 The minor scales

### Natural minor (Aeolian)

```
Pattern:   W   H   W   W   H   W   W
A minor:   A   B   C   D   E   F   G   A
Relative to major: 1  2  ♭3  4  5  ♭6  ♭7
```

Same notes as C major, starting on A: A minor is the **relative minor** of C major.
Natural minor is the dominant minor sound of rock and pop ("Losing My Religion",
"Rolling in the Deep", "Zombie", "All Along the Watchtower").

### Harmonic minor

```
A harmonic minor: A  B  C  D  E  F  G♯  A      (1 2 ♭3 4 5 ♭6 7)
```

Raises the 7th so the V chord becomes **major** (E instead of Em), giving a strong pull
back to the tonic. The augmented 2nd between ♭6 and 7 (F–G♯) gives an "exotic",
neo-classical sound used in metal (Yngwie Malmsteen, Iron Maiden-ish leads).

### Melodic minor

```
A melodic minor (ascending / "jazz minor"): A  B  C  D  E  F♯  G♯  A   (1 2 ♭3 4 5 6 7)
```

Classically it reverts to natural minor descending. Rare as a whole in pop; it shows up in
jazz and some film music. The raised 6th (Dorian flavour) is common in pop, though.

**In practice**: pop/rock in a minor key mostly uses natural minor, but freely swaps in
the **major V chord** (from harmonic minor) for stronger cadences.

## 4.3 Pentatonic scales — the backbone of rock

Five-note scales without semitones; nothing "clashes", so they work over almost any chord
in the key. **The most-used scales in rock guitar and pop vocal melody.**

```
Major pentatonic:  1  2  3  5  6         C D E G A
Minor pentatonic:  1 ♭3  4  5 ♭7         A C D E G   (same notes as C major pentatonic)
```

- **Major pentatonic** — bright, country, classic pop ("My Girl", "Sweet Child o' Mine" solo
  sections, much of Motown).
- **Minor pentatonic** — the rock/blues sound: virtually every classic rock riff and solo
  ("Stairway to Heaven" solo, "Back in Black", "Smells Like Teen Spirit" lead parts).

Pentatonic melodies are naturally singable and catchy — a big reason they dominate hooks.

## 4.4 The blues scale

```
Minor blues scale: 1  ♭3  4  ♭5  5  ♭7        A C D E♭ E G
Major blues scale: 1  2  ♭3  3  5  6          C D E♭ E G A
```

The added **♭5 ("blue note")** is used as a passing/bending tone. Blues notes (♭3, ♭5, ♭7)
are often played **over major chords** — the clash of a minor 3rd against a major chord is the
essence of blues and rock. Guitarists bend the ♭3 slightly sharp, "between" minor and major.

## 4.5 Other scales you'll encounter

| Scale | Formula | Where |
|---|---|---|
| Chromatic | all 12 semitones | Passing tones, runs, chromatic bass walk-ups |
| Mixolydian | 1 2 3 4 5 6 ♭7 | Classic rock, see chapter 06 |
| Dorian | 1 2 ♭3 4 5 6 ♭7 | Funk, rock, see chapter 06 |
| Phrygian | 1 ♭2 ♭3 4 5 ♭6 ♭7 | Metal, flamenco |
| Phrygian dominant | 1 ♭2 3 4 5 ♭6 ♭7 | Metal, Middle-Eastern flavour (5th mode of harmonic minor) |
| Whole-tone | 1 2 3 ♯4 ♯5 ♭7 | Dreamy/unsettled; Stevie Wonder "You Are the Sunshine of My Life" intro |
| Diminished (half-whole) | H W H W H W H W | Jazz, metal, tension |

## 4.6 Which scale for which chord? (pop/rock rule of thumb)

- Over a **major-key** song: major scale or major pentatonic; add minor pentatonic/blues notes
  for grit.
- Over a **minor-key** song: natural minor or minor pentatonic.
- Over a **blues / dominant-7th** progression: minor pentatonic + blues note, mixed with
  Mixolydian/major pentatonic per chord.
- Over a **modal vamp**: the matching mode (chapter 06).

## For the pipeline

Store scales as interval sets from the root. Everything else (transposition, chord-building,
melody constraints) falls out of that.

```python
SCALES = {
    "major":            [0, 2, 4, 5, 7, 9, 11],
    "natural_minor":    [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor":   [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor":    [0, 2, 3, 5, 7, 9, 11],
    "major_pentatonic": [0, 2, 4, 7, 9],
    "minor_pentatonic": [0, 3, 5, 7, 10],
    "blues":            [0, 3, 5, 6, 7, 10],
    "major_blues":      [0, 2, 3, 4, 7, 9],
    "dorian":           [0, 2, 3, 5, 7, 9, 10],
    "phrygian":         [0, 1, 3, 5, 7, 8, 10],
    "lydian":           [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":       [0, 2, 4, 5, 7, 9, 10],
    "locrian":          [0, 1, 3, 5, 6, 8, 10],
    "phrygian_dominant":[0, 1, 4, 5, 7, 8, 10],
}

def scale_pitches(root_pc: int, scale: str) -> set[int]:
    return {(root_pc + i) % 12 for i in SCALES[scale]}
```

- Give each scale degree a **stability weight** for melody generation (e.g. chord tones and
  ^1/^5 high on strong beats; ^4 and ^7 low unless resolving).
- Pentatonic subsets are a safe default for hooks.

## Exercises

1. Write out G major, D major, F major (watch the sharps/flats).
2. Write E natural minor, E harmonic minor, E minor pentatonic.
3. Improvise over a looped Am chord using only A minor pentatonic, then add the E♭.
