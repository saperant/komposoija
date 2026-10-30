# 10 — Song Structure

**Song form** is the order and length of sections. Pop/rock forms are highly conventional,
which makes them easy to model.

## 10.1 Section types

| Section | Abbr. | Purpose | Typical length | Energy |
|---|---|---|---|---|
| **Intro** | I | Set key, tempo, mood; often previews the hook/riff | 2–8 bars (4 most common) | Low–mid |
| **Verse** | V | Tells the story; lyrics change each time, music repeats | 8 or 16 bars | Low–mid |
| **Pre-chorus** (build, lift, channel) | PC | Builds tension towards the chorus | 4 or 8 bars | Rising |
| **Chorus** (refrain) | C | Main hook and title; same lyrics each time | 8 bars (sometimes 16) | High |
| **Post-chorus** | PoC | Extra hook after the chorus (vocal chop, chant, riff) | 4–8 bars | High |
| **Bridge** (middle eight) | B | Contrast: new chords, melody, perspective | 4–8 bars (8 classic) | Variable, often dips then rises |
| **Instrumental / solo** | S | Guitar/synth solo over verse or chorus chords | 8–16 bars | Mid–high |
| **Breakdown** | BD | Stripped back section, sometimes before the last chorus | 4–8 bars | Low → rising |
| **Interlude / turnaround** | — | Short instrumental link (often the intro riff) | 2–4 bars | Mid |
| **Drop** (EDM-pop) | D | Instrumental climax after a build, replaces/augments chorus | 8–16 bars | Highest |
| **Outro** (coda) | O | Ending: fade-out, repeated chorus tag, or final hit | 4–16 bars | Varies |
| **Refrain** (in AABA) | — | A line repeated at the end of each verse (not a separate section) | 1–2 bars | — |

## 10.2 Common forms

### Verse–chorus (the modern standard)

```
Intro – V1 – C – V2 – C – Bridge – C – C – Outro
```

With pre-chorus (very common since the 1980s):

```
Intro – V1 – PC – C – V2 – PC – C – Bridge – C (– C) – Outro
```

Modern pop variants:
- **Start with the chorus** (or a chorus snippet) to hook listeners immediately.
- **Shorter intros** (< 10 s) in the streaming era.
- **Post-chorus** after each chorus.
- **Verse 2 is often half-length** (8 bars instead of 16) to reach the chorus sooner.
- **Breakdown / bridge → final chorus with key change or bigger arrangement**.

### AABA (32-bar song form)

```
A (8) – A (8) – B (8, bridge) – A (8)
```

Tin Pan Alley, early Beatles ("Yesterday", "From Me to You"), many standards. The title
usually appears at the start or end of each A section (refrain). No separate chorus.

### Verse-only / strophic (AAA)

All sections share the same music, lyrics change. Folk, early blues, "Like a Rolling Stone"
(really verse–refrain), "The Times They Are a-Changin'". Repetition is broken up with
instrumental breaks.

### 12-bar blues form

Each verse = one 12-bar blues chorus. Solos are more 12-bar choruses. See chapter 08.

### Verse–chorus–bridge (rock variant)

```
Intro (riff) – V1 – C – V2 – C – Solo – Bridge – C – C – Outro (riff)
```

### Through-composed / suite

No repeating sections — rare in pop ("Bohemian Rhapsody", "A Day in the Life", prog rock).

## 10.3 Typical timings

At ~120 BPM in 4/4, one bar = 2 s, so 8 bars ≈ 16 s.

```
Section     Bars  ~Seconds @120BPM    Cumulative
Intro          4     8                 0:08
Verse 1       16    32                 0:40
Pre-chorus     4     8                 0:48
Chorus         8    16                 1:04
Verse 2        8    16                 1:20
Pre-chorus     4     8                 1:28
Chorus         8    16                 1:44
Bridge         8    16                 2:00
Chorus x2     16    32                 2:32
Outro          4     8                 2:40
```

Target total: **2:30–3:45** for pop; first chorus should start by **~0:45–1:00**.
Rock and ballads can run longer (4–6 min).

## 10.4 What changes between sections

Listeners must feel a section change. Change **at least two or three** of:

- Chord progression (different loop, start chord, or harmonic rhythm)
- Melody register and rhythm (chapter 09)
- Drum pattern (e.g. verse: hi-hat; chorus: ride/crash, open hi-hat, busier kick)
- Bass pattern (verse: sustained roots; chorus: driving eighths)
- Arrangement density (instruments added/removed)
- Dynamics / loudness
- Vocal treatment (single → doubled/harmonies)

And **transitions** between sections use: drum fills, risers/sweeps, a pickup, a stop or
dropout, a reverse cymbal, or a chord on the "& of 4" anticipation.

## 10.5 Energy arc

Most pop/rock songs follow a stepwise **rising energy curve** with dips:

```
Section      Energy (0–10)
Intro        ███
Verse 1      ████
Pre-chorus   ██████
Chorus 1     ████████
Verse 2      █████
Pre-chorus   ███████
Chorus 2     █████████
Bridge       █████          (dip, then build)
Chorus 3     ██████████     (peak: biggest arrangement, maybe key change)
Outro        ████
```

- Verse 2 slightly higher energy than verse 1 (extra instrument, busier drums).
- Bridge often dips (or builds from a dip), so the final chorus can be the peak.
- Final chorus: biggest arrangement, ad-libs, maybe a key change.

## For the pipeline

```python
from dataclasses import dataclass

@dataclass
class Section:
    kind: str          # "intro" | "verse" | "prechorus" | "chorus" | "bridge" | ...
    bars: int
    energy: float      # 0..1, drives arrangement density, drum/bass patterns
    progression: str   # template name or explicit numerals
    ends_with: str     # "fill" | "stop" | "riser" | "none"

FORMS = {
    "pop_standard": ["intro", "verse", "prechorus", "chorus", "verse", "prechorus",
                     "chorus", "bridge", "chorus", "chorus", "outro"],
    "rock_solo":    ["intro", "verse", "chorus", "verse", "chorus", "solo",
                     "bridge", "chorus", "outro"],
    "aaba":         ["A", "A", "B", "A"],
    "chorus_first": ["chorus", "verse", "chorus", "verse", "chorus", "bridge",
                     "chorus", "outro"],
}

DEFAULT_ENERGY = {"intro": 0.3, "verse": 0.4, "prechorus": 0.6, "chorus": 0.85,
                  "postchorus": 0.85, "bridge": 0.55, "solo": 0.75, "breakdown": 0.3,
                  "outro": 0.4}
```

- Treat the **form** as the top of the generation hierarchy: form → per-section key/
  progression/energy → parts (drums, bass, chords, melody) → humanisation.
- **Reuse** material: verse 2 = verse 1 music (with variations), all choruses share
  harmony and melody. Repetition is what makes songs feel like songs.
- Increase energy on repeats (+0.05–0.1 per repetition) so the arc rises.

## Exercises

1. Map the form of three songs you like, with bar counts.
2. Find a song that starts with the chorus and one with a key change in the final chorus.
3. Sketch an energy curve for "Smells Like Teen Spirit" (loud/quiet dynamics).
