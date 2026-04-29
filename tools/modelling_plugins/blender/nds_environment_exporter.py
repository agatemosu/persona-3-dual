"""
NDS Environment Exporter for Blender
Author: Taha Rashid / Persona 3 Dual project
Version: 2.1.0  |  Blender 3.x / 4.x

Exports a scene to NDS display list + optional collision map.
Collision settings live on the Scene (persist with .blend file).
Palette editing syncs with the shared collision_palette.json.
No non-standard packages required — collision handled by obj2nds_environment.py.
"""

bl_info = {
    "name": "NDS Environment Exporter",
    "author": "Taha Rashid",
    "version": (2, 1, 0),
    "blender": (3, 0, 0),
    "location": "File > Export > NDS Environment (.h) | Sidebar (N) > NDS",
    "description": "Exports scene to NDS display list with integrated collision map.",
    "category": "Import-Export",
}

import bpy, os, re, subprocess, sys, shutil, json
from bpy.props import (StringProperty, FloatProperty, BoolProperty,
                       EnumProperty, IntProperty, CollectionProperty,
                       FloatVectorProperty, PointerProperty)
from bpy_extras.io_utils import ExportHelper

# ── Helpers ────────────────────────────────────────────────────────────────────

def sanitize(name):
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def find_image_for_material(mat):
    if mat is None or not mat.use_nodes: return None
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image:
            return node.image
    return None

def get_mesh_objects(context, selection_only):
    src = context.selected_objects if selection_only else context.scene.objects
    return [o for o in src if o.type == 'MESH']

def save_image_to_png(img, path):
    """Save image to disk, bypassing Filmic/AgX color grading."""
    try:
        # Temporarily hijack the filepath to save out the raw data
        old_path = img.filepath_raw
        img.filepath_raw = path
        
        # .save() writes the exact pixel values without View Transforms
        img.save()
        
        img.filepath_raw = old_path
        return True
    except Exception as e:
        print(f"[NDS] save_image_to_png failed: {e}")
        return False

# ── Palette helpers ────────────────────────────────────────────────────────────

def load_palette_from_disk(prefs):
    path = bpy.path.abspath(prefs.palette_file)
    if not path or not os.path.exists(path): return False
    try:
        with open(path, 'r') as f: data = json.load(f)
        prefs.collision_palette.clear()
        for name, info in data.items():
            item          = prefs.collision_palette.add()
            item.name     = name
            item.state_id = info['id']
            item.color    = tuple(v / 255.0 for v in info['rgb'])
        return True
    except Exception: return False

def save_palette_to_disk(prefs):
    path = bpy.path.abspath(prefs.palette_file)
    if not path: return False
    data = {item.name: {"rgb": [int(item.color[i] * 255) for i in range(3)],
                        "id": item.state_id}
            for item in prefs.collision_palette}
    try:
        with open(path, 'w') as f: json.dump(data, f, indent=4)
        return True
    except Exception: return False

# ── PropertyGroups ─────────────────────────────────────────────────────────────

class NDSCollisionColor(bpy.types.PropertyGroup):
    name:     StringProperty(name="Name", default="New State")
    color:    FloatVectorProperty(name="Color", subtype='COLOR',
                                  default=(1.0, 0.0, 0.0), min=0.0, max=1.0)
    state_id: IntProperty(name="ID", default=1, min=0)


def _collision_image_items(self, context):
    """Items callback for EnumProperty — signature MUST be (self, context)."""
    items = [('__NONE__', '-- None --', 'No collision map')]
    for img in bpy.data.images:
        items.append((img.name, img.name, ''))
    return items


class NDS_CollisionSettings(bpy.types.PropertyGroup):
    """Stored on bpy.types.Scene so settings persist with the .blend file."""
    enabled:      BoolProperty(name="Generate Collision Map", default=False)
    source_image: EnumProperty(name="Texture", items=_collision_image_items)
    output_name:  StringProperty(name="Output Name",
                                  description="Stem for collision .h "
                                              "(default: <model>_collision)",
                                  default="")
    tolerance:    IntProperty(name="Tolerance", default=10, min=0, max=127,
                               description="Color match tolerance (0 = exact)")
    use_crop:     BoolProperty(name="Crop Region", default=False)
    crop_x:       IntProperty(name="X", default=0, min=0)
    crop_y:       IntProperty(name="Y", default=0, min=0)
    crop_w:       IntProperty(name="W", default=64, min=1)
    crop_h:       IntProperty(name="H", default=64, min=1)

# ── Palette operators ──────────────────────────────────────────────────────────

class NDS_OT_LoadPalette(bpy.types.Operator):
    bl_idname    = "nds.load_palette"
    bl_label     = "Load / Sync"
    bl_description = "Pull shared collision_palette.json into Blender"
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        ok = load_palette_from_disk(prefs)
        self.report({'INFO'} if ok else {'ERROR'},
                    "Palette loaded" if ok else "Could not load palette JSON")
        return {'FINISHED'}

class NDS_OT_SavePalette(bpy.types.Operator):
    bl_idname    = "nds.save_palette"
    bl_label     = "Save JSON"
    bl_description = "Push Blender palette to shared collision_palette.json"
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        ok = save_palette_to_disk(prefs)
        self.report({'INFO'} if ok else {'ERROR'},
                    "Palette saved" if ok else "Could not save palette JSON")
        return {'FINISHED'}

class NDS_OT_AddPaletteItem(bpy.types.Operator):
    bl_idname = "nds.add_palette_item"; bl_label = "Add State"
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        item = prefs.collision_palette.add()
        item.name = "New State"; item.state_id = len(prefs.collision_palette)
        prefs.palette_index = len(prefs.collision_palette) - 1
        return {'FINISHED'}

class NDS_OT_RemovePaletteItem(bpy.types.Operator):
    bl_idname = "nds.remove_palette_item"; bl_label = "Remove State"
    def execute(self, context):
        prefs = context.preferences.addons[__name__].preferences
        if prefs.collision_palette:
            prefs.collision_palette.remove(prefs.palette_index)
            prefs.palette_index = max(0, prefs.palette_index - 1)
        return {'FINISHED'}

class NDS_OT_SetBrushColor(bpy.types.Operator):
    bl_idname    = "nds.set_brush_color"
    bl_label     = "Set Brush Color"
    bl_description = "Set active paint brush to this palette color"
    color: FloatVectorProperty(size=3, subtype='COLOR')
    def execute(self, context):
        context.tool_settings.image_paint.brush.color = self.color
        return {'FINISHED'}

# ── UIList ─────────────────────────────────────────────────────────────────────

class NDS_UL_PaletteList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):
        row = layout.row(align=True)
        ts  = context.tool_settings
        has_brush = (hasattr(ts, 'image_paint') and ts.image_paint is not None
                     and getattr(ts.image_paint, 'brush', None) is not None)
        sub = row.row(align=True); sub.enabled = has_brush
        op  = sub.operator("nds.set_brush_color", text="", icon='BRUSH_DATA')
        op.color = item.color
        row.prop(item, "color",    text="")
        row.prop(item, "name",     text="", emboss=False)
        row.prop(item, "state_id", text="ID")

# ── Preferences ────────────────────────────────────────────────────────────────

class NDS_Environment_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    converter_script: StringProperty(
        name="Build Script",
        description="Absolute path to nds_build_environment.py",
        default="", subtype='FILE_PATH')
    mapping_file: StringProperty(
        name="Material Mapping JSON",
        description="Optional: maps material names to PNG paths",
        default="", subtype='FILE_PATH')
    palette_file: StringProperty(
        name="Palette JSON",
        description="Absolute path to collision_palette.json",
        default="", subtype='FILE_PATH')

    collision_palette: CollectionProperty(type=NDSCollisionColor)
    palette_index:     IntProperty(default=0)

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Paths", icon='FILE_FOLDER')
        box.prop(self, "converter_script")
        box.prop(self, "mapping_file")
        box = layout.box()
        box.label(text="Shared Palette", icon='COLOR')
        box.prop(self, "palette_file")
        if not self.converter_script:
            layout.label(text="Set build script path to enable export!", icon='ERROR')

# ── Sidebar ────────────────────────────────────────────────────────────────────

def _draw_sidebar(self, context):
    layout = self.layout
    prefs  = context.preferences.addons[__name__].preferences
    cs     = context.scene.nds_collision

    # Palette
    box = layout.box()
    box.label(text="Collision Palette", icon='COLOR')
    palette_ok = (prefs.palette_file and
                  os.path.exists(bpy.path.abspath(prefs.palette_file)))
    if not palette_ok:
        box.label(text="Set palette path in Preferences", icon='ERROR')
    else:
        row = box.row(align=True)
        row.operator("nds.load_palette", icon='FILE_REFRESH')
        row.operator("nds.save_palette", icon='FILE_TICK')
        box.template_list("NDS_UL_PaletteList", "",
                          prefs, "collision_palette", prefs, "palette_index")
        row = box.row(align=True)
        row.operator("nds.add_palette_item",    icon='ADD')
        row.operator("nds.remove_palette_item", icon='REMOVE')
        box.label(text="Brush icon paints with that color", icon='INFO')

    layout.separator()

    # Collision settings
    box = layout.box()
    box.label(text="Collision Map", icon='SNAP_GRID')
    box.prop(cs, "enabled")
    if cs.enabled:
        inner = box.box()
        inner.prop(cs, "source_image")
        inner.prop(cs, "output_name")
        inner.prop(cs, "tolerance")
        inner.separator()
        inner.prop(cs, "use_crop")
        if cs.use_crop:
            cb = inner.box()
            row = cb.row(); row.prop(cs, "crop_x"); row.prop(cs, "crop_y")
            row = cb.row(); row.prop(cs, "crop_w"); row.prop(cs, "crop_h")
            cb.label(text=f"({cs.crop_x},{cs.crop_y})  {cs.crop_w}x{cs.crop_h} px",
                     icon='INFO')

    layout.separator()
    layout.label(text="File > Export > NDS Environment", icon='EXPORT')


class NDS_PT_Sidebar_Image(bpy.types.Panel):
    bl_space_type = 'IMAGE_EDITOR'; bl_region_type = 'UI'
    bl_category = 'NDS'; bl_label = "NDS Exporter"
    def draw(self, context): _draw_sidebar(self, context)

class NDS_PT_Sidebar_3D(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'; bl_region_type = 'UI'
    bl_category = 'NDS'; bl_label = "NDS Exporter"
    def draw(self, context): _draw_sidebar(self, context)

# ── OBJ export ─────────────────────────────────────────────────────────────────

def export_obj_mtl(mesh_objects, obj_path, depsgraph):
    import bmesh
    obj_dir  = os.path.dirname(obj_path)
    mtl_name = os.path.splitext(os.path.basename(obj_path))[0] + '.mtl'
    mtl_path = os.path.join(obj_dir, mtl_name)
    v_lines, vt_lines, f_groups = [], [], []
    global_v = global_vt = 1
    mat_to_png = {}

    for obj in mesh_objects:
        eval_obj  = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.to_mesh()
        bm = bmesh.new(); bm.from_mesh(eval_mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:]); bm.to_mesh(eval_mesh); bm.free()
        eval_mesh.calc_normals_split()
        uv_layer  = eval_mesh.uv_layers.active
        mat_world = obj.matrix_world
        loop_uvs  = ([uv_layer.data[l.index].uv[:] for l in eval_mesh.loops]
                     if uv_layer else [(0.0, 0.0)] * len(eval_mesh.loops))

        local_vi = {}
        for v in eval_mesh.vertices:
            co = mat_world @ v.co
            v_lines.append(f"v {co.x:.6f} {co.y:.6f} {co.z:.6f}")
            local_vi[v.index] = global_v; global_v += 1

        uv_key_map, local_vti = {}, {}
        for loop in eval_mesh.loops:
            uv  = loop_uvs[loop.index]
            key = (round(uv[0], 5), round(uv[1], 5))
            if key not in uv_key_map:
                vt_lines.append(f"vt {uv[0]:.6f} {uv[1]:.6f}")
                uv_key_map[key] = global_vt; global_vt += 1
            local_vti[loop.index] = uv_key_map[key]

        mat_faces = {}
        for poly in eval_mesh.polygons:
            mi  = poly.material_index
            mat = obj.material_slots[mi].material if mi < len(obj.material_slots) else None
            img = find_image_for_material(mat)
            mat_id = sanitize(mat.name) if mat else '__no_material__'
            if img and mat_id not in mat_to_png:
                try:
                    abs_path = bpy.path.abspath(img.filepath)
                    if not os.path.exists(abs_path) and img.packed_file:
                        png_name = sanitize(img.name)
                        if not png_name.endswith('.png'): png_name += '.png'
                        abs_path = os.path.join(obj_dir, png_name)
                        img.save(filepath=abs_path)
                    mat_to_png[mat_id] = abs_path
                except Exception: pass
            face_str = "f" + "".join(
                f" {local_vi[eval_mesh.loops[li].vertex_index]}/{local_vti[li]}"
                for li in poly.loop_indices)
            mat_faces.setdefault(mat_id, []).append(face_str)

        for mat_id, faces in mat_faces.items():
            f_groups.append((mat_id, faces))
        eval_obj.to_mesh_clear()

    with open(mtl_path, 'w') as mf:
        mf.write("# NDS Environment Exporter\n")
        seen = set()
        for mat_id, _ in f_groups:
            if mat_id in seen: continue
            seen.add(mat_id)
            mf.write(f"\nnewmtl {mat_id}\nNs 1\nKa 1 1 1\nKd 1 1 1\nKs 0 0 0\n")
            if mat_id in mat_to_png:
                png_name = os.path.basename(mat_to_png[mat_id])
                src = mat_to_png[mat_id]; dst = os.path.join(obj_dir, png_name)
                if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
                    shutil.copy2(src, dst)
                mf.write(f"map_Kd {png_name}\n")

    with open(obj_path, 'w') as of:
        of.write(f"# NDS Environment Exporter\nmtllib {mtl_name}\n\n")
        of.write('\n'.join(v_lines) + '\n\n')
        of.write('\n'.join(vt_lines) + '\n\n')
        current_mat = None
        for mat_id, faces in f_groups:
            if mat_id != current_mat:
                of.write(f"\nusemtl {mat_id}\n"); current_mat = mat_id
            of.write('\n'.join(faces) + '\n')

    return mat_to_png

# ── Export operator ─────────────────────────────────────────────────────────────

class NDS_OT_ExportEnvironment(bpy.types.Operator, ExportHelper):
    bl_idname  = "export_scene.nds_environment"
    bl_label   = "Export NDS Environment"
    bl_options = {'PRESET'}

    filename_ext  = ".h"
    filter_glob:   StringProperty(default="*.h", options={'HIDDEN'})
    scale_mode:    EnumProperty(name="Scale Mode",
                                items=[('AUTO', "Auto Size", ""),
                                       ('MANUAL', "Manual Scale", "")],
                                default='AUTO')
    target_size:   FloatProperty(name="Target Size",  default=4.0,   min=0.01)
    scale_factor:  FloatProperty(name="Scale Factor", default=0.054, min=0.0001)
    centre_model:  BoolProperty(name="Centre Model",  default=True)
    selection_only:BoolProperty(name="Selection Only",default=False)
    skip_grit:     BoolProperty(name="Skip GRIT",     default=False)
    grit_flags:    StringProperty(name="GRIT Flags",  default="-ftc -fh -gb -gB16 -pu16")

    def draw(self, context):
        layout = self.layout
        cs = context.scene.nds_collision

        box = layout.box(); box.label(text="Geometry", icon='MESH_DATA')
        box.prop(self, "scale_mode")
        box.prop(self, "target_size" if self.scale_mode == 'AUTO' else "scale_factor")
        box.prop(self, "centre_model"); box.prop(self, "selection_only")

        box = layout.box(); box.label(text="Textures / GRIT", icon='TEXTURE')
        box.prop(self, "skip_grit")
        if not self.skip_grit: box.prop(self, "grit_flags")

        box = layout.box()
        box.label(text="Collision  (configure in NDS sidebar)", icon='SNAP_GRID')
        if cs.enabled and cs.source_image != '__NONE__':
            box.label(text=f"Texture: {cs.source_image}", icon='IMAGE_DATA')
            box.label(text=f"Output:  {cs.output_name.strip() or '<model>_collision'}.h")
            if cs.use_crop:
                box.label(text=f"Crop: ({cs.crop_x},{cs.crop_y}) {cs.crop_w}x{cs.crop_h}px")
        elif cs.enabled:
            box.label(text="No texture selected", icon='ERROR')
        else:
            box.label(text="Disabled", icon='INFO')

    def execute(self, context):
        prefs  = context.preferences.addons[__name__].preferences
        cs     = context.scene.nds_collision
        script = bpy.path.abspath(prefs.converter_script.strip())

        if not os.path.exists(script):
            self.report({'ERROR'}, "Build script not found — check Preferences.")
            return {'CANCELLED'}

        mesh_objects = get_mesh_objects(context, self.selection_only)
        if not mesh_objects:
            self.report({'ERROR'}, "No mesh objects found.")
            return {'CANCELLED'}

        h_path   = self.filepath
        out_dir  = os.path.dirname(h_path)
        base     = os.path.splitext(os.path.basename(h_path))[0]
        if base.endswith('_env'): base = base[:-4]
        obj_path = os.path.join(out_dir, base + '.obj')

        try:
            export_obj_mtl(mesh_objects, obj_path, context.evaluated_depsgraph_get())
        except Exception as e:
            self.report({'ERROR'}, f"OBJ export failed: {e}")
            return {'CANCELLED'}

        # save_palette_to_disk(prefs)

        py  = shutil.which("python3") or shutil.which("python") or "python"
        cmd = [py, script, obj_path, out_dir]

        if self.scale_mode == 'MANUAL': cmd += ['--scale',       str(self.scale_factor)]
        else:                           cmd += ['--target-size',  str(self.target_size)]
        if not self.centre_model: cmd += ['--no-center']
        if self.skip_grit:        cmd += ['--skip-grit']
        elif self.grit_flags:     cmd += ['--grit-flags', self.grit_flags]
        if prefs.mapping_file:    cmd += ['--mapping', bpy.path.abspath(prefs.mapping_file)]
        cmd += ['--source-blender']

        # Collision
        tmp_png = None
        if cs.enabled and cs.source_image != '__NONE__':
            img = bpy.data.images.get(cs.source_image)
            if img:
                tmp_png = os.path.join(out_dir, '__nds_col_src__.png')
                if save_image_to_png(img, tmp_png):
                    col_out = cs.output_name.strip() or f"{base}_collision"
                    cmd += ['--collision-png',       tmp_png,
                            '--collision-out',       col_out,
                            '--collision-tolerance', str(cs.tolerance)]
                    if prefs.palette_file:
                        cmd += ['--collision-palette', bpy.path.abspath(prefs.palette_file)]
                    if cs.use_crop:
                        cmd += ['--collision-crop',
                                str(cs.crop_x), str(cs.crop_y),
                                str(cs.crop_w), str(cs.crop_h)]
                else:
                    self.report({'WARNING'}, "Could not save collision texture.")
                    tmp_png = None
            else:
                self.report({'WARNING'}, f"Image '{cs.source_image}' not found.")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                self.report({'ERROR'}, f"Pipeline failed:\n{result.stderr[-600:]}")
                print("STDERR:", result.stderr)
                return {'CANCELLED'}
            print(result.stdout)
        except subprocess.TimeoutExpired:
            self.report({'ERROR'}, "Pipeline timed out (180s).")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Could not run pipeline: {e}")
            return {'CANCELLED'}
        finally:
            if tmp_png and os.path.exists(tmp_png):
                try: os.remove(tmp_png)
                except Exception: pass

        self.report({'INFO'}, f"Done — {out_dir}")
        return {'FINISHED'}

# ── Registration ───────────────────────────────────────────────────────────────

def menu_func_export(self, context):
    self.layout.operator(NDS_OT_ExportEnvironment.bl_idname,
                         text="NDS Environment (.h)")

classes = (
    NDSCollisionColor,
    NDS_CollisionSettings,
    NDS_UL_PaletteList,
    NDS_OT_LoadPalette,
    NDS_OT_SavePalette,
    NDS_OT_AddPaletteItem,
    NDS_OT_RemovePaletteItem,
    NDS_OT_SetBrushColor,
    NDS_PT_Sidebar_Image,
    NDS_PT_Sidebar_3D,
    NDS_Environment_Preferences,
    NDS_OT_ExportEnvironment,
)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.Scene.nds_collision = PointerProperty(type=NDS_CollisionSettings)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    if hasattr(bpy.types.Scene, 'nds_collision'):
        del bpy.types.Scene.nds_collision
    for cls in reversed(classes): bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
