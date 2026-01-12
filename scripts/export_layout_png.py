#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "assets" / "project-layout.png"

IGNORE_DIRS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "venv",
    ".venv",
}

IGNORE_FILES = {
    ".DS_Store",
}


def list_tree(root: Path) -> List[Tuple[int, str]]:
    """
    Return a list of (depth, entry_name) tuples representing the visible tree.
    Depth starts at 0 for the root entry.
    """
    lines: List[Tuple[int, str]] = []

    def walk(dir_path: Path, depth: int) -> None:
        try:
            entries = sorted(dir_path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
        except PermissionError:
            return

        for p in entries:
            name = p.name
            if p.is_dir() and name in IGNORE_DIRS:
                continue
            if p.is_file() and name in IGNORE_FILES:
                continue
            # hide dot files/dirs except .env.example
            if name.startswith(".") and name not in {".env.example"}:
                continue
            rel = p.relative_to(PROJECT_ROOT)
            display = str(rel) + ("/" if p.is_dir() else "")
            lines.append((depth, display))
            if p.is_dir():
                walk(p, depth + 1)

    # add top-level marker
    lines.append((0, PROJECT_ROOT.name + "/"))
    walk(PROJECT_ROOT, 1)
    return lines


def render_text_to_png(lines: Iterable[Tuple[int, str]], output_path: Path) -> None:
    # Rendering params
    padding_x = 20
    padding_y = 16
    indent_px = 24
    line_height = 22
    bg = (250, 252, 255)
    fg = (33, 37, 41)

    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    # Compute image size
    lines_list = list(lines)
    max_width = 0
    def text_size(s: str) -> Tuple[int, int]:
        # Pillow >=10: use getbbox; fallback to getsize for older versions
        try:
            bbox = font.getbbox(s)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except Exception:
            return font.getsize(s)

    for depth, text in lines_list:
        w, _ = text_size((" " * depth * 2) + text)
        max_width = max(max_width, int(w) + depth * indent_px)
    img_width = padding_x * 2 + max_width
    img_height = padding_y * 2 + line_height * len(lines_list)

    # Create and draw
    img = Image.new("RGB", (img_width, img_height), bg)
    draw = ImageDraw.Draw(img)

    y = padding_y
    for depth, text in lines_list:
        x = padding_x + depth * indent_px
        draw.text((x, y), text, font=font, fill=fg)
        y += line_height

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)
    print(f"Wrote {output_path} ({img_width}x{img_height})")


def main() -> None:
    tree = list_tree(PROJECT_ROOT)
    render_text_to_png(tree, OUTPUT_PATH)


if __name__ == "__main__":
    main()

