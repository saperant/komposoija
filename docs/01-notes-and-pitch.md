# 01 — Notes and Pitch

## 1.1 What a note is

A **note** is a sound with a definite **pitch** (how high or low it is) and a **duration**
(how long it lasts). Physically, pitch is the frequency of vibration, measured in hertz (Hz).
A note also has **loudness** (dynamics) and **timbre** (tone colour — why a guitar and a
piano playing the same note sound different).

## 1.2 The musical alphabet

Western music uses seven letter names that repeat:

```
A  B  C  D  E  F  G  A  B  C ...
```

The distance from one note to the next note with the same name (e.g. C to the next C) is an
**octave**. A note one octave higher has exactly **double the frequency** (A4 = 440 Hz,
A5 = 880 Hz). Our ears hear octaves as "the same note, higher", which is why they share a name.

## 1.3 The twelve-tone chromatic system

An octave is divided into **12 equal steps** called **semitones** (half steps). Seven of
these pitches have plain letter names (the white keys on a piano); the other five sit between
them (the black keys) and are named with **accidentals**:

- **♯ sharp** — raise by one semitone (C♯ is one semitone above C)
- **♭ flat** — lower by one semitone (D♭ is one semitone below D)
- **♮ natural** — cancel a sharp or flat
- (𝄪 double sharp and 𝄫 double flat exist but are rare in pop)

```
Piano keyboard, one octave:

 | C♯ | D♯ |   | F♯ | G♯ | A♯ |
 | D♭ | E♭ |   | G♭ | A♭ | B♭ |
C    D    E    F    G    A    B    C
```

Notice there is **no black key between E–F and B–C**: those pairs are already only one
semitone apart. All other neighbouring white keys are two semitones (a **whole step / tone**)
apart.

| Pitch class | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sharp name | C | C♯ | D | D♯ | E | F | F♯ | G | G♯ | A | A♯ | B |
| Flat name  | C | D♭ | D | E♭ | E | F | G♭ | G | A♭ | A | B♭ | B |

### Enharmonic equivalents

C♯ and D♭ are the **same key on the piano** but are spelled differently. They are
**enharmonic**. Which spelling to use depends on the key: in A major you write C♯ (every
letter appears once in a scale), in A♭ major you write D♭. Getting spelling right matters for
readable notation, but for audio/MIDI generation the pitch class number is all that counts.

## 1.4 Octave numbering (scientific pitch notation)

Each octave is numbered, starting a new number at C:

- **C4 = middle C** (around the middle of the piano, ~261.63 Hz)
- A4 = 440 Hz — the standard tuning reference ("concert pitch")
- B3 is just below C4; C5 is one octave above C4.

Typical ranges in a pop/rock band:

| Instrument | Approx. range | Notes |
|---|---|---|
| Bass guitar (4-string) | E1 – G4 (practical: E1–C4) | Most bass lines live in E1–E3 |
| Guitar (standard tuning) | E2 – ~E6 | Rhythm guitar: E2–E5 |
| Male vocal (tenor/baritone) | ~A2 – A4 | Pop tenor belts to A4–C5 |
| Female vocal (alto/soprano) | ~F3 – C6 | Most pop melodies F3–E5 |
| Piano | A0 – C8 | |
| Kick drum fundamental | ~40–100 Hz | Unpitched-ish |

## 1.5 Frequency and tuning

Modern Western music uses **12-tone equal temperament (12-TET)**: every semitone is the same
frequency ratio, the twelfth root of 2 ≈ 1.05946.

```
f(n) = 440 × 2^((n − 69) / 12)        where n is the MIDI note number
```

Some genres deliberately tune differently: e.g. drop-D or down-tuned guitars in metal,
or 432 Hz reference by some artists — but the internal 12-TET structure stays the same.

## 1.6 Note durations (preview)

| Name (US) | Name (UK) | Beats in 4/4 |
|---|---|---|
| Whole note | Semibreve | 4 |
| Half note | Minim | 2 |
| Quarter note | Crotchet | 1 |
| Eighth note | Quaver | 1/2 |
| Sixteenth note | Semiquaver | 1/4 |
| Thirty-second | Demisemiquaver | 1/8 |

A **dot** adds half the value (dotted quarter = 1.5 beats). A **tie** joins two notes into one
longer sound. A **triplet** fits three notes in the time of two. See chapter 03.

## 1.7 Reading notation (minimum you need)

- **Treble clef** (𝄞): guitar, vocals, keyboard right hand. Lines bottom→top: E G B D F
  ("Every Good Boy Does Fine"); spaces: F A C E.
- **Bass clef** (𝄢): bass guitar, keyboard left hand. Lines: G B D F A
  ("Good Boys Do Fine Always"); spaces: A C E G ("All Cows Eat Grass").
- Guitar and bass are written **one octave higher** than they sound.
- Pop/rock musicians often read **chord charts**, **lead sheets** (melody + chord symbols)
  or **tablature** instead of full notation.

## For the pipeline

- Represent pitch as **MIDI note number** (0–127). Pitch class = `n % 12`, octave = `n // 12 − 1`.
- Keep a separate **spelling** layer only if we output notation; choose sharps vs. flats from
  the key signature (chapter 05).
- Constrain each generated part to an instrument **range** table like the one above; clamp or
  re-voice notes that fall outside.

```python
NOTE_NAMES_SHARP = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

def midi_to_name(n: int) -> str:
    return f"{NOTE_NAMES_SHARP[n % 12]}{n // 12 - 1}"

def midi_to_hz(n: float) -> float:
    return 440.0 * 2 ** ((n - 69) / 12)
```

## Exercises

1. Name every black key with both its sharp and flat name.
2. Which MIDI number is E2 (the low string of a guitar)? (Answer: 40.)
3. What is the frequency of A3? (220 Hz.)
