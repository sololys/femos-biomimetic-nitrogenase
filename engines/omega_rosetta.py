#!/usr/bin/env python3
"""
Ω-ROSETTA
31 autonomous systems / 310 semantic bodies.

Stop with Ctrl-C.
"""

from __future__ import annotations

import hashlib
import sys
import time


DOORS = 31

PLANETS = (
    ("☉", 220),  # K_d      / Sun
    ("·", 245),  # Residual / Mercury
    ("◇", 213),  # Estimate / Venus
    ("⊕", 45),   # Commit   / Earth
    ("♂", 203),  # HOLD     / Mars
    ("♃", 214),  # Govern   / Jupiter
    ("◎", 229),  # Witness  / Saturn
    ("⟐", 117),  # Rosetta  / Uranus
    ("≋", 39),   # IDC      / Neptune
)

LINKS = (
    "─",
    "┄",
    "╍",
    "⇄",
    "→",
    "←",
    "↝",
    "∿",
)

SPINE = "ROSETTA│ΣΩΓW│↯⊘"
RESET = "\x1b[0m"
HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
CLEAR = "\x1b[2J\x1b[H"


def color(code: int, value: str) -> str:
    return f"\x1b[38;5;{code}m{value}{RESET}"


def digest(*parts: object, size: int = 16) -> bytes:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    return hashlib.blake2s(payload, digest_size=size).digest()


def reverse_link(link: str) -> str:
    return {
        "→": "←",
        "←": "→",
        "↝": "↜",
        "↜": "↝",
    }.get(link, link)


def candidate_orbit(door: int, index: int, tick: int) -> str:
    """Generate a RAW orbital candidate."""
    phase = (
        door * 31
        + index * 17
        + tick * 13
        + (tick * tick + door * index * 5)
    )

    raw = digest("RAW", door, index, tick, phase)
    return LINKS[raw[0] % len(LINKS)]


def admissible_orbit(
    door: int,
    index: int,
    tick: int,
    candidate: str,
) -> str:
    """Project a candidate through the local structural gate."""
    test = digest("OMEGA", door, index, tick, candidate)

    kernel_value = (
        test[0]
        + 3 * test[1]
        + door
        + index
        + tick
    ) % 17

    if kernel_value in {0, 1}:
        return "×"

    return candidate


def local_system(
    door: int,
    tick: int,
    reverse: bool = False,
) -> tuple[str, int]:
    links: list[str] = []

    for index in range(9):
        raw = candidate_orbit(door, index, tick)
        links.append(admissible_orbit(door, index, tick, raw))

    admitted = sum(link != "×" for link in links)
    gate_state = "+" if admitted >= 6 else "~"
    gate_color = 82 if gate_state == "+" else 196

    bodies = list(PLANETS)
    bodies.append((f"⟦Ω{gate_state}⟧", gate_color))

    if reverse:
        bodies.reverse()
        links = [reverse_link(link) for link in reversed(links)]

    output: list[str] = []

    for index, (glyph, glyph_color) in enumerate(bodies):
        output.append(color(glyph_color, glyph))

        if index < len(links):
            link_color = 240 if links[index] == "×" else 244
            output.append(color(link_color, links[index]))

    return "".join(output), admitted


def next_witness(
    previous: bytes,
    door: int,
    tick: int,
    admitted: int,
    local_state: str,
) -> bytes:
    """Advance the door-local append-only witness digest."""
    payload = (
        previous
        + door.to_bytes(2, "big")
        + tick.to_bytes(8, "big")
        + admitted.to_bytes(1, "big")
        + local_state.encode("utf-8")
    )

    return hashlib.blake2s(payload, digest_size=8).digest()


def render(tick: int, witnesses: list[bytes]) -> str:
    systems: dict[int, str] = {}
    scores: dict[int, int] = {}

    for door in range(1, DOORS + 1):
        reverse = 16 <= door <= 30
        systems[door], scores[door] = local_system(
            door,
            tick,
            reverse=reverse,
        )

        witnesses[door] = next_witness(
            witnesses[door],
            door,
            tick,
            scores[door],
            systems[door],
        )

    lines = [
        color(
            250,
            "╔══════════ Ω-ROSETTA / "
            f"31×10 / WITNESS t={tick:09d} "
            "══════════╗",
        )
    ]

    for row, left_door in enumerate(range(1, 16)):
        right_door = 31 - left_door
        spine_symbol = SPINE[(row + tick // 5) % len(SPINE)]

        left_witness = witnesses[left_door].hex()[:4].upper()
        right_witness = witnesses[right_door].hex()[:4].upper()

        line = (
            color(244, f"W{left_door:02}:{left_witness} ")
            + color(250, f"D{left_door:02} ")
            + systems[left_door]
            + color(238, " ═╡ ")
            + color(51, spine_symbol)
            + color(238, " ╞═ ")
            + systems[right_door]
            + color(250, f" D{right_door:02}")
            + color(244, f" W{right_door:02}:{right_witness}")
        )

        lines.append(line)

    witness_31 = witnesses[31].hex()[:8].upper()

    lines.extend(
        [
            color(238, "                                      │"),
            (
                color(244, f"                W31:{witness_31} ")
                + color(250, "D31 ")
                + systems[31]
                + color(238, " ═╡ ")
                + color(51, "31")
                + color(238, " ╞═ ")
                + color(244, f"t:{tick}")
            ),
            color(238, "                                      ▼"),
            color(240, "                           CONTINUES OUTSIDE FRAME"),
        ]
    )

    return "\n".join(lines)


def main() -> int:
    witnesses = [b"\x00" * 8 for _ in range(DOORS + 1)]
    tick = 0
    once = "--once" in sys.argv

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    try:
        while True:
            frame = render(tick, witnesses)
            sys.stdout.write(CLEAR + frame + "\n")
            sys.stdout.flush()

            if once:
                break

            tick += 1
            time.sleep(0.11)

    except KeyboardInterrupt:
        pass

    finally:
        sys.stdout.write(RESET + SHOW_CURSOR + "\n")
        sys.stdout.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
