# 17 — Blues

The blues came from African-American communities in the Mississippi Delta and the American
South around 1900. It is the root of jazz, rhythm & blues, rock'n'roll, soul and rock. Its
essentials are a **fixed form** (usually 12 bars), **dominant-seventh harmony**, **blue
notes** sung and played against that harmony, the **shuffle** feel, and **call and response**.

## 17.1 Forms

### 12-bar blues

The standard form (chapter 08), in A:

```
| A7  | A7  | A7  | A7  |       I7   I7   I7   I7
| D7  | D7  | A7  | A7  |       IV7  IV7  I7   I7
| E7  | D7  | A7  | E7  |       V7   IV7  I7   V7 (turnaround)
```

Variants:

| Variant | Change | Notes |
|---|---|---|
| **Quick change** | bar 2 → IV7 | very common in Chicago and Texas blues |
| **V–V ending** | bar 10 → V7 instead of IV7 | older/country style |
| **Minor blues** | i7 i7 i7 i7 / iv7 iv7 i7 i7 / ♭VI7 V7 i7 V7 | slow, dramatic; "The Thrill Is Gone" type |
| **Jazz blues** | I7 IV7 I7 (v7 I7) / IV7 ♯iv°7 I7 VI7 / ii7 V7 (I7 VI7) (ii7 V7) | more ii–Vs (chapter 16) |
| **8-bar blues** | I7 V7 IV7 IV7 / I7 V7 I7 V7 | "Key to the Highway" type |
| **16-bar blues** | usually the opening I7 extended to 8 bars, then the last 8 bars of the 12-bar | room for longer lyric lines |

### Turnarounds, intros and endings

- **Turnaround**: the last two bars lead back to the top: | I7 IV7 | I7 V7 |, or a chromatic
  line descending over I7 (guitar or piano), resolving on V7.
- **Intro "from the V"**: start at bar 9 (V7 IV7 I7 V7) — four bars that set key and groove.
- **Endings**: the turnaround resolves to a final I7 (or I9), often approached by **♭II7 → I7**
  (a half step above), or a stop on the last chord with a guitar lick.

## 17.2 Harmony and the blue notes

- Every chord is usually a **dominant 7th** — even the tonic, which is unusual in functional
  harmony and gives the blues its unresolved, earthy colour.
- **Blue notes**: ♭3, ♭5 and ♭7 of the key, played over major-sounding chords. The ♭3 over a
  I7 chord is the defining blues clash; singers and guitarists bend it slightly sharp, between
  minor and major 3rd.
- Melodies mix **minor pentatonic + blues scale** with the **major pentatonic** (chapter 04):
  minor for grit, major for sweetness. B.B. King moves between them constantly.
- Over the IV7 chord, the ♭7 of IV (the ♭3 of the key) becomes a chord tone — which is why the
  minor-pentatonic sound "fits" everywhere.

## 17.3 Melody and lyrics

- **AAB lyric form**: a line, the same line again (often over IV), and an answering line that
  resolves (over V–IV–I).
- Each vocal line takes roughly the first two bars of its 4-bar phrase; the remaining two bars
  are filled by an instrumental **answer** — guitar, harmonica or piano (**call and response**).
- Phrases start high and fall; they lean on the ♭3 and the root; repetition of short motifs is
  the norm.

## 17.4 Rhythm and grooves

| Groove | Feel | Drums | Bass |
|---|---|---|---|
| **Shuffle** | swung 8ths (triplet long–short) | hi-hat or ride shuffle, backbeat on 2 & 4 | boogie lines, walking |
| **Texas shuffle** | driving shuffle | snare shuffles too, with ghost notes | 1–3–5–6–♭7 boogie |
| **Slow blues (12/8)** | four dotted-quarter beats, each split in three | hi-hat triplets, snare on 2 & 4 | roots and walk-ups in triplets |
| **Straight-8th / rock blues** | even 8ths | rock beat | root 8ths |
| **Boogie** | fast shuffle, one-chord grooves | train beat | ostinato riff |
| **Jump blues** | swing (big-band influence) | swing ride | walking |
| **Stop-time** | band hits beat 1 (and sometimes the "& of 4"), silence between | hits only | hits only |

Stop-time is often used for the first four bars of a verse, so the vocal is exposed
("Hoochie Coochie Man" style), then the band falls back into the groove.

## 17.5 Instruments and their roles

- **Guitar**: rhythm parts based on the **5th–6th shuffle** (root + fifth alternating with
  root + sixth, then ♭7), lead fills between vocal lines; string bends, vibrato, double stops,
  slide.
- **Harmonica**: usually played "cross harp" (second position): a harp a fourth above the song's
  key (blues in A → D harmonica), which gives the ♭7 and bendable blue notes.
- **Piano**: boogie-woogie left-hand ostinatos, triplet chord repetitions in slow blues, fills.
- **Organ**: sustained chords and swells behind the band.
- **Bass**: boogie patterns (1–3–5–6–♭7–6–5–3), shuffle roots, walking lines.
- **Drums**: shuffle on hi-hat or ride, solid backbeat, few fills; the groove is everything.

## 17.6 Substyles

| Style | Features | Players |
|---|---|---|
| Delta | solo acoustic guitar, slide, irregular bar lengths | Robert Johnson, Son House |
| Chicago | electric band, harmonica, shuffle | Muddy Waters, Howlin' Wolf, Little Walter |
| Texas | swinging, jazzy guitar, horns | T-Bone Walker, Freddie King, Stevie Ray Vaughan |
| Jump | big-band swing, saxophones | Louis Jordan |
| Soul blues / modern | horns, polished production | B.B. King, Albert King, Robert Cray |
| Blues rock | loud guitars, straight 8ths, long solos | Cream, Led Zeppelin, Joe Bonamassa, Gary Clark Jr. |

## 17.7 In komposoija

```python
song = Song(title="...", key="A major", tempo=108, style="blues")   # 8ths swung at 0.66
verse = song.section("verse", bars=12, chords=blues.progressions.quick_change, lyrics="...")
verse.play(drums=blues.drums.shuffle, bass=blues.bass.boogie,
           guitar=blues.comp.boogie_shuffle, keys=blues.comp.stabs)
```

| Palette | Contents |
|---|---|
| `blues.drums` | `shuffle texas rock_blues slow_12_8 stop_time` |
| `blues.bass` | `boogie boogie_low shuffle_roots walking slow_12_8 stop_time` |
| `blues.comp` | `boogie_shuffle` (5th–6th rhythm guitar), `stabs triplets_12_8 organ stop_time` |
| `blues.progressions` | `twelve_bar quick_change minor eight_bar jazz turnaround` |

- Shuffle comes from the style's swing setting, so the patterns are written in straight 8ths.
- For a slow 12/8 blues use `Song(meter="12/8", style="blues")` with the `slow_12_8` patterns;
  swing is ignored in compound meters because the triplets are already in the bar.
- The boogie patterns transpose from each chord's root and assume dominant chords.
- Blue notes in a melody: write chord tones and add `.transpose(3)` on chosen notes, as in
  `songs/blues_example.py`.

## Exercises

1. Write three AAB verses and map them onto a 12-bar form with instrumental answers.
2. Turn the quick-change blues into a minor blues; which chords change?
3. Arrange one verse as stop-time for four bars, then back to the shuffle.
