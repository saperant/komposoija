# komposoija

Interactive, AI-assisted song composition. Songs are written as code (Strudel-style
mini-notation in Python) and rendered to MIDI for band scores and SoundFont playback.

- `src/komposoija/` — pattern engine (`pattern.py`, `mini.py`), music theory (`theory.py`),
  song model (`song.py`), MIDI rendering (`render.py`), pop-rock presets (`presets.py`),
  genre palettes (`genres.py`: jazz, blues, funk, reggae, metal), style profiles (`styles.py`), CLI.
- `songs/` — song files; `songs/example.py` shows the full flow, `songs/<genre>_example.py`
  one per genre palette.
- `docs/` — music theory study material (chapters 01–15) and `docs/song-dsl.md` (DSL reference).
  Keep `docs/song-dsl.md`, `README.md` and docs/15 section 15.8 in sync with code changes.
- `myrcp/` — the user interface on the myrcp workbench: `product.toml` and the plugin
  `plugins/komposoija` (`myrcp.toml` declares its views and commands); started by
  `scripts/komposoija-ui` (or `myrcp --product myrcp`). It reads songs through
  `komposoija inspect`, so keep that JSON stable or update the plugin with it.
- `tests/` — pytest suite (`test_myrcp_plugin.py` drives the plugin over myrcp's protocol).

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'   # once
.venv/bin/pytest -q
.venv/bin/komposoija render songs/<name>.py      # -> build/<name>.mid + summary
.venv/bin/komposoija show songs/<name>.py
.venv/bin/komposoija render songs/<name>.py --wav    # + build/<name>.wav (FluidSynth, FluidR3_GM)
.venv/bin/komposoija render songs/<name>.py --mp3    # + build/<name>.mp3 (lame)
.venv/bin/komposoija render songs/<name>.py --watch --play   # user's live-coding loop
.venv/bin/komposoija render songs/<name>.py --play --from chorus.2:5   # play from a place
.venv/bin/komposoija inspect songs/<name>.py     # timeline + line->section map as JSON (myrcp companion)
scripts/build-docs-pdf.sh                        # docs -> build/music-theory.pdf
```

## Composing with the user (agent + human workflow)

When the user brings lyrics or a song idea, work in the stages below. Each stage is a
block in the song file, so the user can review and edit it directly. Confirm each stage
with the user before going deep into the next; offer 2-3 concrete options rather than
open questions.

1. **Structure** — read the lyrics and propose sections: repeated lines and the title
   phrase usually mark the chorus; narrative stanzas are verses; a stanza with a new
   perspective is the bridge; short lifting lines before the chorus are a pre-chorus.
   Choose bar counts from the syllables per line (a 4-line stanza usually = 8 bars).
   Put each section's lyrics in `lyrics=`, then `song.arrange(...)`.
2. **Mood** — style profile (`Song(style=...)`), key (consider vocal range), tempo,
   feel/swing, mode, a progression per section and presets for drums/bass/comp, following
   docs 05–08, 10, 13, 14 and the genre chapters 16–20 (jazz, blues, funk, reggae, metal).
   Contrast verse and chorus (start chord, harmonic rhythm, groove energy). Per-section
   `key=` (absolute or `"+1"`), `tempo=`, `tempo_to=` (rit./accel.) and `meter=` give
   modulations, tempo and time-signature changes; section names must not contain spaces.
3. **Details** — fills at section ends, variants for repeats (`like=`), riffs/hooks,
   velocities, extra tracks.

After every edit, run `komposoija render` and check the printed summary (chords per
bar, tracks per section, length). Musical choices should be explainable with the docs;
mention the reasoning briefly ("bVII in the bridge for a Mixolydian lift").

## Conventions

- One pattern cycle = one bar. Roman numerals count from the major scale of the tonic.
- Keep song files readable: stage comments, one `play()` per section, presets first.
- New presets go in `presets.py` with a test if they contain logic.
