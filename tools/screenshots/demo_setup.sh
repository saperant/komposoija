#!/bin/sh
# The made-up home of the screenshots: the repository's example songs in ~/songs.
# demo_setup.sh REPO DEMO_DIR (outside the sandbox)
set -e
rm -rf "$2/home"; mkdir -p "$2/home/songs" "$2/run"; chmod 700 "$2/run"
cp "$1"/songs/*.py "$2/home/songs/"
# A silent stand-in for fluidsynth (and a SoundFont for it), so the playhead runs.
mkdir -p "$2/home/bin"
printf '#!/bin/sh\nexec sleep 300\n' > "$2/home/bin/fluidsynth"; chmod +x "$2/home/bin/fluidsynth"
: > "$2/home/bin/demo.sf2"
