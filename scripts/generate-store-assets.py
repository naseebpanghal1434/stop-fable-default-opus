#!/usr/bin/env python3
"""Draw toolbar icons and capture Chrome Web Store images."""
from __future__ import annotations

import math
import os
import struct
import subprocess
import sys
import zlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ICONS = os.path.join(ROOT, "icons")
ASSETS = os.path.join(ROOT, "store", "assets")
HTML = os.path.join(ROOT, "store", "html")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BG = (26, 26, 26, 255)
CREAM = (244, 237, 228, 255)
CORAL = (196, 92, 62, 255)
CLEAR = (0, 0, 0, 0)


def chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png(w: int, h: int, rgba: bytes) -> bytes:
    raw = b"".join(b"\x00" + rgba[y * w * 4 : (y + 1) * w * 4] for y in range(h))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def sips_size(path: str) -> tuple[int, int]:
    out = subprocess.check_output(
        ["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], text=True
    )
    w = h = None
    for line in out.splitlines():
        if "pixelWidth" in line:
            w = int(line.split()[-1])
        if "pixelHeight" in line:
            h = int(line.split()[-1])
    if not w or not h:
        raise SystemExit(f"could not read size for {path}: {out}")
    return w, h


def flatten_png(path: str) -> None:
    tmp = path + ".jpg"
    subprocess.run(
        ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "90", path, "--out", tmp],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["sips", "-s", "format", "png", tmp, "--out", path],
        check=True,
        capture_output=True,
    )
    os.remove(tmp)


def clamp(x: float, a: float = 0.0, b: float = 1.0) -> float:
    return a if x < a else b if x > b else x


def mix(c1, c2, t: float):
    t = clamp(t)
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def sdf_round_rect(px, py, cx, cy, hw, hh, r):
    dx = abs(px - cx) - (hw - r)
    dy = abs(py - cy) - (hh - r)
    ox, oy = max(dx, 0.0), max(dy, 0.0)
    return math.hypot(ox, oy) + min(max(dx, dy), 0.0) - r


def sdf_circle(px, py, cx, cy, r):
    return math.hypot(px - cx, py - cy) - r


def draw_mark(size: int, pad: int = 0) -> bytes:
    inner = size - pad * 2
    out = bytearray(size * size * 4)
    # draw into inner square, then copy into padded canvas
    cx = cy = (inner - 1) / 2.0
    tile_hw = inner * 0.46
    tile_r = inner * 0.22
    disc_r = inner * 0.22
    ring_r = inner * 0.28
    tick_cx = cx + inner * 0.22
    tick_cy = cy - inner * 0.22
    tick_r = inner * 0.09
    inner_px = bytearray(inner * inner * 4)

    for y in range(inner):
        for x in range(inner):
            acc = [0, 0, 0, 0]
            for oy in (0.25, 0.75):
                for ox in (0.25, 0.75):
                    px, py = x + ox, y + oy
                    tile = sdf_round_rect(px, py, cx, cy, tile_hw, tile_hw, tile_r)
                    a_tile = clamp(0.5 - tile)
                    col = CLEAR
                    if a_tile > 0:
                        col = BG
                        ring = abs(sdf_circle(px, py, cx, cy, ring_r)) - inner * 0.035
                        disc = sdf_circle(px, py, cx, cy, disc_r)
                        a_ring = clamp(0.5 - ring)
                        a_disc = clamp(0.5 - disc)
                        if a_ring > 0:
                            col = mix(col, CREAM, a_ring)
                        if a_disc > 0:
                            col = mix(col, CREAM, a_disc)
                        tick = sdf_circle(px, py, tick_cx, tick_cy, tick_r)
                        a_tick = clamp(0.5 - tick)
                        if a_tick > 0:
                            col = mix(col, CORAL, a_tick)
                        if a_tile < 1:
                            col = (col[0], col[1], col[2], int(col[3] * a_tile))
                    for i in range(4):
                        acc[i] += col[i]
            i = (y * inner + x) * 4
            inner_px[i : i + 4] = bytes(v // 4 for v in acc)

    if pad == 0:
        return bytes(inner_px)
    for y in range(inner):
        src = y * inner * 4
        dst = ((y + pad) * size + pad) * 4
        out[dst : dst + inner * 4] = inner_px[src : src + inner * 4]
    return bytes(out)


def write_png(path: str, w: int, h: int, rgba: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(encode_png(w, h, rgba))
    print("wrote", path, os.path.getsize(path))


def screenshot(html_name: str, out_name: str, w: int, h: int) -> None:
    src = os.path.join(HTML, html_name)
    dest = os.path.join(ASSETS, out_name)
    url = "file://" + src
    cmd = [
        CHROME,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=1",
        f"--window-size={w},{h}",
        f"--screenshot={dest}",
        "--virtual-time-budget=2000",
        url,
    ]
    proc = subprocess.run(cmd, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr.decode("utf-8", "replace"))
        raise SystemExit(f"chrome failed for {html_name}")
    pw, ph = sips_size(dest)
    if (pw, ph) != (w, h):
        subprocess.run(
            ["sips", "-z", str(h), str(w), dest],
            check=True,
            capture_output=True,
        )
        pw, ph = sips_size(dest)
    if (pw, ph) != (w, h):
        raise SystemExit(f"{out_name} is {pw}x{ph}, expected {w}x{h}")
    flatten_png(dest)
    print("shot", dest, f"{pw}x{ph}")


def main() -> None:
    if not os.path.exists(CHROME):
        sys.exit(f"Chrome not found at {CHROME}")

    os.makedirs(ICONS, exist_ok=True)
    os.makedirs(ASSETS, exist_ok=True)

    for size in (16, 32, 48):
        write_png(os.path.join(ICONS, f"icon{size}.png"), size, size, draw_mark(size))

    # 128 in the zip: 96px glyph + 16px transparent padding (CWS icon spec).
    write_png(os.path.join(ICONS, "icon128.png"), 128, 128, draw_mark(128, pad=16))
    write_png(os.path.join(ASSETS, "store-icon-128.png"), 128, 128, draw_mark(128, pad=16))

    # Full-bleed mark for promo HTML.
    write_png(os.path.join(HTML, "mark.png"), 128, 128, draw_mark(128))

    screenshot("screenshot-1.html", "screenshot-1.png", 1280, 800)
    screenshot("screenshot-2.html", "screenshot-2.png", 1280, 800)
    screenshot("screenshot-3.html", "screenshot-3.png", 1280, 800)
    screenshot("promo-small.html", "promo-small-440x280.png", 440, 280)
    screenshot("promo-marquee.html", "promo-marquee-1400x560.png", 1400, 560)


if __name__ == "__main__":
    main()
