#!/usr/bin/env python3
"""
texture2collision.py  —  Texture PNG -> NDS Collision Map Header
For the Persona 3 Dual project.

Converts a painted PNG (one pixel = one tile) into a C header containing a
collision_map[][] array for use on the Nintendo DS.

Tile colors are loaded from a shared collision_palette.json so the whole team
stays in sync without editing this file.

Pass --env with the matching _env.h to automatically derive world-space tile
sizes and offsets so the collision grid lines up exactly with the 3D model.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

IMPORTANT — always use --env or the collision scale will not match the model:

    python3 texture2collision.py collision.png out.h --env model_env.h

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Usage:
    python3 texture2collision.py collision.png output.h --env model_env.h
    python3 texture2collision.py collision.png output.h --env model_env.h --palette collision_palette.json
    python3 texture2collision.py collision.png output.h --env model_env.h --crop 0 0 44 33
    python3 texture2collision.py collision.png output.h --env model_env.h --tolerance 15
    python3 texture2collision.py --print-palette

How scale matching works:
    obj2environment.py writes defines such as:
        #define MAP_WORLD_OFFSET_X  2.000000f
        #define MAP_WORLD_OFFSET_Z  2.000000f
        #define MAP_WORLD_WIDTH     4.000000f
        #define MAP_WORLD_DEPTH     3.000000f

    This script reads those values and derives tile sizes from the FULL image
    dimensions (before any crop), then adjusts the world offset to account for
    where the crop sits inside the full image:

        tile_size_x = WORLD_WIDTH  / full_image_width    (NDS units per tile)
        tile_size_z = WORLD_DEPTH  / full_image_height

        # col 0 of the output grid maps to this world X position:
        world_offset_x = WORLD_OFFSET_X - (full_w - crop_x - crop_w) * tile_size_x

    Runtime lookup in C++:
        int col = (int)((player.x + COLLISION_WORLD_OFFSET_X) / COLLISION_TILE_SIZE_X);
        int row = (int)((player.z + COLLISION_WORLD_OFFSET_Z) / COLLISION_TILE_SIZE_Z);
        uint8_t tile = collision_map[row][col];

How --crop interacts with world offset:
    The full PNG represents the complete model footprint.
    One pixel = one tile at the model's native tile resolution.
    If only part of the PNG has collision data, pass --crop x y w h (pixels).
    The world offset is automatically adjusted so col 0 of the output maps to
    the correct world-space X position, not the left edge of the full model.
"""

import sys
import os
import re
import json
import argparse

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow is required.")
    print("  pip install Pillow")
    sys.exit(1)


# ── Palette ────────────────────────────────────────────────────────────────────

def find_default_palette(script_dir):
    for d in [script_dir, os.getcwd()]:
        p = os.path.join(d, "collision_palette.json")
        if os.path.exists(p):
            return p
    return None


def load_palette(path):
    """
    Load collision_palette.json.
    Returns (palette, raw_data) where:
        palette  : {(r, g, b): tile_id}
        raw_data : original parsed dict (used for the legend comment)
    """
    with open(path, 'r') as f:
        data = json.load(f)
    palette = {}
    for name, info in data.items():
        key = tuple(int(v) for v in info['rgb'])
        palette[key] = int(info['id'])
    return palette, data


# ── World bounds from _env.h ───────────────────────────────────────────────────

_DEF_RE = re.compile(
    r'#define\s+\w+_(WORLD_OFFSET_X|WORLD_OFFSET_Z|WORLD_WIDTH|WORLD_DEPTH'
    r'|TILE_SIZE_X|TILE_SIZE_Z|MAP_COLS|MAP_ROWS)\s+([\d.eE+\-]+)f?'
)

def parse_env_header(env_path):
    """
    Read an _env.h produced by obj2environment.py and return a dict of
    world-bound defines. Keys that may be present:
        WORLD_OFFSET_X, WORLD_OFFSET_Z   — always written
        WORLD_WIDTH, WORLD_DEPTH         — written when --tiles was NOT used
        TILE_SIZE_X, TILE_SIZE_Z         — written when --tiles WAS used
        MAP_COLS, MAP_ROWS               — written when --tiles WAS used
    Values are float, except MAP_COLS/MAP_ROWS which are int.
    Returns None if the file is missing or has no matching defines.
    """
    if not env_path or not os.path.exists(env_path):
        return None
    bounds = {}
    with open(env_path, 'r', errors='replace') as f:
        for line in f:
            m = _DEF_RE.search(line)
            if m:
                key, val = m.group(1), m.group(2)
                bounds[key] = int(val) if key in ('MAP_COLS', 'MAP_ROWS') else float(val)
    return bounds if bounds else None


# ── Color matching ─────────────────────────────────────────────────────────────

def color_matches(pixel, target, tolerance):
    return all(abs(pixel[i] - target[i]) <= tolerance for i in range(3))

def pixel_to_tile(r, g, b, palette, tolerance):
    for color, tile_id in palette.items():
        if color_matches((r, g, b), color, tolerance):
            return tile_id
    return 0


# ── World-space math ───────────────────────────────────────────────────────────

def compute_world_params(bounds, full_w, full_h, crop):
    """
    Derive tile_size_x/z and world_offset_x/z from the env.h bounds,
    the FULL image dimensions, and the crop region.

    The fundamental rule:
        tile_size = world_size / FULL_image_pixel_count

    The crop only affects the world OFFSET (where col 0 starts in world space),
    not the tile size. Tile size is a property of the model, not the crop.

    After crop(cx, cy, cw, ch) followed by ROTATE_180:
        col 0 of the output grid corresponds to
        full-rotated-image col = (full_w - cx - cw)

    So the world X at col 0 = (full_w - cx - cw) * tile_size_x - env_offset_x.
    For the lookup formula  player.x + NEW_OFFSET = col * tile_size  to give
    col=0 at that world position we need:
        NEW_OFFSET_X = env_offset_x - (full_w - cx - cw) * tile_size_x

    Returns (tile_size_x, tile_size_z, world_offset_x, world_offset_z)
    or (None, None, None, None) if bounds is missing required keys.
    """
    if bounds is None:
        return None, None, None, None

    env_ox = bounds.get('WORLD_OFFSET_X')
    env_oz = bounds.get('WORLD_OFFSET_Z')

    if 'TILE_SIZE_X' in bounds and 'TILE_SIZE_Z' in bounds:
        # --tiles mode: tile sizes already computed in env.h
        ts_x = bounds['TILE_SIZE_X']
        ts_z = bounds['TILE_SIZE_Z']
        # Reference full dimensions: use MAP_COLS/ROWS from env.h if available,
        # because the user explicitly specified the grid size with --tiles.
        ref_w = bounds.get('MAP_COLS', full_w)
        ref_h = bounds.get('MAP_ROWS', full_h)
    elif 'WORLD_WIDTH' in bounds and 'WORLD_DEPTH' in bounds:
        # Standard mode: derive tile size from world size / full image pixel count
        ts_x = bounds['WORLD_WIDTH'] / full_w
        ts_z = bounds['WORLD_DEPTH'] / full_h
        ref_w = full_w
        ref_h = full_h
    else:
        print("  [WARN] env.h is missing WORLD_WIDTH/DEPTH or TILE_SIZE_X/Z.")
        print("         World-space defines will be omitted.")
        return None, None, None, None

    # Crop parameters (default = no crop = full image)
    if crop:
        cx, cy, cw, ch = crop
    else:
        cx, cy, cw, ch = 0, 0, ref_w, ref_h

    # After crop-then-ROTATE_180, col 0 of the output corresponds to
    # column (ref_w - cx - cw) in the full rotated image.
    rotated_col_0 = ref_w - cx - cw
    rotated_row_0 = ref_h - cy - ch

    # Adjusted world offsets so that the lookup formula gives the correct
    # world position for col 0 / row 0 of the cropped output.
    new_ox = (env_ox or 0.0) - rotated_col_0 * ts_x
    new_oz = (env_oz or 0.0) - rotated_row_0 * ts_z

    return ts_x, ts_z, new_ox, new_oz


# ── Core conversion ────────────────────────────────────────────────────────────

def convert(input_path, output_path, palette, raw_palette_data,
            env_path=None, tolerance=10, crop=None):

    if not os.path.isfile(input_path):
        print(f"  Error: input PNG not found: {input_path}")
        sys.exit(1)

    img = Image.open(input_path).convert("RGB")

    # ── Record full dimensions BEFORE any crop ────────────────────────────────
    # Tile sizes are derived from the FULL image because one pixel = one tile
    # at the model's native resolution. Cropping only changes where in world
    # space the output grid starts — it does not change the tile size.
    full_w, full_h = img.size
    print(f"  Full image: {full_w} x {full_h} pixels")

    if crop:
        cx, cy, cw, ch = crop
        img = img.crop((cx, cy, cx + cw, cy + ch))
        print(f"  Crop: x={cx}, y={cy}, w={cw}, h={ch}  →  {cw}x{ch} tile grid")

    # ROTATE_180 matches the UV flip in obj2environment.py.
    # The NDS display list uses bottom-left as UV origin; PNG uses top-left.
    img = img.transpose(Image.ROTATE_180)
    map_cols, map_rows = img.size
    print(f"  Output grid: {map_cols} cols x {map_rows} rows")

    # ── World-space parameters ────────────────────────────────────────────────
    bounds = parse_env_header(env_path)
    env_basename = os.path.basename(env_path) if env_path else ""

    if env_path and not bounds:
        print(f"  [WARN] Could not read world bounds from {env_path}.")
        print(f"         Check that the file exists and was produced by obj2environment.py.")

    if not env_path:
        print()
        print("  *** WARNING: --env not provided. ***")
        print("  Tile sizes will NOT be written to the header.")
        print("  The collision grid will not match the scaled 3D model.")
        print("  Re-run with:  --env path/to/model_env.h")
        print()

    tile_size_x, tile_size_z, world_offset_x, world_offset_z = \
        compute_world_params(bounds, full_w, full_h, crop)

    if tile_size_x is not None:
        print(f"  Tile size:    X={tile_size_x:.6f}  Z={tile_size_z:.6f} NDS units")
        print(f"  World offset: X={world_offset_x:.6f}  Z={world_offset_z:.6f}")

    # ── Build tile grid ───────────────────────────────────────────────────────
    tile_grid = []
    for row_y in range(map_rows):
        row = []
        for col_x in range(map_cols):
            r, g, b = img.getpixel((col_x, row_y))
            row.append(pixel_to_tile(r, g, b, palette, tolerance))
        tile_grid.append(row)

    # ── Write header ──────────────────────────────────────────────────────────
    stem  = os.path.splitext(os.path.basename(output_path))[0]
    guard = stem.upper().replace('-', '_')
    pfx   = guard

    with open(output_path, 'w') as f:
        f.write("// Auto-generated by texture2collision.py — do not edit manually\n")
        f.write(f"// Source PNG:  {os.path.basename(input_path)}\n")
        if env_path:
            f.write(f"// World data: {env_basename}\n")
        if crop:
            f.write(f"// Crop:       x={crop[0]}, y={crop[1]}, "
                    f"w={crop[2]}, h={crop[3]}  (of {full_w}x{full_h} full image)\n")
        f.write("\n")
        f.write(f"#ifndef {guard}_H\n")
        f.write(f"#define {guard}_H\n\n")
        f.write("#include <stdint.h>\n\n")

        # Grid dimensions
        f.write(f"#define {pfx}_MAP_COLS  {map_cols}\n")
        f.write(f"#define {pfx}_MAP_ROWS  {map_rows}\n\n")

        # World-space defines
        if tile_size_x is not None:
            f.write(f"// World-space coordinates — derived from {env_basename}\n")
            f.write(f"// Tile size is computed from the FULL image ({full_w}x{full_h} px)\n")
            if crop:
                f.write(f"// World offset is adjusted for the crop region "
                        f"(x={crop[0]}, y={crop[1]})\n")
            f.write(f"//\n")
            f.write(f"// Runtime lookup:\n")
            f.write(f"//   int col = (int)((player.x + {pfx}_WORLD_OFFSET_X)"
                    f" / {pfx}_TILE_SIZE_X);\n")
            f.write(f"//   int row = (int)((player.z + {pfx}_WORLD_OFFSET_Z)"
                    f" / {pfx}_TILE_SIZE_Z);\n")
            f.write(f"//   uint8_t tile = collision_map[row][col];\n")
            f.write(f"#define {pfx}_WORLD_OFFSET_X  {world_offset_x:.6f}f\n")
            f.write(f"#define {pfx}_WORLD_OFFSET_Z  {world_offset_z:.6f}f\n")
            f.write(f"#define {pfx}_TILE_SIZE_X     {tile_size_x:.6f}f\n")
            f.write(f"#define {pfx}_TILE_SIZE_Z     {tile_size_z:.6f}f\n")
            f.write("\n")

        # Tile legend
        f.write("// Tile values (from collision_palette.json):\n")
        f.write("//   0 = walkable (default / unrecognized color)\n")
        for name, info in raw_palette_data.items():
            f.write(f"//   {info['id']} = {name}  RGB{tuple(info['rgb'])}\n")
        f.write("\n")

        # Map array
        f.write(f"static const uint8_t collision_map"
                f"[{pfx}_MAP_ROWS][{pfx}_MAP_COLS] = {{\n")
        for row in tile_grid:
            f.write("    {" + ", ".join(str(t) for t in row) + "},\n")
        f.write("};\n\n")

        f.write(f"#endif // {guard}_H\n")

    print(f"  Written: {output_path}")


# ── CLI ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Convert a painted PNG texture to an NDS collision map C header.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument('input',           nargs='?',
                        help='Input PNG texture (painted collision map)')
    parser.add_argument('output',          nargs='?',
                        help='Output .h header file')
    parser.add_argument('--env',           default=None,
                        help='Path to the _env.h from obj2environment.py. '
                             'Required for correct scale matching with the 3D model.')
    parser.add_argument('--palette',       default=None,
                        help='Path to collision_palette.json '
                             '(default: looks next to this script, then cwd)')
    parser.add_argument('--tolerance',     type=int, default=10,
                        help='Color match tolerance 0-127 (default: 10)')
    parser.add_argument('--crop',          type=int, nargs=4,
                        metavar=('X', 'Y', 'W', 'H'),
                        help='Crop region in pixels (of the FULL original image). '
                             'Tile sizes are still derived from the full image size; '
                             'only the world offset is adjusted for the crop position.')
    parser.add_argument('--print-palette', action='store_true',
                        help='Print the loaded palette and exit')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    # ── Load palette ──────────────────────────────────────────────────────────
    palette_path = args.palette or find_default_palette(script_dir)
    if palette_path is None:
        print("Error: No collision_palette.json found.")
        print("  Use --palette <path>, or place collision_palette.json next to this script.")
        sys.exit(1)

    print(f"Palette:  {palette_path}")
    try:
        palette, raw_palette_data = load_palette(palette_path)
    except FileNotFoundError:
        print(f"Error: Palette file not found: {palette_path}")
        sys.exit(1)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error: Bad palette JSON: {e}")
        sys.exit(1)

    if args.print_palette:
        print(f"\n{len(palette)} palette entries:")
        for (r, g, b), tid in sorted(palette.items(), key=lambda x: x[1]):
            name = next((n for n, info in raw_palette_data.items()
                         if tuple(info['rgb']) == [r, g, b]), "?")
            print(f"  id={tid:>4}  RGB({r:>3},{g:>3},{b:>3})  {name}")
        sys.exit(0)

    print(f"  {len(palette)} entries loaded")

    if not args.input or not args.output:
        parser.error("input and output are required (or use --print-palette)")

    print(f"Input:    {args.input}")
    print(f"Output:   {args.output}")
    if args.env:
        print(f"Env:      {args.env}")

    convert(
        input_path       = args.input,
        output_path      = args.output,
        palette          = palette,
        raw_palette_data = raw_palette_data,
        env_path         = args.env,
        tolerance        = args.tolerance,
        crop             = args.crop,
    )


if __name__ == '__main__':
    main()