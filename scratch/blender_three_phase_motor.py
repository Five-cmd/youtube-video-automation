import bpy
import math
import random
import os

def build_three_phase_scene(out_file="scratch/blender_three_phase_1080x1920.mp4", do_render=True):
    # Clean
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
    if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
        scene.eevee.taa_render_samples = 4

    # Dark background
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.012, 0.015, 0.025, 1.0)
        bg_node.inputs[1].default_value = 0.55

    # ==========================================
    # MATERIALS
    # ==========================================
    # 1. Stator Outer Steel Housing
    mat_stator = bpy.data.materials.new("StatorSteel")
    mat_stator.use_nodes = True
    bs_s = mat_stator.node_tree.nodes.get("Principled BSDF")
    bs_s.inputs['Base Color'].default_value = (0.08, 0.09, 0.12, 1.0)
    bs_s.inputs['Metallic'].default_value = 0.85
    bs_s.inputs['Roughness'].default_value = 0.35

    # 2. Phase A Coil (Vibrant Red)
    mat_phase_a = bpy.data.materials.new("PhaseA_Red")
    mat_phase_a.use_nodes = True
    bs_a = mat_phase_a.node_tree.nodes.get("Principled BSDF")
    bs_a.inputs['Base Color'].default_value = (0.9, 0.1, 0.08, 1.0)
    bs_a.inputs['Emission Color'].default_value = (1.0, 0.15, 0.1, 1.0)
    bs_a.inputs['Emission Strength'].default_value = 3.5

    # 3. Phase B Coil (Electric Cyan)
    mat_phase_b = bpy.data.materials.new("PhaseB_Cyan")
    mat_phase_b.use_nodes = True
    bs_b = mat_phase_b.node_tree.nodes.get("Principled BSDF")
    bs_b.inputs['Base Color'].default_value = (0.05, 0.85, 1.0, 1.0)
    bs_b.inputs['Emission Color'].default_value = (0.0, 0.9, 1.0, 1.0)
    bs_b.inputs['Emission Strength'].default_value = 3.5

    # 4. Phase C Coil (Luminous Gold / Amber)
    mat_phase_c = bpy.data.materials.new("PhaseC_Gold")
    mat_phase_c.use_nodes = True
    bs_c = mat_phase_c.node_tree.nodes.get("Principled BSDF")
    bs_c.inputs['Base Color'].default_value = (1.0, 0.75, 0.05, 1.0)
    bs_c.inputs['Emission Color'].default_value = (1.0, 0.8, 0.1, 1.0)
    bs_c.inputs['Emission Strength'].default_value = 3.5

    # 5. Rotor (Shiny Copper & Heavy Steel Cylindrical Core)
    mat_rotor = bpy.data.materials.new("RotorCore")
    mat_rotor.use_nodes = True
    bs_r = mat_rotor.node_tree.nodes.get("Principled BSDF")
    bs_r.inputs['Base Color'].default_value = (0.95, 0.45, 0.2, 1.0) # Gleaming Copper
    bs_r.inputs['Metallic'].default_value = 0.95
    bs_r.inputs['Roughness'].default_value = 0.18

    # 6. Central Steel Shaft
    mat_shaft = bpy.data.materials.new("ShaftSteel")
    mat_shaft.use_nodes = True
    bs_sh = mat_shaft.node_tree.nodes.get("Principled BSDF")
    bs_sh.inputs['Base Color'].default_value = (0.7, 0.75, 0.8, 1.0)
    bs_sh.inputs['Metallic'].default_value = 0.98
    bs_sh.inputs['Roughness'].default_value = 0.15

    # 7. Rotating Magnetic Field Vortex (Glowing Cyan/Purple Energy Swirl)
    mat_vortex = bpy.data.materials.new("MagneticVortex")
    mat_vortex.use_nodes = True
    bs_vx = mat_vortex.node_tree.nodes.get("Principled BSDF")
    bs_vx.inputs['Base Color'].default_value = (0.2, 0.9, 1.0, 1.0)
    bs_vx.inputs['Emission Color'].default_value = (0.0, 0.95, 1.0, 1.0)
    bs_vx.inputs['Emission Strength'].default_value = 7.0

    # ==========================================
    # 3D MODEL: 3-PHASE STATOR RING & 6 COILS
    # ==========================================
    # Outer Stator Ring (Radius 2.6, Depth 2.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=2.6, depth=2.0, location=(0, 0, 0))
    stator_ring = bpy.context.active_object
    stator_ring.data.materials.append(mat_stator)

    # Hollow out stator center (Radius 2.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=2.05, depth=2.2, location=(0, 0, 0))
    hollow_c = bpy.context.active_object
    m_h = stator_ring.modifiers.new(name="Hollow", type='BOOLEAN')
    m_h.object = hollow_c
    m_h.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = stator_ring
    bpy.ops.object.modifier_apply(modifier="Hollow")
    bpy.data.objects.remove(hollow_c, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # Cutaway front half of stator (Z > 0.3) so inside is 100% visible from camera angle!
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -2.0, 0))
    cut_front = bpy.context.active_object
    cut_front.scale = (6.0, 3.0, 3.0)
    m_cf = stator_ring.modifiers.new(name="CutFront", type='BOOLEAN')
    m_cf.object = cut_front
    m_cf.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = stator_ring
    bpy.ops.object.modifier_apply(modifier="CutFront")
    bpy.data.objects.remove(cut_front, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # 6 Coils arranged at 60-degree increments (3 Phase pairs: A, B, C)
    # Phase A: 0° & 180° (Red)
    # Phase B: 120° & 300° (Cyan)
    # Phase C: 240° & 60° (Gold)
    coil_configs = [
        (0, mat_phase_a, "Coil_A1"),
        (60, mat_phase_c, "Coil_C1"),
        (120, mat_phase_b, "Coil_B1"),
        (180, mat_phase_a, "Coil_A2"),
        (240, mat_phase_c, "Coil_C2"),
        (300, mat_phase_b, "Coil_B2"),
    ]

    for angle_deg, mat, c_name in coil_configs:
        rad = math.radians(angle_deg)
        cx = math.cos(rad) * 1.95
        cy = math.sin(rad) * 1.95
        bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.9, location=(cx, cy, 0))
        coil_obj = bpy.context.active_object
        coil_obj.name = c_name
        coil_obj.rotation_euler = (0, 0, rad + math.radians(90))
        coil_obj.data.materials.append(mat)
        bpy.ops.object.shade_smooth()

    # ==========================================
    # CENTRAL ROTOR (Spins freely with ZERO physical contact!)
    # ==========================================
    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=1.6, location=(0, 0, 0))
    rotor = bpy.context.active_object
    rotor.name = "Rotor"
    rotor.data.materials.append(mat_rotor)
    bpy.ops.object.shade_smooth()

    # Central Steel Shaft (Long axle)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=4.5, location=(0, 0, 0))
    shaft = bpy.context.active_object
    shaft.name = "Shaft"
    shaft.data.materials.append(mat_shaft)
    bpy.ops.object.shade_smooth()

    # Rotor Copper Bars (Squirrel Cage slats) around rotor
    for i in range(12):
        s_angle = math.radians(i * 30)
        sx = math.cos(s_angle) * 1.08
        sy = math.sin(s_angle) * 1.08
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=1.65, location=(sx, sy, 0))
        bar = bpy.context.active_object
        bar.data.materials.append(mat_phase_c)
        bar.parent = rotor

    # ROTOR ROTATION ANIMATION:
    # 0 - 150: Stationary (idle at 0 RPM)
    rotor.rotation_euler = (0, 0, 0)
    rotor.keyframe_insert(data_path="rotation_euler", frame=1)
    rotor.keyframe_insert(data_path="rotation_euler", frame=150)

    # 151 - 320: 3-Phase power turns on! Rotor accelerates rapidly
    rotor.rotation_euler = (0, 0, math.radians(720)) # 2 full spins
    rotor.keyframe_insert(data_path="rotation_euler", frame=320)

    # 321 - 580: High-speed 3,000 RPM frictionless spin!
    rotor.rotation_euler = (0, 0, math.radians(720 + 2880)) # 8 additional rotations
    rotor.keyframe_insert(data_path="rotation_euler", frame=580)

    # ==========================================
    # ROTATING MAGNETIC TORNADO (Glowing vortex rings swirling around rotor!)
    # ==========================================
    vortex_arcs = []
    for v_idx in range(6):
        v_angle = math.radians(v_idx * 60)
        vx = math.cos(v_angle) * 1.55
        vy = math.sin(v_angle) * 1.55
        bpy.ops.mesh.primitive_torus_add(major_radius=0.35, minor_radius=0.04, location=(vx, vy, (v_idx % 3) * 0.3 - 0.3))
        arc = bpy.context.active_object
        arc.name = f"VortexArc_{v_idx}"
        arc.data.materials.append(mat_vortex)
        bpy.ops.object.shade_smooth()

        # Magnetic Vortex Rotation:
        # Starts active from frame 140 onwards
        for f in range(140, 581, 15):
            t = (f - 140) / 10.0
            cur_ang = v_angle + t * 2.5
            arc.location = (math.cos(cur_ang) * 1.55, math.sin(cur_ang) * 1.55, math.sin(t + v_idx) * 0.25)
            arc.rotation_euler = (0, 0, cur_ang)
            arc.keyframe_insert(data_path="location", frame=f)
            arc.keyframe_insert(data_path="rotation_euler", frame=f)
        vortex_arcs.append(arc)

    # ==========================================
    # CAMERA ANIMATION (Dynamic Zack D. Swoop & Heroic Spin)
    # ==========================================
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 38
    cam_data.dof.use_dof = False

    cam = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    # Shot 1 (Frame 1): Wide 3/4 diagonal showing complete motor casing & stationary rotor
    cam.location = (0.0, -7.2, 5.2)
    cam.rotation_euler = (math.radians(60), 0, 0)
    cam.keyframe_insert(data_path="location", frame=1)
    cam.keyframe_insert(data_path="rotation_euler", frame=1)

    # Shot 2 (Frame 120): Camera swoops smoothly toward the 3-phase coils
    cam.location = (0.0, -5.5, 4.2)
    cam.rotation_euler = (math.radians(56), 0, 0)
    cam.keyframe_insert(data_path="location", frame=120)
    cam.keyframe_insert(data_path="rotation_euler", frame=120)

    # Shot 3 (Frame 240): High-angle look directly into the rotating magnetic vortex!
    cam.location = (1.5, -4.8, 4.0)
    cam.rotation_euler = (math.radians(52), 0, math.radians(-16))
    cam.keyframe_insert(data_path="location", frame=240)
    cam.keyframe_insert(data_path="rotation_euler", frame=240)

    # Shot 4 (Frame 420): Dynamic tracking of the high-speed spinning rotor floating in thin air
    cam.location = (-1.5, -4.8, 4.0)
    cam.rotation_euler = (math.radians(52), 0, math.radians(16))
    cam.keyframe_insert(data_path="location", frame=420)
    cam.keyframe_insert(data_path="rotation_euler", frame=420)

    # Shot 5 (Frame 580): Climax Hero perspective
    cam.location = (0.0, -6.2, 4.6)
    cam.rotation_euler = (math.radians(58), 0, 0)
    cam.keyframe_insert(data_path="location", frame=580)
    cam.keyframe_insert(data_path="rotation_euler", frame=580)

    # Studio Lighting
    l1 = bpy.data.lights.new("Key", type='AREA')
    l1.energy = 550
    l1.size = 5.0
    l1.color = (0.75, 0.9, 1.0)
    o1 = bpy.data.objects.new("Key", l1)
    o1.location = (2.0, -5.0, 5.0)
    scene.collection.objects.link(o1)

    l2 = bpy.data.lights.new("Rim", type='POINT')
    l2.energy = 450
    l2.color = (1.0, 0.5, 0.1)
    o2 = bpy.data.objects.new("Rim", l2)
    o2.location = (-4.0, 3.0, 3.5)
    scene.collection.objects.link(o2)

    # Render config
    out_dir = r"scratch"
    os.makedirs(out_dir, exist_ok=True)
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    scene.render.filepath = os.path.abspath(out_file)

    if do_render:
        print(f"[BLENDER] Rendering {scene.frame_end} frames to {out_file}...")
        bpy.ops.render.render(animation=True)
        print(f"[BLENDER] Render finished successfully! Output: {out_file}")

if __name__ == "__main__":
    build_three_phase_scene()
