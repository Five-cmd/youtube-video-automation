import bpy
import math
import random
import os
import sys

def build_lenz_law_scene(out_file="scratch/blender_lenz_1080x1920.mp4", do_render=True):
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    scene = bpy.context.scene
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 570

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
    # 1. Copper Conduit (Gleaming Metallic Copper)
    mat_copper = bpy.data.materials.new("CopperConduit")
    mat_copper.use_nodes = True
    bs_cp = mat_copper.node_tree.nodes.get("Principled BSDF")
    bs_cp.inputs['Base Color'].default_value = (0.95, 0.45, 0.22, 1.0)
    bs_cp.inputs['Metallic'].default_value = 0.95
    bs_cp.inputs['Roughness'].default_value = 0.18

    # 2. Plastic Pipe (Clear Acrylic with zero raytrace noise)
    mat_plastic = bpy.data.materials.new("PlasticPipe")
    mat_plastic.use_nodes = True
    bs_pl = mat_plastic.node_tree.nodes.get("Principled BSDF")
    bs_pl.inputs['Base Color'].default_value = (0.85, 0.95, 1.0, 1.0)
    bs_pl.inputs['Roughness'].default_value = 0.05
    bs_pl.inputs['Transmission Weight'].default_value = 0.0
    bs_pl.inputs['Alpha'].default_value = 0.35
    bs_pl.inputs['Emission Color'].default_value = (0.2, 0.6, 1.0, 1.0)
    bs_pl.inputs['Emission Strength'].default_value = 0.15

    # 3. Neodymium Magnet - North Pole (Ruby Red Chrome)
    mat_mag_n = bpy.data.materials.new("MagnetNorth")
    mat_mag_n.use_nodes = True
    bs_mn = mat_mag_n.node_tree.nodes.get("Principled BSDF")
    bs_mn.inputs['Base Color'].default_value = (0.95, 0.08, 0.1, 1.0)
    bs_mn.inputs['Metallic'].default_value = 0.85
    bs_mn.inputs['Roughness'].default_value = 0.2

    # 4. Neodymium Magnet - South Pole (Cobalt Blue Chrome)
    mat_mag_s = bpy.data.materials.new("MagnetSouth")
    mat_mag_s.use_nodes = True
    bs_ms = mat_mag_s.node_tree.nodes.get("Principled BSDF")
    bs_ms.inputs['Base Color'].default_value = (0.08, 0.35, 0.95, 1.0)
    bs_ms.inputs['Metallic'].default_value = 0.85
    bs_ms.inputs['Roughness'].default_value = 0.2

    # 5. Swirling Eddy Current Rings (Electric Glowing Cyan)
    mat_eddy = bpy.data.materials.new("EddyCurrents")
    mat_eddy.use_nodes = True
    bs_ed = mat_eddy.node_tree.nodes.get("Principled BSDF")
    bs_ed.inputs['Base Color'].default_value = (0.05, 0.85, 1.0, 1.0)
    bs_ed.inputs['Emission Color'].default_value = (0.0, 0.95, 1.0, 1.0)
    bs_ed.inputs['Emission Strength'].default_value = 4.5

    # 6. Upward Magnetic Repulsion Force Arrow (Glowing Neon Amber/Cyan Brake Vector)
    mat_arrow = bpy.data.materials.new("BrakeArrowMat")
    mat_arrow.use_nodes = True
    bs_ar = mat_arrow.node_tree.nodes.get("Principled BSDF")
    bs_ar.inputs['Base Color'].default_value = (1.0, 0.75, 0.05, 1.0)
    bs_ar.inputs['Emission Color'].default_value = (1.0, 0.8, 0.1, 1.0)
    bs_ar.inputs['Emission Strength'].default_value = 6.0

    # ==========================================
    # GEOMETRY
    # ==========================================
    # Tube parameters
    pipe_r = 0.65
    pipe_h = 5.5
    pipe_thick = 0.12

    # 1. Copper Pipe (Right side, X = 0.85) - TRUE HOLLOW CUTAWAY
    bpy.ops.mesh.primitive_cylinder_add(radius=pipe_r, depth=pipe_h, location=(0.85, 0, 0))
    copper_pipe = bpy.context.active_object
    copper_pipe.name = "CopperPipe"
    copper_pipe.data.materials.append(mat_copper)

    # Hollow out the copper pipe (Inner cylinder difference)
    bpy.ops.mesh.primitive_cylinder_add(radius=pipe_r - pipe_thick, depth=pipe_h + 0.2, location=(0.85, 0, 0))
    inner_c = bpy.context.active_object
    m_hollow = copper_pipe.modifiers.new("Hollow", "BOOLEAN")
    m_hollow.operation = 'DIFFERENCE'
    m_hollow.object = inner_c
    bpy.context.view_layer.objects.active = copper_pipe
    bpy.ops.object.modifier_apply(modifier="Hollow")
    bpy.data.objects.remove(inner_c, do_unlink=True)

    # Cutaway front half so interior is exposed to camera
    bpy.ops.mesh.primitive_cube_add(size=7.0, location=(0.85, -3.5, 0))
    cutter_c = bpy.context.active_object
    m_cut = copper_pipe.modifiers.new("CutFront", "BOOLEAN")
    m_cut.operation = 'DIFFERENCE'
    m_cut.object = cutter_c
    bpy.context.view_layer.objects.active = copper_pipe
    bpy.ops.object.modifier_apply(modifier="CutFront")
    bpy.data.objects.remove(cutter_c, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # 2. Plastic Pipe (Left side, X = -0.85) - HOLLOW TRANSPARENT
    bpy.ops.mesh.primitive_cylinder_add(radius=pipe_r, depth=pipe_h, location=(-0.85, 0, 0))
    plastic_pipe = bpy.context.active_object
    plastic_pipe.name = "PlasticPipe"
    plastic_pipe.data.materials.append(mat_plastic)

    bpy.ops.mesh.primitive_cylinder_add(radius=pipe_r - pipe_thick, depth=pipe_h + 0.2, location=(-0.85, 0, 0))
    inner_p = bpy.context.active_object
    m_p_hollow = plastic_pipe.modifiers.new("HollowP", "BOOLEAN")
    m_p_hollow.operation = 'DIFFERENCE'
    m_p_hollow.object = inner_p
    bpy.context.view_layer.objects.active = plastic_pipe
    bpy.ops.object.modifier_apply(modifier="HollowP")
    bpy.data.objects.remove(inner_p, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # 3. Fast Magnet (In Plastic Pipe)
    # North half
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.35, location=(-0.85, 0, 2.2))
    mag_fast_n = bpy.context.active_object
    mag_fast_n.name = "FastMagN"
    mag_fast_n.data.materials.append(mat_mag_n)
    # South half
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.35, location=(-0.85, 0, 1.85))
    mag_fast_s = bpy.context.active_object
    mag_fast_s.name = "FastMagS"
    mag_fast_s.data.materials.append(mat_mag_s)

    # Parent Fast Magnet
    mag_fast_parent = bpy.data.objects.new("FastMagParent", None)
    mag_fast_parent.location = (-0.85, 0, 2.0)
    scene.collection.objects.link(mag_fast_parent)
    mag_fast_n.parent = mag_fast_parent
    mag_fast_s.parent = mag_fast_parent

    # 4. Slow Levitating Magnet (In Copper Pipe)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.35, location=(0.85, 0, 2.2))
    mag_slow_n = bpy.context.active_object
    mag_slow_n.name = "SlowMagN"
    mag_slow_n.data.materials.append(mat_mag_n)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=0.35, location=(0.85, 0, 1.85))
    mag_slow_s = bpy.context.active_object
    mag_slow_s.name = "SlowMagS"
    mag_slow_s.data.materials.append(mat_mag_s)

    # Parent Slow Magnet
    mag_slow_parent = bpy.data.objects.new("SlowMagParent", None)
    mag_slow_parent.location = (0.85, 0, 2.0)
    scene.collection.objects.link(mag_slow_parent)
    mag_slow_n.parent = mag_slow_parent
    mag_slow_s.parent = mag_slow_parent

    # Visible Upward Magnetic Repulsion Force Arrow (Directly underneath pushing UP!)
    bpy.ops.mesh.primitive_cone_add(radius1=0.22, radius2=0.01, depth=0.45, location=(0.85, 0, 1.45))
    brake_arrow_cone = bpy.context.active_object
    brake_arrow_cone.data.materials.append(mat_arrow)
    brake_arrow_cone.parent = mag_slow_parent

    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.45, location=(0.85, 0, 1.1))
    brake_arrow_stem = bpy.context.active_object
    brake_arrow_stem.data.materials.append(mat_arrow)
    brake_arrow_stem.parent = mag_slow_parent

    # 5. Swirling Eddy Current Rings inside Copper Wall (5 concentric glowing rings around slow magnet)
    eddy_rings = []
    for r_idx in range(-2, 3):
        rz = r_idx * 0.22
        bpy.ops.mesh.primitive_torus_add(major_radius=0.58, minor_radius=0.016, location=(0.85, 0, 2.0 + rz))
        ring = bpy.context.active_object
        ring.name = f"EddyRing_{r_idx}"
        ring.data.materials.append(mat_eddy)
        ring.parent = mag_slow_parent
        eddy_rings.append(ring)

    # ==========================================
    # LIGHTING
    # ==========================================
    key_light = bpy.data.lights.new(name="LenzKey", type='SPOT')
    key_light.energy = 2200
    key_light.spot_size = math.radians(45)
    key_light.spot_blend = 0.25
    key_light.color = (1.0, 0.95, 0.88)
    key_obj = bpy.data.objects.new("LenzKeyObj", key_light)
    key_obj.location = (2.5, -3.5, 2.8)
    key_obj.rotation_euler = (math.radians(65), 0, math.radians(30))
    scene.collection.objects.link(key_obj)

    rim_light = bpy.data.lights.new(name="LenzRim", type='POINT')
    rim_light.energy = 950
    rim_light.color = (0.1, 0.8, 1.0)
    rim_obj = bpy.data.objects.new("LenzRimObj", rim_light)
    rim_obj.location = (-2.5, 2.5, 1.5)
    scene.collection.objects.link(rim_obj)

    fill_light = bpy.data.lights.new(name="LenzFill", type='POINT')
    fill_light.energy = 350
    fill_light.color = (0.7, 0.75, 0.9)
    fill_obj = bpy.data.objects.new("LenzFillObj", fill_light)
    fill_obj.location = (0, -2.5, -1.0)
    scene.collection.objects.link(fill_obj)

    # ==========================================
    # CAMERA (Cinematic Dynamic Angles)
    # ==========================================
    cam_data = bpy.data.cameras.new("LenzCamera")
    cam_data.lens = 28
    cam_obj = bpy.data.objects.new("LenzCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera Animation:
    # Frames 1-120: Side-by-side overview (Plastic vs Copper), both magnets released at Frame 30!
    #   - Fast magnet falls in 20 frames and hits bottom with a clatter
    #   - Slow magnet is gently gliding downward!
    # Frames 120-240: Zoom into the Copper pipe cutaway
    # Frames 240-380: Extreme macro view showing Eddy currents swirling around the magnet, pushing UP
    # Frames 380-570: Magnet emerges smoothly out the bottom like a levitating spaceship
    cam_obj.location = (0.0, -7.5, 0.4)
    cam_obj.rotation_euler = (math.radians(88), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Zoom in to Copper Pipe
    cam_obj.location = (0.85, -3.2, 0.2)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(8))
    cam_obj.keyframe_insert(data_path="location", frame=180)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Extreme Macro on Eddy Currents
    cam_obj.location = (0.85, -2.0, -0.1)
    cam_obj.rotation_euler = (math.radians(90), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=320)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=320)

    # Pull out for bottom exit climax
    cam_obj.location = (0.85, -5.5, -1.2)
    cam_obj.rotation_euler = (math.radians(82), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=440)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=440)

    cam_obj.location = (0.85, -5.0, -1.0)
    cam_obj.rotation_euler = (math.radians(80), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=570)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=570)

    # ==========================================
    # MAGNET & CURRENT ANIMATION
    # ==========================================
    # Fast Magnet (Plastic pipe): Dropped at Frame 30, free falls to -2.3 by Frame 55!
    mag_fast_parent.location = (-0.85, 0, 2.0)
    mag_fast_parent.keyframe_insert(data_path="location", frame=1)
    mag_fast_parent.keyframe_insert(data_path="location", frame=30)

    mag_fast_parent.location = (-0.85, 0, -2.3) # SMACK bottom
    mag_fast_parent.keyframe_insert(data_path="location", frame=55)
    mag_fast_parent.keyframe_insert(data_path="location", frame=570)

    # Slow Magnet (Copper pipe): Dropped at Frame 30, constant slow velocity down to -2.3 by Frame 520!
    mag_slow_parent.location = (0.85, 0, 2.0)
    mag_slow_parent.keyframe_insert(data_path="location", frame=1)
    mag_slow_parent.keyframe_insert(data_path="location", frame=30)

    for f in range(40, 530, 20):
        prog = (f - 30) / 490.0
        cur_z = 2.0 - prog * 4.3
        mag_slow_parent.location = (0.85, 0, cur_z)
        mag_slow_parent.keyframe_insert(data_path="location", frame=f)

    mag_slow_parent.location = (0.85, 0, -2.4)
    mag_slow_parent.keyframe_insert(data_path="location", frame=570)

    # Spin Eddy Current Rings
    for ring_i, ring in enumerate(eddy_rings):
        for f in range(1, 571, 30):
            spin_angle = (f / 24.0) * (4.0 if ring_i % 2 == 0 else -4.0)
            ring.rotation_euler = (0, 0, spin_angle)
            ring.keyframe_insert(data_path="rotation_euler", frame=f)

    # ==========================================
    # RENDER SETTINGS & OUTPUT
    # ==========================================
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
    scene.render.filepath = os.path.abspath(out_file)

    test_frame = None
    if "-f" in sys.argv:
        idx = sys.argv.index("-f")
        if idx + 1 < len(sys.argv):
            test_frame = int(sys.argv[idx + 1])

    if test_frame is not None:
        scene.frame_set(test_frame)
        scene.render.image_settings.file_format = 'PNG'
        test_out = f"scratch/lenz_frame_{test_frame}.png"
        scene.render.filepath = os.path.abspath(test_out)
        print(f"Rendering test frame {test_frame} -> {test_out}...", flush=True)
        bpy.ops.render.render(write_still=True)
        print("Test frame complete!", flush=True)
    elif do_render:
        print(f"Starting EEVEE Next Render (Frames 1 - {scene.frame_end})...", flush=True)
        bpy.ops.render.render(animation=True)
        print("Render complete!", flush=True)

if __name__ == "__main__":
    build_lenz_law_scene()
