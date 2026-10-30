"""Mini-notation parser (a practical subset of Strudel's).

    a b c       sequence: items share one cycle (bar) equally
    [a b]       subsequence in one step
    <a b>       alternate: one item per cycle
    a, b        (inside [] or <>, or at top level) play simultaneously
    ~  -        rest
    a*2  a/2    faster / slower
    a!3  a !    replicate (bare ! repeats the previous step)
    a@3         weight: the step takes 3 units of time (inside <>: lasts 3 cycles)
    a?  a?0.3   drop at random (deterministic)
    a(3,8,2)    Euclidean rhythm: 3 hits over 8 steps, rotated by 2

Atoms are converted by a caller-supplied function, so the same syntax serves
drum names, note names, scale degrees, chord tones and chord symbols. Atoms may
contain letters, digits and `# b ' ^ ° ø Δ + - . : _`, and `/` when followed by
a letter (so `V/V` and `C/E` are atoms while `a/2` is "a, slowed by 2").
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Any, Callable

from .pattern import Pattern, cat, euclid, pure, sequence, silence, stack

Convert = Callable[[str], dict[str, Any]]

_ATOM_CHARS = re.compile(r"[A-Za-z0-9#'^°øΔ+\-.:_]")
_NUMBER = re.compile(r"-?\d+(?:\.\d+)?(?:/\d+)?")


class MiniNotationError(ValueError):
    def __init__(self, message: str, text: str, pos: int):
        pointer = " " * pos + "^"
        super().__init__(f"{message}\n  {text}\n  {pointer}")
        self.pos = pos


class _Parser:
    def __init__(self, text: str, convert: Convert):
        self.text = text
        self.convert = convert
        self.pos = 0
        self.atom_index = 0

    # ---------- helpers ----------

    def error(self, message: str, pos: int | None = None) -> MiniNotationError:
        return MiniNotationError(message, self.text, self.pos if pos is None else pos)

    def skip_ws(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def peek(self) -> str:
        self.skip_ws()
        return self.text[self.pos] if self.pos < len(self.text) else ""

    def expect(self, ch: str) -> None:
        if self.peek() != ch:
            raise self.error(f"expected {ch!r}")
        self.pos += 1

    def number(self) -> Fraction:
        self.skip_ws()
        m = _NUMBER.match(self.text, self.pos)
        if not m:
            raise self.error("expected a number")
        self.pos = m.end()
        return Fraction(m.group(0))

    # ---------- grammar ----------

    def parse(self) -> Pattern:
        pat = self.stack_of_sequences(closing="")
        if self.peek():
            raise self.error(f"unexpected {self.peek()!r}")
        return pat

    def stack_of_sequences(self, closing: str, alternate: bool = False) -> Pattern:
        layers = [self.steps(closing)]
        while self.peek() == ",":
            self.pos += 1
            layers.append(self.steps(closing))
        pats = [_alternating(steps, self) if alternate else _weighted(steps) for steps in layers]
        return pats[0] if len(pats) == 1 else stack(*pats)

    def steps(self, closing: str) -> list[tuple[Pattern, Fraction]]:
        steps: list[tuple[Pattern, Fraction]] = []
        while True:
            ch = self.peek()
            if ch == "" or ch == closing or ch == ",":
                break
            if ch == "!":  # bare "!" repeats the previous step
                if not steps:
                    raise self.error("'!' needs a step before it")
                self.pos += 1
                steps.append(steps[-1])
                continue
            steps.extend(self.step())
        if not steps and closing:
            raise self.error("empty group")
        return steps

    def step(self) -> list[tuple[Pattern, Fraction]]:
        pat = self.term()
        weight, copies = Fraction(1), 1
        while True:
            ch = self.text[self.pos] if self.pos < len(self.text) else ""
            if ch == "*":
                self.pos += 1
                pat = pat.fast(self.number())
            elif ch == "/":
                self.pos += 1
                pat = pat.slow(self.number())
            elif ch == "@":
                self.pos += 1
                weight = self.number()
            elif ch == "!" and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit():
                self.pos += 1
                copies = int(self.number())
            elif ch == "?":
                self.pos += 1
                prob = 0.5
                if self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == "."):
                    prob = float(self.number())
                pat = pat.degrade(prob, seed=self.pos)
            elif ch == "(":
                self.pos += 1
                k = int(self.number())
                self.expect(",")
                n = int(self.number())
                rot = 0
                if self.peek() == ",":
                    self.pos += 1
                    rot = int(self.number())
                self.expect(")")
                pat = euclid(pat, k, n, rot)
            else:
                break
        return [(pat, weight)] * copies

    def term(self) -> Pattern:
        ch = self.peek()
        if ch == "[":
            self.pos += 1
            pat = self.stack_of_sequences(closing="]")
            self.expect("]")
            return pat
        if ch == "<":
            self.pos += 1
            pat = self.stack_of_sequences(closing=">", alternate=True)
            self.expect(">")
            return pat
        if ch in ("~",):
            self.pos += 1
            return silence
        return self.atom()

    def atom(self) -> Pattern:
        start = self.pos
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if _ATOM_CHARS.match(ch):
                self.pos += 1
            elif ch == "/" and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isalpha():
                self.pos += 1  # "V/V", "C/E": a slash followed by a letter is part of the atom
            else:
                break
        token = self.text[start:self.pos]
        if not token:
            raise self.error(f"unexpected {self.text[self.pos]!r}" if self.pos < len(self.text) else "unexpected end")
        if token == "-":
            return silence
        try:
            value = self.convert(token)
        except ValueError as exc:
            raise self.error(str(exc), start) from None
        return pure(value)


def _weighted(steps: list[tuple[Pattern, Fraction]]) -> Pattern:
    if len(steps) == 1 and steps[0][1] == 1:
        return steps[0][0]
    return sequence(*[p for p, _ in steps], weights=[w for _, w in steps])


def _alternating(steps: list[tuple[Pattern, Fraction]], parser: _Parser) -> Pattern:
    """`<a@3 b>`: in an alternation a weight is a number of cycles."""
    items = []
    for p, w in steps:
        if w.denominator != 1 or w < 1:
            raise parser.error(f"weights inside <...> must be whole cycles, got @{w}")
        items.extend([p] * int(w))
    return cat(*items)


def mini(text: str, convert: Convert) -> Pattern:
    """Parse mini-notation, converting each atom with `convert` (which may raise ValueError)."""
    return _Parser(text, convert).parse()
