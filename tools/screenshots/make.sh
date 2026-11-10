#!/bin/sh
# The README's screenshots (docs/screenshots), from a made-up home in a sandbox with the
# example songs and a silent stand-in for fluidsynth:
#   tools/screenshots/make.sh [MYRCP_BUILD_DIR]
# The terminal ones need pyte and vim; the GTK ones a myrcp build with myrcp-gtk
# (cmake -DMYRCP_GTK=ON) given as the argument, Xvfb, xdotool and ImageMagick.
set -e
HERE=$(cd "$(dirname "$0")" && pwd); REPO=$(dirname "$(dirname "$HERE")")
OUT=$REPO/docs/screenshots; WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
mkdir -p "$OUT"
run() { "$HERE/sandbox.sh" "$WORK/demo" env MYRCP_EDITOR_MODE=tab VISUAL=vim "$@"; }
PERSPECTIVE='key:\x10' ; P2='key:perspective komposoija\r'

"$HERE/demo_setup.sh" "$REPO" "$WORK/demo"
run python "$HERE/rcp_shots.py" "$WORK" wait:Saved "$PERSPECTIVE" "$P2" wait:Properties \
  'key:\x1b[B' sleep:1 "shot:rcp-songs:komposoija-ui — the myrcp workbench" \
  'key:\r' wait:chorus.4 'key:\x1b[B\x1b[B\x1b[B' 'key:\r' sleep:3.5 \
  "shot:rcp-playing:komposoija-ui — Paper Lanterns"
"$HERE/demo_setup.sh" "$REPO" "$WORK/demo"
run python "$HERE/rcp_shots.py" "$WORK" wait:Saved "$PERSPECTIVE" "$P2" wait:Properties \
  'key:\x1b[B' 'key:\r' wait:chorus.4 key:e wait:STRUCTURE 'key::52s/ vi>/ xi>/\r' 'key::w\r' \
  wait:MiniNotationError "shot:rcp-error:komposoija-ui — a render error after a save"
cp "$WORK"/rcp-*.svg "$OUT/"
if [ -n "$1" ]; then
  "$HERE/demo_setup.sh" "$REPO" "$WORK/demo"
  MYRCP_GTK_DIR=$1 run python "$HERE/gtk_shots.py" "$WORK" \
    "key:ctrl+p" "sleep:0.5" "type:perspective komposoija" "sleep:0.6" "key:Return" "sleep:1.5" \
    "click:200,193" "sleep:1" "shot:gtk-songs" \
    "key:Return" "sleep:3" "click:200,235" "key:Return" "sleep:3.5" "shot:gtk-playing" \
    "key:space" "key:e" "sleep:3" "type::52s/ vi>/ xi>/" "key:Return" "type::w" "key:Return" \
    "sleep:3" "shot:gtk-error"
  for f in "$WORK"/gtk-*.png; do convert "$f" -strip -colors 256 "PNG8:$OUT/$(basename "$f")"; done
fi
ls -l "$OUT"
