# 05 — Keys and the Circle of Fifths

## 5.1 What a key is

A **key** is a tonal centre (tonic) plus a scale (usually major or minor). "This song is in
G major" means G is home and the notes of the G major scale form the main palette.
A **key signature** lists the sharps or flats that apply throughout.

## 5.2 The circle of fifths

Arrange the 12 keys so each is a **perfect fifth** above the previous one. Going clockwise
adds one sharp (or removes a flat); going counter-clockwise adds one flat.

```
                         C / Am
                  F / Dm    0     G / Em
                  1♭               1♯
         B♭ / Gm                          D / Bm
           2♭                               2♯

     E♭ / Cm                                   A / F♯m
       3♭                                        3♯

         A♭ / Fm                          E / C♯m
           4♭                               4♯
                  D♭ / B♭m          B / G♯m
                    5♭                5♯
                      G♭ / E♭m = F♯ / D♯m
                          6♭   =   6♯
```

Clockwise (up a 5th): C → G → D → A → E → B → F♯/G♭ → D♭ → A♭ → E♭ → B♭ → F → C

| Major | Relative minor | Signature | Sharps/flats |
|---|---|---|---|
| C | A m | — | — |
| G | E m | 1♯ | F♯ |
| D | B m | 2♯ | F♯ C♯ |
| A | F♯ m | 3♯ | F♯ C♯ G♯ |
| E | C♯ m | 4♯ | F♯ C♯ G♯ D♯ |
| B | G♯ m | 5♯ | F♯ C♯ G♯ D♯ A♯ |
| F♯ / G♭ | D♯ m / E♭ m | 6♯ / 6♭ | |
| D♭ | B♭ m | 5♭ | B♭ E♭ A♭ D♭ G♭ |
| A♭ | F m | 4♭ | B♭ E♭ A♭ D♭ |
| E♭ | C m | 3♭ | B♭ E♭ A♭ |
| B♭ | G m | 2♭ | B♭ E♭ |
| F | D m | 1♭ | B♭ |

Order of sharps: **F C G D A E B** ("Father Charles Goes Down And Ends Battle").
Order of flats: the reverse, **B E A D G C F**.

### Why the circle matters

1. **Neighbouring keys are closely related** — they share 6 of 7 notes. Modulating to a
   neighbour sounds smooth; jumping across the circle sounds dramatic.
2. **The diatonic chords of a key are clustered together**: for C major, the three major
   chords are F, C, G (the key and its two neighbours), and the three minor chords are
   their relative minors Dm, Am, Em. Six of the seven chords are in one "slice".
3. **Root movement by fifths is the strongest harmonic motion**. Moving counter-clockwise
   (down a fifth, e.g. G → C) is the classic **V → I resolution**. Jazz "ii–V–I" and
   "circle progressions" (e.g. Am–Dm–G–C) walk around it.
4. **Rock often moves clockwise "backwards"** (e.g. C → G → D, the I–V–II or ♭VII–IV–I
   "Mixolydian" motions like D–C–G in "Sweet Home Alabama"). Plagal and ♭VII motion
   is part of rock's sound versus classical/jazz's V–I.

## 5.3 Relative and parallel keys

- **Relative** keys share a key signature: C major ↔ A minor. The relative minor's tonic is
  ^6 of the major key (or 3 semitones below the major tonic).
- **Parallel** keys share a tonic: C major ↔ C minor. Borrowing chords from the parallel
  key is called **modal mixture** (chapter 08) and is everywhere in rock.

Many pop songs are ambiguous between relative keys: the verse sits on vi (Am) and the
chorus lands on I (C), or vice versa. Example: the "vi–IV–I–V" loop can be heard as either
A minor or C major.

## 5.4 Finding the key of a song

1. What chord feels like "home"? Usually the first and/or last chord, and the chorus target.
2. Which notes are used? Match them to a key signature.
3. Look for the V → I cadence (or ♭VII → I, IV → I in rock).
4. Watch for a raised 7th (G♯ in A minor) — that implies minor with a major V.

## 5.5 Popular keys in pop/rock

Keys are chosen for **singer range** and **instrument convenience**:

- **Guitar-driven rock**: E, A, D, G, C, and their minors (Em, Am, Bm) — open strings ring.
  Metal: E/Em, D (drop D), and down-tuned keys (C♯, C, B).
- **Piano-driven pop**: C, F, G, B♭, E♭, A♭ also common.
- **Horn-driven (funk, soul)**: flat keys — B♭, E♭, F.
- Statistically, **C, G, D, A, E** major and **Am, Em** are the most common in pop catalogues.

## 5.6 Modulation (key changes)

| Type | How | Example |
|---|---|---|
| **Truck-driver's change** | Final chorus up a semitone or whole tone, often abruptly | "Man in the Mirror", "Livin' on a Prayer", "Love on Top" (multiple) |
| Pivot-chord modulation | Use a chord common to both keys to slide into the new one | Common in ballads, Beatles |
| Direct/abrupt | Just start in the new key at a section boundary | Chorus in a new key |
| Relative major/minor shift | Verse in minor, chorus in relative major | "Ain't No Sunshine"-style shifts; very common |
| Chromatic mediant | Jump to a key a major/minor 3rd away | Film-like, dramatic (C → E, C → A♭) |

A **dominant pivot** (playing V of the new key before it arrives) makes a key change feel
prepared rather than jarring.

## For the pipeline

```python
CIRCLE_MAJOR = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]  # C G D A E B F# Db Ab Eb Bb F

def fifths_distance(key_a: int, key_b: int) -> int:
    """Number of steps between two major keys on the circle (0..6)."""
    i, j = CIRCLE_MAJOR.index(key_a), CIRCLE_MAJOR.index(key_b)
    d = abs(i - j)
    return min(d, 12 - d)

def relative_minor(major_pc: int) -> int:
    return (major_pc + 9) % 12

def prefers_flats(major_pc: int) -> bool:
    return major_pc in {5, 10, 3, 8, 1, 6}  # F Bb Eb Ab Db Gb
```

- Pick the song key from the **vocal range** first, then from style (guitar-friendly keys
  for rock).
- Modulations can be scored by circle distance; for a final-chorus lift, +1 or +2
  semitones regardless of circle distance is idiomatic.
- In komposoija a section's key can be relative to the song key:
  `song.section("last_chorus", like="chorus", key="+1")`. For a dominant pivot, end the
  previous section on the new key's V: for C → D that is `V7/ii` (A7) in C.

## Exercises

1. Without looking, name the key signatures of A major, E♭ major and B minor.
2. What are the three major and three minor diatonic chords in G major? (G C D / Em Am Bm.)
3. Transpose "C–G–Am–F" to D, E and B♭.
