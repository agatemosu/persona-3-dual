#!/usr/bin/env python3
"""
nds_build_environment.py  —  One-command NDS environment build pipeline
For the Persona 3 Dual project.

  1. obj2nds_environment.py  ->  model_env.h + model_textures.txt  [+ collision.h]
  2. GRIT on every texture   ->  texture.h  + texture.s

Usage:
    python nds_build_environment.py input.obj output_dir/
    python nds_build_environment.py input.obj output_dir/ --source-blender
    python nds_build_environment.py input.obj output_dir/ --target-size 4.0
    python nds_build_environment.py input.obj output_dir/ --skip-grit

    # With collision (palette auto-discovered; crop optional):
    python nds_build_environment.py input.obj output_dir/ --collision-png col.png
    python nds_build_environment.py input.obj output_dir/ --collision-png col.png \\
        --collision-out room_col --collision-crop 0 0 44 33
"""

import subprocess, sys, os, re, argparse, shutil

HERE      = os.path.dirname(os.path.abspath(__file__))
CONVERTER = os.path.join(HERE, 'obj2nds_environment.py')


def run(cmd, desc):
    print(f"\n{'─'*60}\n  {desc}\n  $ {' '.join(str(c) for c in cmd)}\n{'─'*60}")
    result = subprocess.run(cmd, text=True)
    if result.returncode != 0:
        print(f"\n[FAIL] {desc}")
        sys.exit(result.returncode)


def find_grit():
    g = shutil.which('grit')
    if g: return g
    for c in ['/opt/devkitpro/tools/bin/grit',
              os.path.expanduser('~/devkitPro/tools/bin/grit'),
              'C:/devkitPro/tools/bin/grit.exe']:
        if os.path.exists(c): return c
    return None


def main():
    p = argparse.ArgumentParser(
        description='NDS environment build pipeline: OBJ -> .h + textures')
    p.add_argument('input')
    p.add_argument('output_dir')
    p.add_argument('--scale',                type=float, default=None)
    p.add_argument('--target-size',          type=float, default=4.0)
    p.add_argument('--no-center',            action='store_true')
    p.add_argument('--source-blender',       action='store_true')
    p.add_argument('--mapping',              type=str, default=None)
    p.add_argument('--tiles',                type=float, nargs=4,
                   metavar=('SX', 'SZ', 'COLS', 'ROWS'), default=None)
    p.add_argument('--skip-grit',            action='store_true')
    p.add_argument('--grit-flags',           type=str,
                   default='-ftc -fh -gb -gB16 -pu16')
    # Collision — passed straight through to obj2nds_environment.py
    p.add_argument('--collision-png',        type=str, default=None,
                   help='Painted collision PNG (one pixel = one tile)')
    p.add_argument('--collision-palette',    type=str, default=None,
                   help='collision_palette.json (auto-discovered if omitted)')
    p.add_argument('--collision-out',        type=str, default=None,
                   help='Output stem for collision header (default: <model>_collision)')
    p.add_argument('--collision-tolerance',  type=int, default=10)
    p.add_argument('--collision-crop',       type=int, nargs=4,
                   metavar=('X', 'Y', 'W', 'H'), default=None)
    args = p.parse_args()

    obj_path   = os.path.abspath(args.input)
    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)
    base_name  = re.sub(r'[^a-zA-Z0-9_]', '_',
                        os.path.splitext(os.path.basename(obj_path))[0])

    # ── Step 1: OBJ → env header (+ optional collision header) ───────────────
    cmd = [sys.executable, CONVERTER, obj_path, output_dir]
    if args.scale is not None: cmd += ['--scale',       str(args.scale)]
    else:                      cmd += ['--target-size', str(args.target_size)]
    if args.no_center:         cmd += ['--no-center']
    if args.source_blender:    cmd += ['--source-blender']
    if args.mapping:           cmd += ['--mapping', args.mapping]
    if args.tiles:             cmd += ['--tiles'] + [str(t) for t in args.tiles]
    if args.collision_png:
        cmd += ['--collision-png',       args.collision_png,
                '--collision-tolerance', str(args.collision_tolerance)]
        if args.collision_palette: cmd += ['--collision-palette', args.collision_palette]
        if args.collision_out:     cmd += ['--collision-out',     args.collision_out]
        if args.collision_crop:    cmd += ['--collision-crop'] + [str(v) for v in args.collision_crop]

    run(cmd, 'OBJ → NDS display list header')

    # ── Step 2: GRIT ─────────────────────────────────────────────────────────
    if args.skip_grit:
        print("\n[SKIP] GRIT (--skip-grit)")
        return

    tex_list = os.path.join(output_dir, f'{base_name}_textures.txt')
    if not os.path.exists(tex_list):
        print(f"\n[WARN] No texture list at {tex_list} — skipping GRIT."); return

    grit = find_grit()
    if not grit:
        print("\n[WARN] grit not found — install devkitPro and add tools/bin to PATH."); return

    flags = args.grit_flags.split()
    pngs  = [l.strip() for l in open(tex_list)
             if l.strip() and not l.startswith('#')]

    for png in pngs:
        if not os.path.exists(png):
            print(f"  [WARN] PNG not found: {png}"); continue
        stem = re.sub(r'[^a-zA-Z0-9_]', '_',
                      os.path.splitext(os.path.basename(png))[0])
        run([grit, png] + flags + ['-o', os.path.join(output_dir, stem)],
            f'GRIT: {os.path.basename(png)} → {stem}.h + {stem}.s')

    col_stem = args.collision_out or (f'{base_name}_collision' if args.collision_png else None)
    print(f"\n{'='*60}\n  BUILD COMPLETE  →  {output_dir}/")
    print(f"    #include \"{base_name}_env.h\"")
    if col_stem: print(f"    #include \"{col_stem}.h\"")
    for png in pngs:
        print(f"    #include \"{re.sub(chr(91) + r'^a-zA-Z0-9_' + chr(93), '_', os.path.splitext(os.path.basename(png))[0])}.h\"")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
