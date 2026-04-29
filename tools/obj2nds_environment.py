#!/usr/bin/env python3
"""
obj2nds_environment.py  —  Multi-texture OBJ -> NDS C Header Converter
For the Persona 3 Dual project.

Produces:
  - modelName_env.h        : display lists + Load/Draw/Delete functions + world bounds
  - modelName_textures.txt : PNG paths for GRIT
  - modelName_collision.h  : collision tile map  (optional, see --collision-png)

Usage:
    python obj2nds_environment.py input.obj output_dir/
    python obj2nds_environment.py input.obj output_dir/ --target-size 4.0
    python obj2nds_environment.py input.obj output_dir/ --scale 0.054
    python obj2nds_environment.py input.obj output_dir/ --no-center
    python obj2nds_environment.py input.obj output_dir/ --source-blender
    python obj2nds_environment.py input.obj output_dir/ --tiles 0 0 64 64
    python obj2nds_environment.py input.obj output_dir/ --mapping mat_map.json

    # Collision map (auto-scales to match the 3D model, no Pillow needed):
    python obj2nds_environment.py input.obj output_dir/ \\
        --collision-png   collision.png \\
        --collision-palette collision_palette.json   # optional; auto-discovered
        --collision-out   room_collision             # optional; default: <model>_collision
        --collision-crop  0 0 44 33                 # optional; pixel region of full PNG
        --collision-tolerance 10                    # optional; default 10

Collision palette JSON format (collision_palette.json):
    {
        "Collision": {"rgb": [197, 0, 0],   "id": 1},
        "Save":      {"rgb": [197, 194, 0], "id": 2}
    }

If --collision-palette is omitted the script searches for collision_palette.json
next to itself, then next to the input OBJ, then in the output directory.
"""

import sys, os, re, json, struct, zlib, argparse
from collections import defaultdict

# ── NDS GPU constants ──────────────────────────────────────────────────────────
FIFO_TEXCOORD = 0x22
FIFO_BEGIN    = 0x40
FIFO_VERTEX16 = 0x23
FIFO_NOP      = 0x00
GL_TRIANGLES  = 0
GL_QUADS      = 1
VALID_TEX_SIZES = {8, 16, 32, 64, 128, 256, 512, 1024}

# ── Shared helpers ─────────────────────────────────────────────────────────────

def sanitize(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def floattov16(f):
    return max(-32768, min(32767, int(f * (1 << 12)))) & 0xFFFF

def floattot16(f):
    return max(-32768, min(32767, int(f * (1 << 4)))) & 0xFFFF

def pack_cmds(c1, c2=FIFO_NOP, c3=FIFO_NOP, c4=FIFO_NOP):
    return struct.pack('<I', (c4 << 24) | (c3 << 16) | (c2 << 8) | c1)

# ── PNG reader (stdlib only, no Pillow) ────────────────────────────────────────

def _paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else (b if pb <= pc else c)

def read_png_pixels(path):
    """
    Read a PNG using only stdlib (struct + zlib).
    Supports 8-bit RGB (color_type 2) and RGBA (color_type 6), all 5 filter types.
    Returns (rgb_rows, width, height) where rgb_rows[y][x] = (r, g, b).
    Returns (None, None, None) on any failure.
    """
    try:
        with open(path, 'rb') as f:
            data = f.read()

        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return None, None, None

        pos, ihdr, idat = 8, None, []
        while pos < len(data):
            length = struct.unpack('>I', data[pos:pos+4])[0]
            ctype  = data[pos+4:pos+8]
            chunk  = data[pos+8:pos+8+length]
            pos   += 12 + length
            if   ctype == b'IHDR': ihdr = chunk
            elif ctype == b'IDAT': idat.append(chunk)
            elif ctype == b'IEND': break

        if ihdr is None:
            return None, None, None

        w, h       = struct.unpack('>II', ihdr[:8])
        bit_depth  = ihdr[8]
        color_type = ihdr[9]
        if bit_depth != 8:
            return None, None, None

        nch = {2: 3, 6: 4}.get(color_type)
        if nch is None:
            return None, None, None

        raw  = zlib.decompress(b''.join(idat))
        rows = []
        idx  = 0
        for _ in range(h):
            filt = raw[idx]; idx += 1
            row  = bytearray(raw[idx:idx + w * nch]); idx += w * nch
            prev = rows[-1] if rows else bytearray(w * nch)
            if filt == 1:
                for i in range(nch, len(row)):
                    row[i] = (row[i] + row[i - nch]) & 0xFF
            elif filt == 2:
                for i in range(len(row)):
                    row[i] = (row[i] + prev[i]) & 0xFF
            elif filt == 3:
                for i in range(len(row)):
                    a = row[i - nch] if i >= nch else 0
                    row[i] = (row[i] + (a + prev[i]) // 2) & 0xFF
            elif filt == 4:
                for i in range(len(row)):
                    a = row[i - nch] if i >= nch else 0
                    row[i] = (row[i] + _paeth(a, prev[i], prev[i - nch] if i >= nch else 0)) & 0xFF
            rows.append(bytes(row))

        rgb_rows = [
            [(row[i], row[i+1], row[i+2]) for i in range(0, len(row), nch)]
            for row in rows
        ]
        return rgb_rows, w, h

    except Exception:
        return None, None, None

# ── Collision palette ──────────────────────────────────────────────────────────

def find_collision_palette(search_dirs):
    """Auto-discover collision_palette.json in a list of directories."""
    for d in search_dirs:
        p = os.path.join(d, 'collision_palette.json')
        if os.path.exists(p):
            return p
    return None

def load_collision_palette(path):
    """
    Load collision_palette.json.
    Returns ({(r,g,b): tile_id}, raw_dict) or (None, None) on failure.
    """
    try:
        with open(path, 'r') as f:
            raw = json.load(f)
        palette = {tuple(int(v) for v in info['rgb']): int(info['id'])
                   for info in raw.values()}
        return palette, raw
    except Exception as e:
        print(f"  [COLLISION] Could not load palette {path}: {e}")
        return None, None

def _color_matches(pixel, target, tol):
    return all(abs(pixel[i] - target[i]) <= tol for i in range(3))

def _pixel_to_tile(r, g, b, palette, tol):
    for color, tid in palette.items():
        if _color_matches((r, g, b), color, tol):
            return tid
    return 0

# ── Collision header writer ────────────────────────────────────────────────────

def write_collision_header(png_path, out_path, out_stem,
                           palette, raw_palette,
                           world_offset_x, world_offset_z,
                           world_width, world_depth,
                           tolerance=10, crop=None):
    """
    Read png_path, map pixels to tile IDs, write a C header to out_path.

    Tile sizes are derived from the FULL image dimensions (before crop) because
    one pixel = one tile at the model's native resolution. The crop region only
    shifts the world-space offset — it does not change the tile size.

    After crop(cx,cy,cw,ch) + ROTATE_180, col 0 of the output corresponds to
    full-image column (full_w - cx - cw), giving:
        new_offset_x = world_offset_x - (full_w - cx - cw) * tile_size_x
    """
    rgb_rows, full_w, full_h = read_png_pixels(png_path)
    if rgb_rows is None:
        print(f"  [COLLISION] ERROR: could not read PNG '{png_path}'")
        print(f"              Make sure it is a standard 8-bit RGB/RGBA PNG.")
        return False

    print(f"  [COLLISION] PNG: {full_w}x{full_h} — {os.path.basename(png_path)}")

    # Crop (before rotate, using original pixel coordinates)
    if crop:
        cx, cy, cw, ch = crop
        rgb_rows = [row[cx:cx + cw] for row in rgb_rows[cy:cy + ch]]
        print(f"  [COLLISION] Crop: x={cx} y={cy} w={cw} h={ch}")
    else:
        cx = cy = 0
        cw, ch = full_w, full_h

    # FLIP VERTICAL ONLY — matches the UV flip in the display list (V = 1-v)
    # Do NOT reverse the columns, otherwise the map mirrors on the X-axis!
    rgb_rows = list(reversed(rgb_rows))

    map_cols = len(rgb_rows[0]) if rgb_rows else 0
    map_rows = len(rgb_rows)
    print(f"  [COLLISION] Grid: {map_cols} cols x {map_rows} rows")

    # Tile sizes from FULL image (not crop)
    ts_x = world_width  / full_w
    ts_z = world_depth  / full_h

    # World offset adjusted for crop position (Fixed Math)
    # Since we didn't flip X, the X crop position is just cx.
    # We flipped Y, so row 0 is the bottom of the crop (full_h - cy - ch)
    adj_ox = world_offset_x - (cx * ts_x)
    adj_oz = world_offset_z - ((full_h - cy - ch) * ts_z)

    print(f"  [COLLISION] Tile size : X={ts_x:.6f}  Z={ts_z:.6f} NDS units")
    print(f"  [COLLISION] Offset    : X={adj_ox:.6f}  Z={adj_oz:.6f}")

    # Build tile grid
    tile_grid = [
        [_pixel_to_tile(p[0], p[1], p[2], palette, tolerance) for p in row]
        for row in rgb_rows
    ]

    # Write header
    pfx   = sanitize(out_stem).upper()
    guard = pfx + '_H'

    with open(out_path, 'w') as f:
        f.write("// Auto-generated by obj2nds_environment.py — do not edit manually\n")
        f.write(f"// Source: {os.path.basename(png_path)}\n")
        if crop:
            f.write(f"// Crop:   x={cx} y={cy} w={cw} h={ch} "
                    f"(of {full_w}x{full_h} full image)\n")
        f.write(f"\n#ifndef {guard}\n#define {guard}\n\n")
        f.write("#include <stdint.h>\n\n")

        f.write(f"#define {pfx}_MAP_COLS  {map_cols}\n")
        f.write(f"#define {pfx}_MAP_ROWS  {map_rows}\n\n")

        f.write(f"// World-space lookup:\n")
        f.write(f"//   int col = (int)((x + {pfx}_WORLD_OFFSET_X) / {pfx}_TILE_SIZE_X);\n")
        f.write(f"//   int row = (int)((z + {pfx}_WORLD_OFFSET_Z) / {pfx}_TILE_SIZE_Z);\n")
        f.write(f"//   uint8_t tile = collision_map[row][col];\n")
        f.write(f"#define {pfx}_WORLD_OFFSET_X  {adj_ox:.6f}f\n")
        f.write(f"#define {pfx}_WORLD_OFFSET_Z  {adj_oz:.6f}f\n")
        f.write(f"#define {pfx}_TILE_SIZE_X     {ts_x:.6f}f\n")
        f.write(f"#define {pfx}_TILE_SIZE_Z     {ts_z:.6f}f\n\n")

        f.write("// Tile values (from collision_palette.json):\n")
        f.write("//   0 = walkable (default)\n")
        for name, info in raw_palette.items():
            f.write(f"//   {info['id']} = {name}  RGB{tuple(info['rgb'])}\n")
        f.write("\n")

        f.write(f"static const uint8_t collision_map[{pfx}_MAP_ROWS][{pfx}_MAP_COLS] = {{\n")
        for row in tile_grid:
            f.write("    {" + ", ".join(str(t) for t in row) + "},\n")
        f.write("};\n\n")
        f.write(f"#endif // {guard}\n")

    print(f"  [COLLISION] Written: {out_path}")
    return True

# ── OBJ / MTL parser ──────────────────────────────────────────────────────────

def parse_mtl(mtl_path, extra_mapping=None):
    mapping = {}
    if mtl_path and os.path.exists(mtl_path):
        current = None
        with open(mtl_path, 'r', errors='replace') as f:
            for line in f:
                parts = line.strip().split()
                if not parts: continue
                if parts[0] == 'newmtl':
                    current = parts[1] if len(parts) > 1 else None
                elif parts[0] == 'map_Kd' and current:
                    mapping[current] = line.strip()[len('map_Kd'):].strip()
    if extra_mapping:
        mapping.update(extra_mapping)
    return mapping

def parse_obj(obj_path):
    vertices, texcoords, groups = [], [], []
    current_mat, current_faces = '__no_material__', []

    def flush():
        if current_faces:
            groups.append({'material': current_mat, 'faces': list(current_faces)})

    with open(obj_path, 'r', errors='replace') as f:
        for line in f:
            parts = line.split()
            if not parts: continue
            tok = parts[0]
            if tok == 'v':
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif tok == 'vt':
                texcoords.append((float(parts[1]), float(parts[2])))
            elif tok == 'usemtl':
                flush()
                current_mat, current_faces = (parts[1] if len(parts) > 1 else '__no_material__'), []
            elif tok == 'f':
                face = []
                for p in parts[1:]:
                    c = p.split('/')
                    face.append((int(c[0]) - 1,
                                 int(c[1]) - 1 if len(c) > 1 and c[1] else None))
                current_faces.append(face)
    flush()
    return vertices, texcoords, groups

# ── Geometry ───────────────────────────────────────────────────────────────────

def compute_bounds(vertices):
    xs = [v[0] for v in vertices]; ys = [v[1] for v in vertices]; zs = [v[2] for v in vertices]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

def convert_blender_zup(vertices):
    return [(x, z, y) for x, y, z in vertices]

def build_display_list(faces, vertices, texcoords, scale, offset, tex_w, tex_h, flip_winding=False):
    words = []
    ox, oy, oz = offset
    for face in faces:
        if flip_winding and len(face) >= 2:
            face = [face[1], face[0]] + face[2:]
        n = len(face)
        if n == 4:   prim = GL_QUADS
        elif n == 3: prim = GL_TRIANGLES
        else:
            for i in range(1, n - 1):
                words += build_display_list([face[0], face[i], face[i+1]],
                                             vertices, texcoords, scale, offset,
                                             tex_w, tex_h, flip_winding)
            continue
        words.append(pack_cmds(FIFO_BEGIN))
        words.append(struct.pack('<I', prim))
        for vi, vti in face:
            if vti is not None and tex_w and tex_h:
                u, v = texcoords[vti]
                u16 = floattot16(u * tex_w)
                v16 = floattot16((1.0 - v) * tex_h)
                words.append(pack_cmds(FIFO_TEXCOORD))
                words.append(struct.pack('<I', (u16 & 0xFFFF) | ((v16 & 0xFFFF) << 16)))
            vx, vy, vz = vertices[vi]
            sx = (vx - ox) * scale; sy = (vy - oy) * scale; sz = (vz - oz) * scale
            words.append(pack_cmds(FIFO_VERTEX16))
            words.append(struct.pack('<I', (floattov16(sy) << 16) | floattov16(sx)))
            words.append(struct.pack('<I', floattov16(sz)))
    return words

# ── Texture helpers ────────────────────────────────────────────────────────────

def find_texture_size(png_path):
    """Return (w, h) of a PNG using stdlib fallback — no Pillow needed."""
    try:
        with open(png_path, 'rb') as f:
            f.read(16)
            w = struct.unpack('>I', f.read(4))[0]
            h = struct.unpack('>I', f.read(4))[0]
            return w, h
    except Exception:
        return None, None

def nearest_valid_tex_size(n):
    if n is None: return None
    for s in sorted(VALID_TEX_SIZES):
        if s >= n: return s
    return 1024

def words_to_c_array(words):
    hex_vals = [f'0x{struct.unpack("<I", w)[0]:08X}' for w in words]
    return '\n'.join('    ' + ', '.join(hex_vals[i:i+8]) + ','
                     for i in range(0, len(hex_vals), 8))

# ── Main convert ───────────────────────────────────────────────────────────────

def convert(obj_path, output_dir,
            scale=None, target_size=4.0, center=True,
            extra_mapping=None, tiles=None, blender_source=False,
            collision_png=None, collision_palette_path=None,
            collision_out=None, collision_tolerance=10, collision_crop=None):

    obj_path   = os.path.abspath(obj_path)
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    obj_dir   = os.path.dirname(obj_path)
    base_name = sanitize(os.path.splitext(os.path.basename(obj_path))[0])

    # MTL
    mtl_path = None
    with open(obj_path, 'r', errors='replace') as f:
        for line in f:
            parts = line.strip().split()
            if parts and parts[0] == 'mtllib':
                mtl_path = os.path.join(obj_dir, ' '.join(parts[1:]))
                break
    mat_to_tex = parse_mtl(mtl_path, extra_mapping)

    # Geometry
    print(f"Parsing {os.path.basename(obj_path)} ...")
    vertices, texcoords, groups = parse_obj(obj_path)
    print(f"  {len(vertices)} vertices, "
          f"{sum(len(g['faces']) for g in groups)} faces, "
          f"{len(groups)} material groups")

    if blender_source:
        print("  Converting Blender Z-up → NDS Y-up")
        vertices = convert_blender_zup(vertices)

    (xmin, xmax), (ymin, ymax), (zmin, zmax) = compute_bounds(vertices)
    max_dim = max(xmax - xmin, ymax - ymin, zmax - zmin)

    if scale is None:
        scale = (target_size / max_dim) if max_dim > 0 else 1.0
        print(f"  Auto-scale: {scale:.6f}  (target {target_size} NDS units, model {max_dim:.3f})")
    else:
        print(f"  Manual scale: {scale:.6f}")

    if center:
        ox = (xmin + xmax) / 2.0; oy = ymin; oz = (zmin + zmax) / 2.0
    else:
        ox = oy = oz = 0.0
    offset = (ox, oy, oz)
    print(f"  Center offset: ({ox:.3f}, {oy:.3f}, {oz:.3f})")

    # World bounds (used for collision and env header)
    trans_min_x = (xmin - ox) * scale; trans_max_x = (xmax - ox) * scale
    trans_min_z = (zmin - oz) * scale; trans_max_z = (zmax - oz) * scale
    world_offset_x = -trans_min_x
    world_offset_z = -trans_min_z
    world_width    = trans_max_x - trans_min_x
    world_depth    = trans_max_z - trans_min_z

    # Merge material groups by texture
    merged, tex_paths = defaultdict(list), {}
    for g in groups:
        mat, faces = g['material'], g['faces']
        if not faces: continue
        tex_rel = mat_to_tex.get(mat)
        if tex_rel is None:
            print(f"  WARNING: no texture for '{mat}' — rendering without UV")
            tex_key = '__no_texture__'
        else:
            tex_abs = os.path.join(obj_dir, tex_rel)
            tex_key = os.path.basename(tex_rel)
            tex_paths[tex_key] = tex_abs
        merged[tex_key].extend(faces)

    print(f"  Texture groups: {len(merged)}")

    # Build display lists
    dl_groups = []
    for tex_key, faces in merged.items():
        tex_abs = tex_paths.get(tex_key)
        tw, th  = find_texture_size(tex_abs) if tex_abs else (None, None)
        if tw: tw = nearest_valid_tex_size(tw)
        if th: th = nearest_valid_tex_size(th)
        words = build_display_list(faces, vertices, texcoords,
                                    scale, offset, tw, th,
                                    flip_winding=blender_source)
        dl_groups.append((tex_key, words, tw, th))
        print(f"  [{tex_key}] {len(faces)} faces, {tw}x{th}, {len(words)} words")

    # ── Write env header ──────────────────────────────────────────────────────
    header_path   = os.path.join(output_dir, f'{base_name}_env.h')
    tex_list_path = os.path.join(output_dir, f'{base_name}_textures.txt')
    n = len(dl_groups)

    with open(header_path, 'w') as h:
        h.write(f"#pragma once\n"
                f"// Auto-generated by obj2nds_environment.py\n"
                f"// Source: {os.path.basename(obj_path)}\n"
                f"// Scale: {scale:.6f}  Centred: {center}\n"
                f"// DO NOT EDIT — regenerate from source.\n\n"
                f"#include <nds.h>\n\n")

        h.write("// --- World Bounds ---\n")
        if tiles and len(tiles) == 4:
            sx, sz, cols, rows = tiles
            tsz_x = world_width / cols if cols else 0.0
            tsz_z = world_depth / rows if rows else 0.0
            fox = world_offset_x - sx * tsz_x
            foz = world_offset_z - sz * tsz_z
            h.write(f"#define {base_name.upper()}_WORLD_OFFSET_X {fox:.6f}f\n"
                    f"#define {base_name.upper()}_WORLD_OFFSET_Z {foz:.6f}f\n"
                    f"#define {base_name.upper()}_TILE_SIZE_X    {tsz_x:.6f}f\n"
                    f"#define {base_name.upper()}_TILE_SIZE_Z    {tsz_z:.6f}f\n"
                    f"#define {base_name.upper()}_MAP_COLS       {int(cols)}\n"
                    f"#define {base_name.upper()}_MAP_ROWS       {int(rows)}\n")
        else:
            h.write(f"#define {base_name.upper()}_WORLD_OFFSET_X {world_offset_x:.6f}f\n"
                    f"#define {base_name.upper()}_WORLD_OFFSET_Z {world_offset_z:.6f}f\n"
                    f"#define {base_name.upper()}_WORLD_WIDTH    {world_width:.6f}f\n"
                    f"#define {base_name.upper()}_WORLD_DEPTH    {world_depth:.6f}f\n")
        h.write("\n")

        h.write(f"enum {base_name}_TexSlot {{\n")
        for i, (tex_key, _, _, _) in enumerate(dl_groups):
            h.write(f"    {base_name.upper()}_TEX_{sanitize(os.path.splitext(tex_key)[0]).upper()} = {i},\n")
        h.write(f"    {base_name.upper()}_TEX_COUNT = {n}\n}};\n\n")

        for i, (tex_key, words, tw, th) in enumerate(dl_groups):
            h.write(f"// Slot {i}: {tex_key}  ({tw}x{th})\n"
                    f"static const u32 {base_name}_dl_{i}[] = {{\n"
                    f"    {len(words)},\n"
                    f"{words_to_c_array(words)}\n}};\n\n")

        h.write(f"static const int {base_name}_tex_widths[{n}]  = {{\n    "
                + ', '.join(str(tw or 0) for _, _, tw, _ in dl_groups) + "\n};\n")
        h.write(f"static const int {base_name}_tex_heights[{n}] = {{\n    "
                + ', '.join(str(th or 0) for _, _, _, th in dl_groups) + "\n};\n\n")

        h.write(f"inline void Load_{base_name}"
                f"(int ids[{n}], const unsigned int* bitmaps[{n}]) {{\n")
        for i, (tex_key, _, tw, th) in enumerate(dl_groups):
            nw = f"TEXTURE_SIZE_{tw}" if tw else "TEXTURE_SIZE_8"
            nh = f"TEXTURE_SIZE_{th}" if th else "TEXTURE_SIZE_8"
            h.write(f"    glGenTextures(1, &ids[{i}]);\n"
                    f"    glBindTexture(GL_TEXTURE_2D, ids[{i}]);\n"
                    f"    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, {nw}, {nh}, 0,\n"
                    f"        TEXGEN_TEXCOORD | GL_TEXTURE_WRAP_S | GL_TEXTURE_WRAP_T,\n"
                    f"        bitmaps[{i}]);\n")
        h.write("}\n\n")

        h.write(f"inline void Draw_{base_name}(const int ids[{n}]) {{\n")
        for i, (tex_key, _, _, _) in enumerate(dl_groups):
            h.write(f"    glBindTexture(GL_TEXTURE_2D, ids[{i}]);  // {tex_key}\n"
                    f"    glCallList((u32*){base_name}_dl_{i});\n")
        h.write("}\n\n")

        h.write(f"inline void Delete_{base_name}(int ids[{n}]) {{\n"
                f"    glDeleteTextures({n}, ids);\n}}\n")

    print(f"\nWrote: {header_path}")

    # Texture list for GRIT
    with open(tex_list_path, 'w') as t:
        t.write(f"# Textures for {base_name} — run GRIT on each\n\n")
        for i, (tex_key, _, tw, th) in enumerate(dl_groups):
            abs_path = tex_paths.get(tex_key, f"<missing: {tex_key}>")
            t.write(f"# Slot {i}  ({tw}x{th})  var: {sanitize(os.path.splitext(tex_key)[0])}Bitmap\n"
                    f"{abs_path}\n\n")
    print(f"Wrote: {tex_list_path}")

    # ── Collision map (optional) ───────────────────────────────────────────────
    if collision_png:
        collision_png = os.path.abspath(collision_png)

        # Auto-discover palette if not specified
        if not collision_palette_path:
            collision_palette_path = find_collision_palette([
                os.path.dirname(os.path.abspath(__file__)),
                obj_dir,
                output_dir,
            ])
            if collision_palette_path:
                print(f"\n  [COLLISION] Auto-found palette: {collision_palette_path}")
            else:
                print("\n  [COLLISION] ERROR: no collision_palette.json found.")
                print("              Place it next to this script or use --collision-palette.")
                return header_path, tex_list_path

        palette, raw_palette = load_collision_palette(collision_palette_path)
        if palette is None:
            return header_path, tex_list_path

        col_stem     = collision_out or f"{base_name}_collision"
        col_out_path = os.path.join(output_dir, col_stem + '.h')

        print(f"\nGenerating collision map → {col_stem}.h")
        write_collision_header(
            png_path      = collision_png,
            out_path      = col_out_path,
            out_stem      = col_stem,
            palette       = palette,
            raw_palette   = raw_palette,
            world_offset_x= world_offset_x,
            world_offset_z= world_offset_z,
            world_width   = world_width,
            world_depth   = world_depth,
            tolerance     = collision_tolerance,
            crop          = collision_crop,
        )

    # ── Usage summary ─────────────────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  Include in your NDS project:")
    print(f"    #include \"{base_name}_env.h\"")
    for tex_key, _, _, _ in dl_groups:
        print(f"    #include \"{sanitize(os.path.splitext(tex_key)[0])}.h\"")
    if collision_png and collision_out:
        print(f"    #include \"{collision_out}.h\"")

    bn_up = base_name.upper()
    print(f"\n  Init():")
    print(f"    static int {base_name}Ids[{bn_up}_TEX_COUNT];")
    print(f"    const unsigned int* bitmaps[{bn_up}_TEX_COUNT] = {{")
    for tex_key, _, _, _ in dl_groups:
        print(f"        {sanitize(os.path.splitext(tex_key)[0])}Bitmap,")
    print(f"    }};")
    print(f"    Load_{base_name}({base_name}Ids, bitmaps);")
    print(f"\n  Draw(): Draw_{base_name}({base_name}Ids);")
    print(f"  Cleanup(): Delete_{base_name}({base_name}Ids);")
    print(f"{'─'*60}\n")

    return header_path, tex_list_path


# ── CLI ────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description='Convert a multi-texture OBJ to an NDS C header.')
    p.add_argument('input')
    p.add_argument('output_dir')
    p.add_argument('--scale',                type=float, default=None)
    p.add_argument('--target-size',          type=float, default=4.0)
    p.add_argument('--no-center',            action='store_true')
    p.add_argument('--source-blender',       action='store_true')
    p.add_argument('--mapping',              type=str,   default=None)
    p.add_argument('--tiles',                type=float, nargs=4,
                   metavar=('SX','SZ','COLS','ROWS'), default=None)
    p.add_argument('--collision-png',        type=str,   default=None)
    p.add_argument('--collision-palette',    type=str,   default=None)
    p.add_argument('--collision-out',        type=str,   default=None)
    p.add_argument('--collision-tolerance',  type=int,   default=10)
    p.add_argument('--collision-crop',       type=int,   nargs=4,
                   metavar=('X','Y','W','H'), default=None)
    args = p.parse_args()

    extra = None
    if args.mapping:
        with open(args.mapping) as f:
            extra = json.load(f)

    convert(
        obj_path              = args.input,
        output_dir            = args.output_dir,
        scale                 = args.scale,
        target_size           = args.target_size,
        center                = not args.no_center,
        extra_mapping         = extra,
        tiles                 = args.tiles,
        blender_source        = args.source_blender,
        collision_png         = args.collision_png,
        collision_palette_path= args.collision_palette,
        collision_out         = args.collision_out,
        collision_tolerance   = args.collision_tolerance,
        collision_crop        = args.collision_crop,
    )
