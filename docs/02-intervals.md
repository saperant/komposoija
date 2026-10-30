# 02 — Intervals

An **interval** is the distance between two pitches. Intervals are the atoms of harmony and
melody: chords are stacks of intervals, scales are sequences of them, and the "feel" of a
melody comes largely from the intervals it moves by.

- **Melodic interval** — two notes played one after another.
- **Harmonic interval** — two notes played together.

## 2.1 Interval names

An interval has a **number** (count letter names inclusively: C→E = C, D, E = a 3rd) and a
**quality** (major, minor, perfect, augmented, diminished).

| Semitones | Name | Short | Example from C | Character |
|---|---|---|---|---|
| 0 | Perfect unison | P1 | C–C | identical |
| 1 | Minor 2nd | m2 | C–D♭ | harsh, tense, "Jaws" |
| 2 | Major 2nd | M2 | C–D | step, mild tension |
| 3 | Minor 3rd | m3 | C–E♭ | sad/dark, defines minor |
| 4 | Major 3rd | M3 | C–E | bright, defines major |
| 5 | Perfect 4th | P4 | C–F | open, "Here Comes the Bride" |
| 6 | Augmented 4th / Diminished 5th (tritone) | A4/d5 | C–F♯ / C–G♭ | unstable, bluesy, metal |
| 7 | Perfect 5th | P5 | C–G | strong, stable, "power chord" |
| 8 | Minor 6th | m6 | C–A♭ | bittersweet |
| 9 | Major 6th | M6 | C–A | sweet, "My Bonnie" |
| 10 | Minor 7th | m7 | C–B♭ | bluesy, wants to resolve |
| 11 | Major 7th | M7 | C–B | dreamy/tense, jazzy |
| 12 | Perfect octave | P8 | C–C' | same note, higher |

Intervals larger than an octave are **compound intervals**: 9th = octave + 2nd (14 st),
11th = octave + 4th (17 st), 13th = octave + 6th (21 st). These names appear in chord
extensions (Cadd9, C11, C13).

### Rules of quality

- Unisons, 4ths, 5ths and octaves are **perfect** (they can be augmented or diminished but
  are never "major/minor").
- 2nds, 3rds, 6ths and 7ths are **major** or **minor**.
- One semitone larger than major/perfect = **augmented**; one smaller than minor/perfect =
  **diminished**.

## 2.2 Consonance and dissonance

Roughly, from most stable to most tense (in a pop/rock context):

1. **Perfect consonances**: unison, octave, perfect 5th, (perfect 4th)
2. **Imperfect consonances**: major/minor 3rds, major/minor 6ths
3. **Mild dissonances**: major 2nd, minor 7th
4. **Sharp dissonances**: minor 2nd, major 7th, tritone

Dissonance is not "bad" — it creates **tension** that wants to **resolve** to consonance.
Songs are built on cycles of tension and release.

Distortion changes the picture: heavily distorted guitars make 3rds sound muddy, which is why
rock and metal guitarists play **power chords** (root + 5th + octave) instead of full triads.

## 2.3 Interval inversion

Flip an interval (move the lower note up an octave) and:

- The numbers add to **9** (3rd ↔ 6th, 2nd ↔ 7th, 4th ↔ 5th).
- Major ↔ minor, augmented ↔ diminished, perfect stays perfect.
- Semitones add to **12**.

So C up to G is a P5 (7 st); G up to C is a P4 (5 st).

## 2.4 Recognising intervals by ear (song references)

| Interval | Ascending | Descending |
|---|---|---|
| m2 | "Jaws" theme | "Für Elise" (first two notes) |
| M2 | "Happy Birthday" (2nd→3rd syllables) | "Yesterday" (Beatles) |
| m3 | "Smoke on the Water" riff (1st→2nd) | "Hey Jude" ("Hey Jude") |
| M3 | "When the Saints Go Marching In" | "Swing Low, Sweet Chariot" |
| P4 | "Here Comes the Bride", "Amazing Grace" | "Born Free" |
| Tritone | "Maria" (West Side Story), "The Simpsons" theme | "Purple Haze" intro (E–B♭, harmonic) |
| P5 | "Twinkle Twinkle", "Star Wars" main theme | "Flintstones" |
| m6 | "The Entertainer" (3rd→4th notes) | "Love Story" theme |
| M6 | "My Bonnie Lies Over the Ocean", NBC chime | "Nobody Knows the Trouble" |
| m7 | "Somewhere" (West Side Story), original "Star Trek" theme | "Watermelon Man" |
| M7 | "Don't Know Why" (Norah Jones, opening "I waited") | "I Love You" (Cole Porter) |
| P8 | "Somewhere Over the Rainbow" | "Willow Weep for Me" |

## 2.5 Intervals in melody

- **Steps** (m2, M2) make smooth, singable lines — most pop melody notes move by step.
- **Leaps** (3rd and larger) add drama and emphasis; hooks often feature one memorable leap.
- A common rule: **after a large leap, move by step in the opposite direction** ("gap fill").
- Vocal melodies rarely leap more than an octave.

## For the pipeline

- An interval is just `b - a` in MIDI numbers; interval class = `abs(b - a) % 12`.
- Assign a **dissonance score** per interval class for scoring harmonies, e.g.:

```python
# 0 = most consonant. Rough, context-free; tune empirically.
DISSONANCE = {0: 0, 7: 1, 5: 2, 4: 2, 3: 2, 9: 3, 8: 3, 2: 5, 10: 5, 6: 7, 11: 8, 1: 9}
```

- Melody generators should weight steps much more heavily than leaps (e.g. ~65–75 % steps
  or repeated notes, ~25–35 % leaps, mostly ≤ P5).
- Avoid **parallel octaves/fifths** between melody and bass only if aiming for "classical"
  smoothness — in rock, parallel fifths (power chords) are the norm.

## Exercises

1. Name the interval: E–B, F–B, A–C, D–C♯ (above), G–E♭ (above).
2. Invert each one and name the result.
3. Sing a major 3rd and a minor 3rd above any note and describe the difference.
