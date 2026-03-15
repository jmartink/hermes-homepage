#!/usr/bin/env python3
"""
Franc — ASCII art intro video
Renders a 20-second MP4 with CRT terminal aesthetic.

Scenes:
  0-3s   Title 'FRANC' fades in
  3-8s   Galleon builds line by line with animated waves
  8-10s  Latin motto types out
  10-12s Matrix rain overlay
  12-16s Galleon morphs to rocket
  16-18s New motto types
  18-20s Fade to stars
"""

import os, sys, subprocess, random, math, time
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# === CONFIG ===
W, H = 1920, 1080
FPS = 24
DURATION = 20
TOTAL_FRAMES = FPS * DURATION

BG = (10, 10, 10)
GREEN = (0, 255, 65)
GREEN_DIM = (0, 179, 60)
AMBER = (255, 176, 0)
WHITE = (200, 220, 200)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, 'assets')
OUT = os.path.join(ASSETS, 'franc_intro.mp4')

# === FONT ===
def find_mono_font(size=16):
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf',
        '/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf',
        '/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf',
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    # fallback
    return ImageFont.load_default()

font_small = find_mono_font(14)
font_med = find_mono_font(18)
font_large = find_mono_font(28)

# Measure character cell
def cell_size(font):
    bbox = font.getbbox('M')
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

cw_s, ch_s = cell_size(font_small)
cw_m, ch_m = cell_size(font_med)
cw_l, ch_l = cell_size(font_large)

# === LOAD ASCII ART ===
def load_art(name):
    with open(os.path.join(ASSETS, name)) as f:
        return f.read().split('\n')

galleon_lines = load_art('galleon.txt')
rocket_lines = load_art('rocket.txt')
title_lines = load_art('title_banner.txt')

MOTTO_LATIN = "Multi pertransibunt et augebitur scientia"
MOTTO_ENGLISH = "Many will pass through and knowledge will be increased."
MOTTO_STARS = "Ad astra per curiositatem"
MOTTO_STARS_EN = "To the stars through curiosity."

# === MATRIX RAIN STATE ===
KATAKANA = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓ"
LATIN = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
MATRIX_CHARS = KATAKANA + LATIN

n_cols = W // (cw_s + 2)
rain_y = [random.randint(-H, 0) for _ in range(n_cols)]
rain_speed = [random.randint(4, 14) for _ in range(n_cols)]
rain_chars = [[random.choice(MATRIX_CHARS) for _ in range(H // ch_s + 2)] for _ in range(n_cols)]

# === SCANLINES ===
scanline_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(scanline_img)
for y in range(0, H, 3):
    sd.line([(0, y), (W, y)], fill=(0, 0, 0, 30))

# === VIGNETTE ===
vignette = np.zeros((H, W), dtype=np.float32)
cy, cx = H / 2, W / 2
for y in range(H):
    for x in range(0, W, 4):  # skip pixels for speed
        dist = math.sqrt((x - cx)**2 / (cx**2) + (y - cy)**2 / (cy**2))
        v = max(0, min(1, 1.0 - 0.35 * dist**2))
        vignette[y, x:x+4] = v

# === RENDER HELPERS ===
def draw_text_centered(draw, y, text, font, color, alpha=1.0):
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    if alpha < 1.0:
        c = tuple(int(v * alpha) for v in color)
    else:
        c = color
    draw.text((x, y), text, fill=c, font=font)

def draw_ascii_block(draw, lines, font, cw, ch, color, start_y=None, max_lines=None, alpha=1.0):
    """Draw ASCII art centered on screen."""
    if max_lines is not None:
        lines = lines[:max_lines]
    if not lines:
        return
    block_h = len(lines) * ch
    block_w = max(len(l) for l in lines) * cw
    x0 = (W - block_w) // 2
    if start_y is None:
        y0 = (H - block_h) // 2
    else:
        y0 = start_y
    c = tuple(int(v * alpha) for v in color) if alpha < 1.0 else color
    for i, line in enumerate(lines):
        draw.text((x0, y0 + i * ch), line, fill=c, font=font)

def draw_matrix_rain(draw, t, opacity=0.15):
    """Draw matrix rain columns."""
    for col in range(n_cols):
        rain_y[col] += rain_speed[col]
        if rain_y[col] > H + 200:
            rain_y[col] = random.randint(-400, -50)
            rain_speed[col] = random.randint(4, 14)
        x = col * (cw_s + 2) + 4
        base_y = int(rain_y[col])
        trail_len = 12
        for j in range(trail_len):
            cy = base_y - j * ch_s
            if 0 <= cy < H:
                fade = 1.0 - (j / trail_len)
                brightness = fade * opacity
                g = int(255 * brightness)
                c = (0, g, int(g * 0.25))
                if j == 0:
                    c = (int(180 * opacity), int(255 * opacity), int(180 * opacity))
                char = random.choice(MATRIX_CHARS) if random.random() > 0.7 else rain_chars[col][j % len(rain_chars[col])]
                draw.text((x, cy), char, fill=c, font=font_small)

def apply_post(img):
    """Apply scanlines and vignette."""
    # Scanlines
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, scanline_img)
    img = img.convert('RGB')
    # Vignette (fast)
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] *= vignette
    arr[:, :, 1] *= vignette
    arr[:, :, 2] *= vignette
    return Image.fromarray(arr.astype(np.uint8))

def morph_char(from_c, to_c, progress):
    """Return character during morph transition."""
    if progress < 0.3:
        return from_c if random.random() > progress * 2 else random.choice(MATRIX_CHARS)
    elif progress < 0.7:
        return random.choice(MATRIX_CHARS)
    else:
        return to_c if random.random() < (progress - 0.5) * 2 else random.choice(MATRIX_CHARS)

def draw_morphing_art(draw, from_lines, to_lines, font, cw, ch, color, progress, start_y=None):
    """Draw ASCII art morphing between two scenes."""
    lines = from_lines
    n = max(len(from_lines), len(to_lines))
    block_w = max(max(len(l) for l in from_lines), max(len(l) for l in to_lines)) * cw
    x0 = (W - block_w) // 2
    block_h = n * ch
    y0 = start_y if start_y else (H - block_h) // 2

    for i in range(n):
        fl = from_lines[i] if i < len(from_lines) else ''
        tl = to_lines[i] if i < len(to_lines) else ''
        max_len = max(len(fl), len(tl))
        fl = fl.ljust(max_len)
        tl = tl.ljust(max_len)
        for j, (fc, tc) in enumerate(zip(fl, tl)):
            if fc == ' ' and tc == ' ':
                continue
            char = morph_char(fc, tc, progress)
            if char == ' ':
                continue
            # Color shift during morph
            if progress < 0.5:
                c = GREEN
            else:
                c = (int(GREEN[0] * 0.6 + 100 * 0.4),
                     int(GREEN[1] * 0.6 + 220 * 0.4),
                     int(GREEN[2] * 0.6 + 200 * 0.4))
            draw.text((x0 + j * cw, y0 + i * ch), char, fill=c, font=font)

# === MAIN RENDER ===
def render_frame(frame_idx):
    t = frame_idx / FPS  # time in seconds
    img = Image.new('RGB', (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene timing
    art_y = 120  # top of ASCII art area
    motto_y = art_y + len(galleon_lines) * ch_m + 20

    # --- SCENE 1: Title fade in (0-3s) ---
    if t < 3.0:
        alpha = min(1.0, t / 1.5)
        # Subtle matrix rain in background
        draw_matrix_rain(draw, t, opacity=0.06)
        draw_ascii_block(draw, title_lines, font_large, cw_l, ch_l, GREEN, start_y=H//2 - len(title_lines)*ch_l//2, alpha=alpha)
        # Subtitle
        if t > 1.5:
            sub_alpha = min(1.0, (t - 1.5) / 1.0)
            draw_text_centered(draw, H//2 + len(title_lines)*ch_l//2 + 30,
                             "Into Open Waters", font_med, AMBER, alpha=sub_alpha)

    # --- SCENE 2: Galleon builds (3-8s) ---
    elif t < 8.0:
        scene_t = t - 3.0
        draw_matrix_rain(draw, t, opacity=0.08)

        # Build line by line (bottom to top)
        total_lines = len(galleon_lines)
        lines_to_show = min(total_lines, int((scene_t / 4.0) * total_lines) + 1)

        # Show from bottom up
        visible = galleon_lines[total_lines - lines_to_show:]
        y_offset = art_y + (total_lines - lines_to_show) * ch_m
        draw_ascii_block(draw, visible, font_med, cw_m, ch_m, GREEN, start_y=y_offset)

        # Animate waves on visible water lines (shimmer)
        if scene_t > 1.0:
            # slight color variation on wave chars
            pass

    # --- SCENE 3: Motto types (8-10s) ---
    elif t < 10.0:
        scene_t = t - 8.0
        draw_matrix_rain(draw, t, opacity=0.08)
        draw_ascii_block(draw, galleon_lines, font_med, cw_m, ch_m, GREEN, start_y=art_y)

        # Type Latin motto
        chars_shown = int((scene_t / 1.2) * len(MOTTO_LATIN))
        typed = MOTTO_LATIN[:min(chars_shown, len(MOTTO_LATIN))]
        draw_text_centered(draw, motto_y, typed, font_med, AMBER)

        # English translation after Latin is done
        if scene_t > 1.3:
            eng_t = scene_t - 1.3
            eng_chars = int((eng_t / 0.6) * len(MOTTO_ENGLISH))
            eng_typed = MOTTO_ENGLISH[:min(eng_chars, len(MOTTO_ENGLISH))]
            draw_text_centered(draw, motto_y + ch_m + 10, eng_typed, font_small, GREEN_DIM)

    # --- SCENE 4: Matrix rain burst (10-12s) ---
    elif t < 12.0:
        scene_t = t - 10.0
        intensity = 0.08 + 0.25 * math.sin(scene_t * math.pi / 2.0)
        draw_matrix_rain(draw, t, opacity=intensity)
        draw_ascii_block(draw, galleon_lines, font_med, cw_m, ch_m, GREEN, start_y=art_y)
        draw_text_centered(draw, motto_y, MOTTO_LATIN, font_med, AMBER)
        draw_text_centered(draw, motto_y + ch_m + 10, MOTTO_ENGLISH, font_small, GREEN_DIM)

    # --- SCENE 5: Morph galleon → rocket (12-16s) ---
    elif t < 16.0:
        scene_t = t - 12.0
        progress = scene_t / 4.0
        draw_matrix_rain(draw, t, opacity=0.10)
        draw_morphing_art(draw, galleon_lines, rocket_lines, font_med, cw_m, ch_m, GREEN, progress, start_y=art_y)

        # Flash at start of morph
        if scene_t < 0.3:
            flash_alpha = int(200 * (1.0 - scene_t / 0.3))
            overlay = Image.new('RGB', (W, H), (flash_alpha, flash_alpha, flash_alpha // 2))
            img = Image.blend(img, overlay, 0.3 * (1.0 - scene_t / 0.3))
            draw = ImageDraw.Draw(img)

    # --- SCENE 6: New motto (16-18s) ---
    elif t < 18.0:
        scene_t = t - 16.0
        draw_matrix_rain(draw, t, opacity=0.08)
        draw_ascii_block(draw, rocket_lines, font_med, cw_m, ch_m,
                        (100, 255, 200), start_y=art_y)

        chars_shown = int((scene_t / 1.0) * len(MOTTO_STARS))
        typed = MOTTO_STARS[:min(chars_shown, len(MOTTO_STARS))]
        draw_text_centered(draw, motto_y, typed, font_med, AMBER)

        if scene_t > 1.1:
            eng_t = scene_t - 1.1
            eng_chars = int((eng_t / 0.6) * len(MOTTO_STARS_EN))
            eng_typed = MOTTO_STARS_EN[:min(eng_chars, len(MOTTO_STARS_EN))]
            draw_text_centered(draw, motto_y + ch_m + 10, eng_typed, font_small, GREEN_DIM)

    # --- SCENE 7: Fade out (18-20s) ---
    else:
        scene_t = t - 18.0
        fade = max(0, 1.0 - scene_t / 2.0)
        draw_matrix_rain(draw, t, opacity=0.06 * fade)
        draw_ascii_block(draw, rocket_lines, font_med, cw_m, ch_m,
                        (100, 255, 200), start_y=art_y, alpha=fade)
        draw_text_centered(draw, motto_y, MOTTO_STARS, font_med, AMBER, alpha=fade)
        draw_text_centered(draw, motto_y + ch_m + 10, MOTTO_STARS_EN, font_small, GREEN_DIM, alpha=fade)

        # Draw some stars
        random.seed(42)
        for _ in range(80):
            sx, sy = random.randint(0, W-1), random.randint(0, H-1)
            brightness = random.random() * fade
            sc = (int(200 * brightness), int(255 * brightness), int(200 * brightness))
            draw.text((sx, sy), random.choice('.*+'), fill=sc, font=font_small)

    # Post-processing
    img = apply_post(img)
    return img


def main():
    print(f"Rendering {TOTAL_FRAMES} frames at {W}x{H} @ {FPS}fps...")
    start = time.time()

    # Open ffmpeg pipe
    cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{W}x{H}',
        '-pix_fmt', 'rgb24',
        '-r', str(FPS),
        '-i', '-',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '20',
        '-pix_fmt', 'yuv420p',
        OUT
    ]

    stderr_path = '/tmp/ffmpeg_render.log'
    stderr_fh = open(stderr_path, 'w')
    pipe = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=stderr_fh)

    for i in range(TOTAL_FRAMES):
        frame = render_frame(i)
        pipe.stdin.write(np.array(frame).tobytes())
        if i % FPS == 0:
            elapsed = time.time() - start
            fps_actual = (i + 1) / elapsed if elapsed > 0 else 0
            print(f"  Frame {i}/{TOTAL_FRAMES} ({i/FPS:.1f}s) - {fps_actual:.1f} fps render speed")

    pipe.stdin.close()
    pipe.wait()
    stderr_fh.close()

    elapsed = time.time() - start
    size_mb = os.path.getsize(OUT) / 1024 / 1024
    print(f"\nDone! {elapsed:.1f}s render time, {size_mb:.1f}MB")
    print(f"Output: {OUT}")


if __name__ == '__main__':
    main()
