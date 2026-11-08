import bpy
import math
import random
import os

def build_perfect_electron_scene(do_render=True, out_file="scratch/test_electron_cutaway.mp4"):
    # 1. Clean scene
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    scene = bpy.context.scene
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 580

    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    scene.render.use_motion_blur = False
    if hasattr(scene, 'eevee'):
        if hasattr(scene.eevee, 'taa_render_samples'):
            scene.eevee.taa_render_samples = 4

    # Dark studio background
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.01, 0.015, 0.03, 1.0)
        bg_node.inputs[1].default_value = 0.8

    # Materials
    # Outer Rubber Jacket (Dark Charcoal)
    mat_outer = bpy.data.materials.new("OuterJacket")
    mat_outer.use_nodes = True
    bsdf_out = mat_outer.node_tree.nodes.get("Principled BSDF")
    if bsdf_out:
        bsdf_out.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
        bsdf_out.inputs['Roughness'].default_value = 0.7

    # Red Wire Insulation
    mat_red = bpy.data.materials.new("WireRed")
    mat_red.use_nodes = True
    bsdf_r = mat_red.node_tree.nodes.get("Principled BSDF")
    if bsdf_r:
        bsdf_r.inputs['Base Color'].default_value = (0.85, 0.1, 0.08, 1.0)
        bsdf_r.inputs['Roughness'].default_value = 0.35

    # Shiny Metallic Copper
    mat_copper = bpy.data.materials.new("MetallicCopper")
    mat_copper.use_nodes = True
    bsdf_c = mat_copper.node_tree.nodes.get("Principled BSDF")
    if bsdf_c:
        bsdf_c.inputs['Base Color'].default_value = (0.95, 0.45, 0.22, 1.0)
        bsdf_c.inputs['Metallic'].default_value = 0.95
        bsdf_c.inputs['Roughness'].default_value = 0.22

    # Copper Atomic Nucleus (Warm Gold/Amber)
    mat_nucleus = bpy.data.materials.new("CopperNucleus")
    mat_nucleus.use_nodes = True
    bsdf_n = mat_nucleus.node_tree.nodes.get("Principled BSDF")
    if bsdf_n:
        bsdf_n.inputs['Base Color'].default_value = (1.0, 0.55, 0.1, 1.0)
        bsdf_n.inputs['Emission Color'].default_value = (1.0, 0.5, 0.05, 1.0)
        bsdf_n.inputs['Emission Strength'].default_value = 2.0
        bsdf_n.inputs['Roughness'].default_value = 0.3

    # Glowing Cyan Electric Electron (HUGE & BRIGHT)
    mat_elec = bpy.data.materials.new("GlowingElectron")
    mat_elec.use_nodes = True
    bsdf_e = mat_elec.node_tree.nodes.get("Principled BSDF")
    if bsdf_e:
        bsdf_e.inputs['Base Color'].default_value = (0.05, 0.95, 1.0, 1.0)
        bsdf_e.inputs['Emission Color'].default_value = (0.0, 0.9, 1.0, 1.0)
        bsdf_e.inputs['Emission Strength'].default_value = 10.0 # Blazing bright!

    # 1. Outer Cable & Cutaway
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=14.0, location=(0, 0, 0))
    jacket = bpy.context.active_object
    jacket.rotation_euler = (0, math.radians(90), 0)
    jacket.data.materials.append(mat_outer)

    # Cut away top-front half of outer jacket to reveal inside
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.0, 1.0))
    cut_j = bpy.context.active_object
    cut_j.scale = (16.0, 3.0, 3.0)
    bool_j = jacket.modifiers.new(name="CutJacket", type='BOOLEAN')
    bool_j.object = cut_j
    bool_j.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = jacket
    bpy.ops.object.modifier_apply(modifier="CutJacket")
    bpy.data.objects.remove(cut_j, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # 2. Red Insulated Wire Inside
    bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=14.0, location=(0, -0.4, -0.1))
    wire_r = bpy.context.active_object
    wire_r.rotation_euler = (0, math.radians(90), 0)
    wire_r.data.materials.append(mat_red)

    # Cut away section of red wire
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.6, 0.6))
    cut_r = bpy.context.active_object
    cut_r.scale = (16.0, 2.0, 2.0)
    bool_r = wire_r.modifiers.new(name="CutRed", type='BOOLEAN')
    bool_r.object = cut_r
    bool_r.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = wire_r
    bpy.ops.object.modifier_apply(modifier="CutRed")
    bpy.data.objects.remove(cut_r, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # 3. Metallic Copper Wire Core (HALF-CYLINDER CUTAWAY BED)
    # The bottom half forms a shiny metallic copper trough/conduit,
    # top half is OPEN so electrons inside are 100% VISIBLE!
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=14.0, location=(0, -0.4, -0.1))
    copper_core = bpy.context.active_object
    copper_core.rotation_euler = (0, math.radians(90), 0)
    copper_core.data.materials.append(mat_copper)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.4, 0.6))
    cut_c = bpy.context.active_object
    cut_c.scale = (16.0, 2.0, 1.2)
    bool_c = copper_core.modifiers.new(name="CutCopper", type='BOOLEAN')
    bool_c.object = cut_c
    bool_c.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = copper_core
    bpy.ops.object.modifier_apply(modifier="CutCopper")
    bpy.data.objects.remove(cut_c, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # 4. Stationary Copper Nuclei Grid (Orange glowing spheres along track)
    for i in range(12):
        nx = (i / 11.0) * 10.0 - 5.0
        ny = -0.4
        nz = -0.25
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=(nx, ny, nz))
        nuc = bpy.context.active_object
        nuc.data.materials.append(mat_nucleus)
        bpy.ops.object.shade_smooth()

    # 5. Prominent Glowing Cyan Electrons (Floating above copper track inside the wire canal)
    random.seed(42)
    electrons = []
    num_electrons = 24 # Fewer, bigger, punchier so each electron is distinct & prominent!
    for i in range(num_electrons):
        base_x = (i / float(num_electrons)) * 11.0 - 5.5
        base_y = -0.4 + random.uniform(-0.18, 0.18)
        base_z = -0.05 + random.uniform(-0.08, 0.15) # Floating inside the open copper canal

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.13, location=(base_x, base_y, base_z))
        elec = bpy.context.active_object
        elec.name = f"VisElectron_{i}"
        elec.data.materials.append(mat_elec)
        bpy.ops.object.shade_smooth()

        # Keyframe animations:
        # Phase 1: DC Drift (Frames 1 - 250)
        # All electrons slowly drift forward in +X direction
        drift_dist = 2.2
        elec.location = (base_x, base_y, base_z)
        elec.keyframe_insert(data_path="location", frame=1)

        elec.location = (base_x + drift_dist, base_y, base_z)
        elec.keyframe_insert(data_path="location", frame=250)

        # Phase 2: AC Back-and-Forth Rapid Oscillation (Frames 251 - 580)
        freq = 0.85 + random.uniform(-0.05, 0.05)
        amp = 0.35 + random.uniform(-0.05, 0.05)
        phase = random.uniform(0, math.pi * 2)

        for f in range(251, 581, 4):
            t = f - 250
            dx = math.sin(t * freq + phase) * amp
            dy = math.cos(t * freq * 0.7 + phase) * 0.03
            elec.location = (base_x + drift_dist + dx, base_y + dy, base_z)
            elec.keyframe_insert(data_path="location", frame=f)

        electrons.append(elec)

    # 6. Camera Animation - Perfectly focused on the open copper canal & glowing electrons!
    cam_data = bpy.data.cameras.new("HeroCam")
    cam_data.lens = 42
    cam_data.dof.use_dof = False

    cam_obj = bpy.data.objects.new("HeroCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Keyframe 1 (Frame 1): Macro view of cable
    cam_obj.location = (0.0, -8.0, 4.5)
    cam_obj.rotation_euler = (math.radians(65), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Keyframe 2 (Frame 110): Smooth swoop down directly towards cutaway canal
    cam_obj.location = (0.0, -4.5, 2.5)
    cam_obj.rotation_euler = (math.radians(58), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=110)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=110)

    # Keyframe 3 (Frame 220): Direct close-up into the wire core - electrons fill screen!
    cam_obj.location = (0.3, -2.2, 1.2)
    cam_obj.rotation_euler = (math.radians(50), 0, math.radians(-10))
    cam_obj.keyframe_insert(data_path="location", frame=220)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=220)

    # Keyframe 4 (Frame 380): Dramatic angle tracking vibrating AC electrons
    cam_obj.location = (0.6, -1.8, 1.1)
    cam_obj.rotation_euler = (math.radians(44), 0, math.radians(12))
    cam_obj.keyframe_insert(data_path="location", frame=380)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=380)

    # Keyframe 5 (Frame 580): Heroic end perspective
    cam_obj.location = (0.1, -1.7, 1.0)
    cam_obj.rotation_euler = (math.radians(40), 0, math.radians(4))
    cam_obj.keyframe_insert(data_path="location", frame=580)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=580)

    # Lighting
    # Key light
    l1 = bpy.data.lights.new("Key", type='AREA')
    l1.energy = 600
    l1.size = 5.0
    l1.color = (0.5, 0.85, 1.0)
    o1 = bpy.data.objects.new("Key", l1)
    o1.location = (3.0, -4.0, 5.0)
    scene.collection.objects.link(o1)

    # Warm rim light
    l2 = bpy.data.lights.new("Rim", type='POINT')
    l2.energy = 500
    l2.color = (1.0, 0.55, 0.15)
    o2 = bpy.data.objects.new("Rim", l2)
    o2.location = (-4.0, -3.0, 3.0)
    scene.collection.objects.link(o2)

    # Render setup
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    scene.render.filepath = os.path.abspath(out_file)

    if do_render:
        print(f"[BLENDER] Rendering {scene.frame_end} frames to {out_file}...")
        bpy.ops.render.render(animation=True)
        print("[BLENDER] Done!")

if __name__ == "__main__":
    build_perfect_electron_scene()
