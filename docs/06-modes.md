# 06 — Modes

## 6.1 What a mode is

The seven **modes** of the major scale are the same set of notes started from a different
degree, so that a different note is heard as the tonic. With C major's white keys:

| Mode | Start | Notes (white keys) | Formula vs. major | Quality |
|---|---|---|---|---|
| **Ionian** | C | C D E F G A B | 1 2 3 4 5 6 7 | = major scale |
| **Dorian** | D | D E F G A B C | 1 2 ♭3 4 5 **6** ♭7 | minor |
| **Phrygian** | E | E F G A B C D | 1 **♭2** ♭3 4 5 ♭6 ♭7 | minor |
| **Lydian** | F | F G A B C D E | 1 2 3 **♯4** 5 6 7 | major |
| **Mixolydian** | G | G A B C D E F | 1 2 3 4 5 6 **♭7** | major |
| **Aeolian** | A | A B C D E F G | 1 2 ♭3 4 5 ♭6 ♭7 | = natural minor |
| **Locrian** | B | B C D E F G A | 1 **♭2** ♭3 4 **♭5** ♭6 ♭7 | diminished |

Mnemonic: **I Don't Particularly Like Modes A Lot**.

The more useful way to think about modes is **parallel**: compare each mode to the major or
minor scale **on the same tonic**, and focus on the **characteristic note** (bold) that
makes it different.

Ordered from brightest to darkest (each step lowers one note):

```
Lydian  >  Ionian  >  Mixolydian  >  Dorian  >  Aeolian  >  Phrygian  >  Locrian
 (♯4)     (major)       (♭7)        (♭3 ♭7)    (♭3♭6♭7)    (+♭2)        (+♭5)
```

## 6.2 Each mode in pop/rock

### Ionian (major)
Standard pop major. Strong V–I pull because of the leading tone ^7.

### Mixolydian — *the* classic rock mode
- Major with a ♭7. The **♭VII chord** (e.g. in G: F major) replaces or supplements V.
- Characteristic progressions: **I–♭VII–IV–I**, **I–♭VII–I**, **♭VII–IV–I**.
- Songs: "Sweet Home Alabama" (D–C–G), "Hey Jude" coda (I–♭VII–IV–I), "Norwegian Wood",
  "Gloria" (E–D–A), "Sympathy for the Devil", "Royals" (Lorde), much AC/DC,
  "Fortunate Son".
- Also the natural sound of the **dominant 7th / blues**.

### Dorian — the "cool" minor
- Minor with a natural (major) 6th. Makes the **IV chord major** (in D Dorian: G major).
- Characteristic vamp: **i–IV** (Dm–G), or **i–♭VII** with the bright 6th in the melody.
- Songs: "Oye Como Va" (Am7–D9), "Moondance", "Evil Ways", "Scarborough Fair",
  "Another Brick in the Wall pt. 2", "Get Lucky" (Bm–D–F♯m–E),
  "Mad World", lots of funk and Santana.

### Aeolian (natural minor)
- The standard rock/pop minor. Characteristic progression: **i–♭VI–♭VII** (Am–F–G),
  **i–♭VII–♭VI–♭VII**, **i–♭VI–♭III–♭VII**.
- Songs: "All Along the Watchtower" (Am–G–F), "Stairway to Heaven" (end section),
  "Losing My Religion", "Zombie", "Rolling in the Deep".

### Phrygian — dark, heavy, Spanish
- Minor with a ♭2. The **♭II chord** (in E: F major) a semitone above the tonic is the hallmark.
- Characteristic move: **i–♭II** (Em–F), and riffs that hit the ♭2 right after the root.
- Metal (Metallica "Wherever I May Roam", much death/thrash),
  flamenco ("Andalusian cadence" iv–♭III–♭II–I: Am–G–F–E, as in "Hit the Road Jack",
  "Sultans of Swing").
- **Phrygian dominant** (major 3rd added) = the Middle-Eastern/"Misirlou" sound.

### Lydian — dreamy, floating, "wonder"
- Major with a ♯4. The **II major chord** (in F: G major) is the hallmark: **I–II** vamp.
- Songs: "The Simpsons" theme, "Flying in a Blue Dream" (Satriani), "Dreams" (Fleetwood Mac),
  "Man on the Moon" (R.E.M.) verse, much film music (John Williams), Steve Vai.

### Locrian — unstable
- Diminished tonic chord makes it hard to feel as home. Rare; appears in metal riffs
  (Slayer, Meshuggah-adjacent, "Army of Me" by Björk is often cited).

## 6.3 How to "sound" a mode

A mode only sounds modal if the **tonic is established** and the **characteristic note is
emphasised**. Practical techniques:

1. **Drone or pedal** the tonic (bass stays on the root).
2. **Vamp** on the tonic chord and the chord containing the characteristic note
   (Mixolydian I–♭VII, Dorian i–IV, Lydian I–II, Phrygian i–♭II).
3. **Avoid the major V–I cadence**, which pulls the ear back to Ionian/Aeolian.
4. Put the characteristic note on **strong beats / long notes** in the melody.

## 6.4 Modes of other scales (brief)

Every scale has modes. Two of practical use:

- **Phrygian dominant** — 5th mode of harmonic minor (1 ♭2 3 4 5 ♭6 ♭7).
- **Lydian dominant** — 4th mode of melodic minor (1 2 3 ♯4 5 6 ♭7), the "Simpsons" /
  fusion sound.

## For the pipeline

```python
MODES = ["ionian", "dorian", "phrygian", "lydian", "mixolydian", "aeolian", "locrian"]
MAJOR = [0, 2, 4, 5, 7, 9, 11]

def mode_intervals(mode: str) -> list[int]:
    k = MODES.index(mode)
    rotated = MAJOR[k:] + [x + 12 for x in MAJOR[:k]]
    return [x - rotated[0] for x in rotated]

CHARACTERISTIC = {           # semitone offset of the mode's colour note
    "dorian": 9, "phrygian": 1, "lydian": 6,
    "mixolydian": 10, "locrian": 6,
}
SIGNATURE_PROGRESSIONS = {   # Roman numerals relative to the modal tonic
    "mixolydian": [["I", "bVII", "IV", "I"], ["I", "bVII", "I"]],
    "dorian":     [["i", "IV"], ["i", "bVII", "IV", "i"]],
    "aeolian":    [["i", "bVI", "bVII", "i"], ["i", "bVII", "bVI", "bVII"]],
    "phrygian":   [["i", "bII", "i"], ["iv", "bIII", "bII", "I"]],
    "lydian":     [["I", "II", "I"], ["I", "II", "vii", "I"]],
}
```

- A **mode choice** is a high-level "mood" parameter: bright → Lydian/Ionian, rocky →
  Mixolydian, cool/funky → Dorian, sad/epic → Aeolian, heavy/dark → Phrygian.

## Exercises

1. Play an A drone and improvise with A Dorian (A B C D E F♯ G), then A Aeolian (F natural).
   Hear the difference of the 6th.
2. Play G–F–C–G repeatedly. What mode is that? (G Mixolydian.)
3. Write a 4-bar riff in E Phrygian that uses the F prominently.
