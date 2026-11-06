import bpy
import math
import random
import os

def build_cable_zoom_scene():
    # 1. Clean scene
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    scene = bpy.context.scene

    # 1080x1920 9:16 vertical (Shorts format)
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 560 # 23.3 seconds at 24 fps

    # EEVEE Next Engine
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    if hasattr(scene, 'eevee'):
        if hasattr(scene.eevee, 'taa_render_samples'):
            scene.eevee.taa_render_samples = 12
        if hasattr(scene.eevee, 'use_motion_blur'):
            scene.eevee.use_motion_blur = True

    # Dark background
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.005, 0.008, 0.015, 1.0)
        bg_node.inputs[1].default_value = 0.5

    # ==========================================
    # 2. Materials
    # ==========================================
    # Outer Rubber Jacket (Black/Dark Slate)
    mat_outer = bpy.data.materials.new("OuterJacket")
    mat_outer.use_nodes = True
    bsdf_out = mat_outer.node_tree.nodes.get("Principled BSDF")
    if bsdf_out:
        bsdf_out.inputs['Base Color'].default_value = (0.03, 0.03, 0.04, 1.0)
        bsdf_out.inputs['Roughness'].default_value = 0.65

    # Red/Brown Inner Wire Insulation
    mat_wire_red = bpy.data.materials.new("WireInsulRed")
    mat_wire_red.use_nodes = True
    bsdf_red = mat_wire_red.node_tree.nodes.get("Principled BSDF")
    if bsdf_red:
        bsdf_red.inputs['Base Color'].default_value = (0.75, 0.12, 0.08, 1.0)
        bsdf_red.inputs['Roughness'].default_value = 0.35

    # Blue Wire Insulation
    mat_wire_blue = bpy.data.materials.new("WireInsulBlue")
    mat_wire_blue.use_nodes = True
    bsdf_blue = mat_wire_blue.node_tree.nodes.get("Principled BSDF")
    if bsdf_blue:
        bsdf_blue.inputs['Base Color'].default_value = (0.08, 0.35, 0.85, 1.0)
        bsdf_blue.inputs['Roughness'].default_value = 0.35

    # Metallic Copper Strands
    mat_copper = bpy.data.materials.new("MetallicCopper")
    mat_copper.use_nodes = True
    bsdf_cop = mat_copper.node_tree.nodes.get("Principled BSDF")
    if bsdf_cop:
        bsdf_cop.inputs['Base Color'].default_value = (0.95, 0.45, 0.22, 1.0)
        bsdf_cop.inputs['Metallic'].default_value = 0.98
        bsdf_cop.inputs['Roughness'].default_value = 0.18

    # Neon Glowing Cyan Electrons
    mat_elec = bpy.data.materials.new("NeonElectron")
    mat_elec.use_nodes = True
    bsdf_el = mat_elec.node_tree.nodes.get("Principled BSDF")
    if bsdf_el:
        bsdf_el.inputs['Base Color'].default_value = (0.0, 0.9, 1.0, 1.0)
        if 'Emission Color' in bsdf_el.inputs:
            bsdf_el.inputs['Emission Color'].default_value = (0.0, 0.95, 1.0, 1.0)
            bsdf_el.inputs['Emission Strength'].default_value = 18.0
        elif 'Emission' in bsdf_el.inputs:
            bsdf_el.inputs['Emission'].default_value = (0.0, 0.95, 1.0, 1.0)

    # Copper Atoms (Orange Lattice Spheres)
    mat_atom = bpy.data.materials.new("CopperAtom")
    mat_atom.use_nodes = True
    bsdf_at = mat_atom.node_tree.nodes.get("Principled BSDF")
    if bsdf_at:
        bsdf_at.inputs['Base Color'].default_value = (0.6, 0.25, 0.1, 1.0)
        bsdf_at.inputs['Roughness'].default_value = 0.4
        bsdf_at.inputs['Metallic'].default_value = 0.5

    # ==========================================
    # 3. Macro Cable Geometry (Outer Jacket & Multi-Wires)
    # ==========================================
    # Outer black jacket cylinder
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=14.0, location=(0, 0, 0))
    outer_cable = bpy.context.active_object
    outer_cable.rotation_euler = (0, math.radians(90), 0)
    outer_cable.data.materials.append(mat_outer)

    # Cut away half of outer jacket along X to reveal inside wires
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -1.0, 1.0))
    cut_outer = bpy.context.active_object
    cut_outer.scale = (16.0, 2.5, 2.5)
    bool_out = outer_cable.modifiers.new(name="CutOuter", type='BOOLEAN')
    bool_out.object = cut_outer
    bool_out.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = outer_cable
    bpy.ops.object.modifier_apply(modifier="CutOuter")
    bpy.data.objects.remove(cut_outer, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # Inner Red and Blue insulated sub-wires
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=15.0, location=(0, -0.4, 0.3))
    wire_red = bpy.context.active_object
    wire_red.rotation_euler = (0, math.radians(90), 0)
    wire_red.data.materials.append(mat_wire_red)
    bpy.ops.object.shade_smooth()

    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=15.0, location=(0, 0.4, -0.3))
    wire_blue = bpy.context.active_object
    wire_blue.rotation_euler = (0, math.radians(90), 0)
    wire_blue.data.materials.append(mat_wire_blue)
    bpy.ops.object.shade_smooth()

    # Stripped Red Wire exposing Twisted Copper Strands bundle!
    # Cutaway section of red wire jacket
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.4, 0.7))
    cut_red = bpy.context.active_object
    cut_red.scale = (10.0, 1.2, 1.2)
    bool_r = wire_red.modifiers.new(name="CutRed", type='BOOLEAN')
    bool_r.object = cut_red
    bool_r.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = wire_red
    bpy.ops.object.modifier_apply(modifier="CutRed")
    bpy.data.objects.remove(cut_red, do_unlink=True)

    # Copper strands bundle inside red wire
    for angle_deg in range(0, 360, 60):
        rad = math.radians(angle_deg)
        sx = 0
        sy = -0.4 + math.cos(rad) * 0.35
        sz = 0.3 + math.sin(rad) * 0.35
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=15.0, location=(sx, sy, sz))
        strand = bpy.context.active_object
        strand.rotation_euler = (0, math.radians(90), 0)
        strand.data.materials.append(mat_copper)
        bpy.ops.object.shade_smooth()

    # Center copper core where microscopic zoom happens
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=15.0, location=(0, -0.4, 0.3))
    center_strand = bpy.context.active_object
    center_strand.rotation_euler = (0, math.radians(90), 0)
    center_strand.data.materials.append(mat_copper)
    bpy.ops.object.shade_smooth()

    # ==========================================
    # 4. Microscopic Atoms and Electrons Lattice
    # ==========================================
    random.seed(999)
    electrons = []
    atoms = []

    # Copper Lattice Atoms (stationary stationary orange spheres)
    for i in range(25):
        ax = (i / 25.0) * 8.0 - 4.0
        ay = -0.4 + random.uniform(-0.3, 0.3)
        az = 0.3 + random.uniform(-0.3, 0.3)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(ax, ay, az))
        atom_obj = bpy.context.active_object
        atom_obj.data.materials.append(mat_atom)
        bpy.ops.object.shade_smooth()
        atoms.append(atom_obj)

    # 60 Glowing Electron Spheres
    num_electrons = 60
    for i in range(num_electrons):
        base_x = (i / num_electrons) * 10.0 - 5.0
        base_y = -0.4 + random.uniform(-0.25, 0.25)
        base_z = 0.3 + random.uniform(-0.25, 0.25)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(base_x, base_y, base_z))
        sphere = bpy.context.active_object
        sphere.name = f"ZoomElectron_{i}"
        sphere.data.materials.append(mat_elec)
        bpy.ops.object.shade_smooth()

        # Keyframing:
        # Phase 1: DC Drift (Frames 1 - 260)
        # Steady drift along +X
        drift_speed = 0.014
        drift_dist = drift_speed * 260

        sphere.location = (base_x, base_y, base_z)
        sphere.keyframe_insert(data_path="location", frame=1)

        sphere.location = (base_x + drift_dist, base_y, base_z)
        sphere.keyframe_insert(data_path="location", frame=260)

        # Phase 2: AC Rapid Vibration (Frames 261 - 560)
        freq = 0.70 + random.uniform(-0.08, 0.08)
        amp = 0.28 + random.uniform(-0.04, 0.04)
        phase_offset = random.uniform(0, math.pi * 2)

        for f in range(261, 561, 3):
            t = (f - 260)
            dx = math.sin(t * freq + phase_offset) * amp
            dy = math.cos(t * freq * 0.8 + phase_offset) * 0.02
            sphere.location = (base_x + drift_dist + dx, base_y + dy, base_z)
            sphere.keyframe_insert(data_path="location", frame=f)

        electrons.append(sphere)

    # ==========================================
    # 5. DYNAMIC ZOOM CAMERA ANIMATION (Signature Zack D. Macro-to-Micro Flythrough!)
    # ==========================================
    cam_data = bpy.data.cameras.new("ZoomCam")
    cam_data.lens = 38
    cam_data.dof.use_dof = True
    cam_data.dof.focus_distance = 3.5
    cam_data.dof.aperture_fstop = 2.8

    cam_obj = bpy.data.objects.new("ZoomCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Keyframe 1 (Frame 1): Wide Macro view of the complete cable
    cam_obj.location = (0.0, -9.5, 5.5)
    cam_obj.rotation_euler = (math.radians(64), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Keyframe 2 (Frame 90): Camera starts plunging inward towards stripped copper section
    cam_obj.location = (0.0, -5.5, 3.2)
    cam_obj.rotation_euler = (math.radians(58), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=90)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=90)

    # Keyframe 3 (Frame 180): Deep Microscopic Zoom inside the copper strand lattice!
    cam_obj.location = (0.2, -2.1, 1.4)
    cam_obj.rotation_euler = (math.radians(50), 0, math.radians(-10))
    cam_obj.keyframe_insert(data_path="location", frame=180)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Keyframe 4 (Frame 360): Orbiting close-up around vibrating electron
    cam_obj.location = (0.5, -1.8, 1.2)
    cam_obj.rotation_euler = (math.radians(45), 0, math.radians(15))
    cam_obj.keyframe_insert(data_path="location", frame=360)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=360)

    # Keyframe 5 (Frame 560): Final heroic perspective
    cam_obj.location = (0.1, -1.6, 1.1)
    cam_obj.rotation_euler = (math.radians(42), 0, math.radians(5))
    cam_obj.keyframe_insert(data_path="location", frame=560)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=560)

    # ==========================================
    # 6. Studio Lighting
    # ==========================================
    light_key = bpy.data.lights.new("KeyLight", type='AREA')
    light_key.energy = 550
    light_key.size = 5.0
    light_key.color = (0.35, 0.85, 1.0)
    key_obj = bpy.data.objects.new("KeyLight", light_key)
    scene.collection.objects.link(key_obj)
    key_obj.location = (3.5, -3.5, 6.0)

    light_rim = bpy.data.lights.new("RimLight", type='POINT')
    light_rim.energy = 400
    light_rim.color = (1.0, 0.5, 0.2)
    rim_obj = bpy.data.objects.new("RimLight", light_rim)
    scene.collection.objects.link(rim_obj)
    rim_obj.location = (-4.0, -3.0, 3.0)

    # Set interpolation to bezier for smooth dramatic camera swoops
    if cam_obj.animation_data and cam_obj.animation_data.action:
        for fcurve in cam_obj.animation_data.action.fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'BEZIER'

    # Render settings
    out_dir = r"scratch"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "blender_cable_zoom_1080x1920.mp4")

    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    scene.render.filepath = os.path.abspath(out_file)

    print(f"[BLENDER] Ready to render Cable Zoom Scene ({scene.frame_end} frames) to {out_file}!")

if __name__ == "__main__":
    build_cable_zoom_scene()
