"""Screenshots of komposoija-ui in the terminal workbench (run inside sandbox.sh):
rcp_shots.py OUT_DIR STEP..., a step being "key:<text with \\x escapes>", "wait:<text on
screen>", "sleep:<seconds>" or "shot:<name>:<window title>" (an SVG in OUT_DIR)."""
import fcntl, os, pty, struct, subprocess, sys, termios, threading, time
from pathlib import Path

import pyte

sys.path.insert(0, os.path.dirname(__file__))
from term_svg import render  # noqa: E402

(Path.home() / ".local/state/komposoija/workbench.state").unlink(missing_ok=True)
OUT = Path(sys.argv[1]); COLS, ROWS = 160, 38
env = dict(os.environ, TERM="xterm-256color", MYRCP_PLUGIN_PATH="")
master, slave = pty.openpty()
fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLS, 0, 0))
proc = subprocess.Popen(["komposoija-ui"], stdin=slave, stdout=slave, stderr=slave, env=env,
                        start_new_session=True)
os.close(slave)
buf = bytearray(); lock = threading.Lock()


def reader():
    while True:
        try:
            d = os.read(master, 65536)
        except OSError:
            return
        if not d:
            return
        with lock:
            buf.extend(d)


threading.Thread(target=reader, daemon=True).start()


def screen():
    s = pyte.Screen(COLS, ROWS)
    with lock:
        pyte.ByteStream(s).feed(bytes(buf))
    return s


def wait(needle, timeout=30):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if needle in "\n".join(screen().display):
            return
        time.sleep(0.1)
    raise TimeoutError(needle + "\n" + "\n".join(screen().display))


try:
    for step in sys.argv[2:]:
        kind, _, arg = step.partition(":")
        if kind == "key":
            os.write(master, arg.encode().decode("unicode_escape").encode())
            time.sleep(0.5)
        elif kind == "wait":
            wait(arg)
        elif kind == "sleep":
            time.sleep(float(arg))
        elif kind == "shot":
            name, _, title = arg.partition(":")
            time.sleep(0.8)
            (OUT / f"{name}.svg").write_text(render(screen(), title))
finally:
    proc.kill()
