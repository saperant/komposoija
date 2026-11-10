#!/bin/sh
# Run a command where the demo home is /home/me and none of the real home directories are
# visible, except this checkout (and its .venv) and, if set, $MYRCP_GTK_DIR (a myrcp build
# with myrcp-gtk). Needs bubblewrap.  sandbox.sh DEMO_DIR command...
set -e
D=$(realpath "$1"); shift
REPO=$(realpath "$(dirname "$0")/../..")
HOMES=$(realpath /home)
mkdir -p "$D/home" "$D/run"
set -- --dev-bind / / --tmpfs "$HOMES" --bind "$REPO" "$REPO" \
  ${MYRCP_GTK_DIR:+--bind "$(realpath "$MYRCP_GTK_DIR")" "$(realpath "$MYRCP_GTK_DIR")"} \
  --bind "$D/home" "$HOMES/me" --tmpfs /run/user --bind "$D/run" /run/user/me \
  --setenv HOME /home/me --setenv USER me --setenv LOGNAME me --setenv LANG C.UTF-8 --unsetenv LC_ALL --unsetenv LANGUAGE \
  --setenv XDG_CONFIG_HOME /home/me/.config --setenv XDG_STATE_HOME /home/me/.local/state \
  --setenv XDG_RUNTIME_DIR /run/user/me --unsetenv KOMPOSOIJA_SONGS --unsetenv KOMPOSOIJA_PYTHON \
  --setenv MYRCP_GTK_DIR "${MYRCP_GTK_DIR:+$(realpath "$MYRCP_GTK_DIR")}" \
  --setenv PATH "/home/me/bin:$REPO/.venv/bin:/usr/bin:/bin" --setenv KOMPOSOIJA_SOUNDFONT /home/me/bin/demo.sf2 --chdir /home/me/songs "$@"
exec bwrap "$@"
