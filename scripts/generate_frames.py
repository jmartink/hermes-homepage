#!/usr/bin/env python3
"""
Generate ASCII animation frames for the Franc homepage.
Three phases:
  1. Ship sailing with animated waves + twinkling stars (loops)
  2. Ship-to-rocket morph transition (scramble effect)
  3. Rocket with animated exhaust (loops)

Uses only basic ASCII for max font compatibility.
Output: assets/frames.json
"""

import json
import random
import math
import os

random.seed(42)

WIDTH = 62
HEIGHT = 30

# ============================================================
# THE SHIP — Galleon between symbolic pillars (Novum Organum)
# Plain ASCII only — no Unicode line-drawing
# ============================================================
SHIP_RAW = r"""
        .            *                .            *
    *          .           .                .            .   *
                     .          *                    .
  |                                                        |
  |                          .                             |
  |                         /|\                            |
  |                        / | \                           |
  |                       /  |  \                          |
  |                    __/   |   \__                       |
  |                   /  /   |   \  \                      |
  |                  /  /    |    \  \                     |
  |                 /  / FRANC|    \  \                    |
  |                /__/______|______\__\                   |
  |                |                   |                   |
  |                | .  F R A N C  . . |                   |
  |                |  . . . . . . . .  |                   |
  |                |___________________|                   |
  |                 \                 /                    |
  |           ~~~~~~~~~~~~~~~~~~~~~~~~~~                   |
  |        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~              |
  |      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~            |
  |    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~          |
  |   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~         |
  |  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~        |
  | ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~       |
  |                                                        |
  |  multi pertransibunt et augebitur scientia             |
  |                                                        |
  |--------------------------------------------------------|
""".strip('\n').split('\n')

# ============================================================
# THE ROCKET
# ============================================================
ROCKET_RAW = r"""
        *            .                *            .
    .          *           *                *            *   .
                     *          .                    *
  |                                                        |
  |                         /\                             |
  |                        /  \                            |
  |                       / /\ \                           |
  |                      / /  \ \                          |
  |                     / / () \ \                         |
  |                    | |      | |                        |
  |                    | | FRNC | |                        |
  |                    | |      | |                        |
  |                    | |______| |                        |
  |                   /| |::::::| |\                       |
  |                  /_|_|______|_|_\                      |
  |                 |  |  FRANC |  |                       |
  |                 |__|________|__|                       |
  |                /  / |      | \  \                      |
  |               /__/  |      |  \__\                     |
  |                   .^|^^^^^^|^.                          |
  |                 .^^^|^^^^^^|^^^.                        |
  |               .^^^^^|^^^^^^|^^^^^.                     |
  |             .^^^^^^^|^^^^^^|^^^^^^^.                   |
  |            ^^^^^^^^^^^^^^^^^^^^^^^^^^                  |
  |           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^                 |
  |                                                        |
  |  ad astra per curiositatem                             |
  |                                                        |
  |--------------------------------------------------------|
""".strip('\n').split('\n')


def pad_lines(raw_lines, width=WIDTH, height=HEIGHT):
    """Ensure every line is exactly WIDTH chars, total HEIGHT lines."""
    result = []
    for line in raw_lines[:height]:
        if len(line) < width:
            line = line + ' ' * (width - len(line))
        elif len(line) > width:
            line = line[:width]
        result.append(line)
    while len(result) < height:
        result.append(' ' * width)
    return result


def make_star_positions(width=WIDTH, height=4, density=0.006, seed=42):
    rng = random.Random(seed)
    return [(x, y) for y in range(height) for x in range(width) if rng.random() < density]


STARS = make_star_positions()


def twinkle_stars(lines, frame_num):
    """Subtle star twinkling in the sky rows."""
    result = [list(line) for line in lines]
    chars = '..*+. *.'
    for x, y in STARS:
        if y < len(result) and x < len(result[y]) and result[y][x] == ' ':
            phase = (frame_num * 3 + x * 7 + y * 13) % 12
            if phase < 5:
                result[y][x] = chars[phase % len(chars)]
    return [''.join(r) for r in result]


def animate_waves(lines, frame_num):
    """Shift wave pattern each frame."""
    result = list(lines)
    wave = '~-~=~-~='
    for i, line in enumerate(lines):
        if '~' not in line:
            continue
        cs = list(line)
        ws = we = None
        for j, c in enumerate(cs):
            if c == '~':
                if ws is None: ws = j
                we = j
        if ws is not None:
            off = (frame_num * 2 + i * 3) % len(wave)
            for j in range(we - ws + 1):
                cs[ws + j] = wave[(j + off) % len(wave)]
            result[i] = ''.join(cs)
    return result


def animate_exhaust(lines, frame_num):
    """Flicker rocket exhaust."""
    result = list(lines)
    flames = ['^*o.^*o.', '*o.^^*o.', 'o.^*^o.*', '.^*o.*^o']
    fset = flames[frame_num % len(flames)]
    for i, line in enumerate(lines):
        if '^' not in line:
            continue
        cs = list(line)
        for j, c in enumerate(cs):
            if c == '^':
                cs[j] = fset[(j * 3 + i * 5 + frame_num * 7) % len(fset)]
        result[i] = ''.join(cs)
    return result


def generate_ship_frames(n=36):
    base = pad_lines(SHIP_RAW)
    return [twinkle_stars(animate_waves(base, f), f) for f in range(n)]


def generate_rocket_frames(n=36):
    base = pad_lines(ROCKET_RAW)
    return [twinkle_stars(animate_exhaust(base, f), f + 81) for f in range(n)]


def generate_morph_frames(n=45):
    ship = pad_lines(SHIP_RAW)
    rocket = pad_lines(ROCKET_RAW)
    scramble = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789#$%&*+~='
    cx, cy = WIDTH // 2, HEIGHT // 2
    md = math.sqrt(cx**2 + cy**2)
    rng = random.Random(123)
    reveal = [[((math.sqrt((x-cx)**2+((y-cy)*2)**2)/md)*0.5 + rng.random()*0.5) for x in range(WIDTH)] for y in range(HEIGHT)]

    frames = []
    for f in range(n):
        p = f / (n - 1)
        lines = []
        for y in range(HEIGHT):
            row = []
            for x in range(WIDTH):
                s = ship[y][x] if y < len(ship) and x < len(ship[y]) else ' '
                r = rocket[y][x] if y < len(rocket) and x < len(rocket[y]) else ' '
                t = reveal[y][x]
                if p < t * 0.6:
                    row.append(s)
                elif p > t * 0.6 + 0.32:
                    row.append(r)
                elif s == ' ' and r == ' ':
                    row.append(' ')
                elif rng.random() < 0.5:
                    row.append(rng.choice(scramble))
                else:
                    row.append(r if p > 0.5 else s)
            lines.append(''.join(row))
        frames.append(twinkle_stars(lines, f + 36))
    return frames


def main():
    print('Generating frames...')
    ship = generate_ship_frames(36)
    morph = generate_morph_frames(45)
    rocket = generate_rocket_frames(36)

    data = {
        'ship': ship,
        'morph': morph,
        'rocket': rocket,
        'meta': {'width': WIDTH, 'height': HEIGHT, 'fps': 8,
                 'ship_count': len(ship), 'morph_count': len(morph), 'rocket_count': len(rocket)}
    }

    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'frames.json')
    with open(out, 'w') as f:
        json.dump(data, f, separators=(',', ':'))

    kb = os.path.getsize(out) / 1024
    print(f'Frames: {len(ship)}+{len(morph)}+{len(rocket)} = {len(ship)+len(morph)+len(rocket)} total')
    print(f'Output: {out} ({kb:.1f} KB)')

    print('\n=== SHIP 0 ===')
    for l in ship[0]: print(l)
    print('\n=== ROCKET 0 ===')
    for l in rocket[0]: print(l)
    print(f'\n=== MORPH {len(morph)//2} ===')
    for l in morph[len(morph)//2]: print(l)


if __name__ == '__main__':
    main()
