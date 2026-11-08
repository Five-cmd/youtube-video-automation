import bpy
import math
import random
import os
import sys

def build_acoustic_levitation_scene(out_file="scratch/blender_acoustic_1080x1920.mp4", do_render=True):
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
        bg_node.inputs[0].default_value = (0.012, 0.015, 0.024, 1.0)
        bg_node.inputs[1].default_value = 0.5

    # ==========================================
    # MATERIALS
    # ==========================================
    # 1. Transducer Metal (Brushed Dark Titanium)
    mat_metal = bpy.data.materials.new("TransducerMetal")
    mat_metal.use_nodes = True
    bs_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    bs_m.inputs['Base Color'].default_value = (0.18, 0.20, 0.24, 1.0)
    bs_m.inputs['Metallic'].default_value = 0.95
    bs_m.inputs['Roughness'].default_value = 0.25

    # 2. Water Droplet (Gleaming Liquid Gems with Specular & Zero Noise)
    mat_water = bpy.data.materials.new("WaterDrop")
    mat_water.use_nodes = True
    bs_w = mat_water.node_tree.nodes.get("Principled BSDF")
    bs_w.inputs['Base Color'].default_value = (0.8, 0.95, 1.0, 1.0)
    bs_w.inputs['Roughness'].default_value = 0.05
    bs_w.inputs['Transmission Weight'].default_value = 0.0
    bs_w.inputs['Alpha'].default_value = 0.7
    bs_w.inputs['Emission Color'].default_value = (0.2, 0.7, 1.0, 1.0)
    bs_w.inputs['Emission Strength'].default_value = 0.4

    # 3. Acoustic Standing Wave Rings (Cyan / Violet Holographic Pressure Nodes)
    mat_node_cyan = bpy.data.materials.new("NodeCyan")
    mat_node_cyan.use_nodes = True
    bs_nc = mat_node_cyan.node_tree.nodes.get("Principled BSDF")
    bs_nc.inputs['Base Color'].default_value = (0.05, 0.85, 1.0, 1.0)
    bs_nc.inputs['Emission Color'].default_value = (0.0, 0.9, 1.0, 1.0)
    bs_nc.inputs['Emission Strength'].default_value = 3.5

    mat_node_violet = bpy.data.materials.new("NodeViolet")
    mat_node_violet.use_nodes = True
    bs_nv = mat_node_violet.node_tree.nodes.get("Principled BSDF")
    bs_nv.inputs['Base Color'].default_value = (0.7, 0.2, 1.0, 1.0)
    bs_nv.inputs['Emission Color'].default_value = (0.75, 0.15, 1.0, 1.0)
    bs_nv.inputs['Emission Strength'].default_value = 3.0

    # 4. Force Vectors: Upward Sound Pressure (Cyan) & Downward Gravity (Red)
    mat_force_up = bpy.data.materials.new("ForceUp")
    mat_force_up.use_nodes = True
    bs_fu = mat_force_up.node_tree.nodes.get("Principled BSDF")
    bs_fu.inputs['Base Color'].default_value = (0.1, 0.9, 1.0, 1.0)
    bs_fu.inputs['Emission Color'].default_value = (0.1, 0.95, 1.0, 1.0)
    bs_fu.inputs['Emission Strength'].default_value = 5.0

    mat_force_down = bpy.data.materials.new("ForceDown")
    mat_force_down.use_nodes = True
    bs_fd = mat_force_down.node_tree.nodes.get("Principled BSDF")
    bs_fd.inputs['Base Color'].default_value = (1.0, 0.2, 0.1, 1.0)
    bs_fd.inputs['Emission Color'].default_value = (1.0, 0.25, 0.1, 1.0)
    bs_fd.inputs['Emission Strength'].default_value = 5.0

    # ==========================================
    # GEOMETRY
    # ==========================================
    # Top Ultrasonic Transducer Emitter
    bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=0.5, location=(0, 0, 2.2))
    top_trans = bpy.context.active_object
    top_trans.name = "TopTransducer"
    top_trans.data.materials.append(mat_metal)

    # Bottom Ultrasonic Transducer Reflector
    bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=0.5, location=(0, 0, -2.2))
    bot_trans = bpy.context.active_object
    bot_trans.name = "BottomTransducer"
    bot_trans.data.materials.append(mat_metal)

    # Floating Water Droplets at 3 Pressure Nodes
    # Node 1 (Z = 0.7), Node 2 (Z = 0.0), Node 3 (Z = -0.7)
    droplets = []
    node_z = [0.75, 0.0, -0.75]
    for idx, z in enumerate(node_z):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(0, 0, z))
        drop = bpy.context.active_object
        drop.name = f"WaterDrop_{idx}"
        drop.data.materials.append(mat_water)
        # Flatten slightly due to acoustic radiation pressure (oblate spheroid)
        drop.scale = (1.15, 1.15, 0.85)
        droplets.append(drop)

    # Visible Force Vectors on Center Drop (Z = 0.0)
    # Upward Acoustic Radiation Pressure Cone (pushing UP)
    bpy.ops.mesh.primitive_cone_add(radius1=0.14, radius2=0.01, depth=0.35, location=(0, 0, -0.42))
    arrow_up = bpy.context.active_object
    arrow_up.name = "ArrowSoundPressure"
    arrow_up.data.materials.append(mat_force_up)
    arrow_up.parent = droplets[1]

    # Downward Gravity Cone (pulling DOWN)
    bpy.ops.mesh.primitive_cone_add(radius1=0.14, radius2=0.01, depth=0.35, location=(0, 0, 0.42))
    arrow_down = bpy.context.active_object
    arrow_down.name = "ArrowGravity"
    arrow_down.rotation_euler = (math.pi, 0, 0)
    arrow_down.data.materials.append(mat_force_down)
    arrow_down.parent = droplets[1]

    # Acoustic Standing Wave Rings (Toruses showing pressure nodes)
    wave_rings = []
    for r_idx in range(-3, 4):
        rz = r_idx * 0.38
        bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.018, location=(0, 0, rz))
        ring = bpy.context.active_object
        ring.name = f"WaveRing_{r_idx}"
        mat = mat_node_cyan if r_idx % 2 == 0 else mat_node_violet
        ring.data.materials.append(mat)
        wave_rings.append(ring)

    # ==========================================
    # LIGHTING
    # ==========================================
    # Key Spot (Highlighting water droplets with liquid caustics)
    key_light = bpy.data.lights.new(name="WaterKey", type='SPOT')
    key_light.energy = 2000
    key_light.spot_size = math.radians(40)
    key_light.spot_blend = 0.3
    key_light.color = (0.9, 0.95, 1.0)
    key_obj = bpy.data.objects.new("WaterKeyObj", key_light)
    key_obj.location = (2.2, -3.2, 2.5)
    key_obj.rotation_euler = (math.radians(65), 0, math.radians(35))
    scene.collection.objects.link(key_obj)

    # Cyan Rim
    rim_light = bpy.data.lights.new(name="RimAcoustic", type='POINT')
    rim_light.energy = 900
    rim_light.color = (0.1, 0.8, 1.0)
    rim_obj = bpy.data.objects.new("RimAcousticObj", rim_light)
    rim_obj.location = (-2.2, 2.5, 1.0)
    scene.collection.objects.link(rim_obj)

    # Violet Fill
    fill_light = bpy.data.lights.new(name="FillViolet", type='POINT')
    fill_light.energy = 400
    fill_light.color = (0.6, 0.2, 0.9)
    fill_obj = bpy.data.objects.new("FillVioletObj", fill_light)
    fill_obj.location = (0, -2.5, -1.0)
    scene.collection.objects.link(fill_obj)

    # ==========================================
    # CAMERA (Cinematic Dynamic Angles)
    # ==========================================
    cam_data = bpy.data.cameras.new("AcousticCamera")
    cam_data.lens = 30
    cam_obj = bpy.data.objects.new("AcousticCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera Animation:
    # Frames 1-120: Overview of apparatus with 3 floating water droplets in mid air
    # Frames 120-220: Swoop in to center droplet (Z=0.0) macro
    # Frames 220-380: Extreme macro showing acoustic waves squeezing the water drop into a floating disc
    # Frames 380-570: Modulating phase, water drops dancing and floating backwards!
    cam_obj.location = (0.0, -6.5, 0.3)
    cam_obj.rotation_euler = (math.radians(88), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Swoop to Center Droplet
    cam_obj.location = (0.7, -2.6, 0.12)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(18))
    cam_obj.keyframe_insert(data_path="location", frame=180)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Extreme Macro
    cam_obj.location = (0.55, -1.8, 0.05)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(20))
    cam_obj.keyframe_insert(data_path="location", frame=320)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=320)

    # Dynamic pull out for dancing motion
    cam_obj.location = (1.2, -5.5, 1.4)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(15))
    cam_obj.keyframe_insert(data_path="location", frame=440)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=440)

    cam_obj.location = (1.4, -5.2, 1.6)
    cam_obj.rotation_euler = (math.radians(70), 0, math.radians(18))
    cam_obj.keyframe_insert(data_path="location", frame=570)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=570)

    # ==========================================
    # DROPLET & WAVE ANIMATION
    # ==========================================
    # Acoustic Pressure Pulsing (Wave Rings expand and contract)
    for f in range(1, 571, 15):
        t = f / 24.0
        pulse = 1.0 + math.sin(t * 12.0) * 0.08
        for ring in wave_rings:
            ring.scale = (pulse, pulse, 1.0)
            ring.keyframe_insert(data_path="scale", frame=f)

        # Droplet gentle bobbing & wobble
        for d_idx, drop in enumerate(droplets):
            base_z = node_z[d_idx]
            # When phase modulates at frames 380-570, drops dance upwards!
            dance_offset = 0.0
            if f > 360:
                dance_offset = math.sin((f - 360) / 25.0 + d_idx) * 0.22

            z_bob = base_z + math.sin(t * 4.0 + d_idx * 1.5) * 0.03 + dance_offset
            drop.location = (0, 0, z_bob)
            drop.keyframe_insert(data_path="location", frame=f)

            # Surface tension deformation
            squish = 1.15 + math.sin(t * 8.0 + d_idx) * 0.08
            drop.scale = (squish, squish, 0.85 / (squish * 0.5))
            drop.keyframe_insert(data_path="scale", frame=f)

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
        test_out = f"scratch/acoustic_frame_{test_frame}.png"
        scene.render.filepath = os.path.abspath(test_out)
        print(f"Rendering test frame {test_frame} -> {test_out}...", flush=True)
        bpy.ops.render.render(write_still=True)
        print("Test frame complete!", flush=True)
    elif do_render:
        print(f"Starting EEVEE Next Render (Frames 1 - {scene.frame_end})...", flush=True)
        bpy.ops.render.render(animation=True)
        print("Render complete!", flush=True)

if __name__ == "__main__":
    build_acoustic_levitation_scene()
