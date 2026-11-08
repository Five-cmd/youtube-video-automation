import bpy
import math
import random
import os
import sys

def build_pinch_scene(out_file="scratch/blender_pinch_1080x1920.mp4", do_render=True):
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

    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.012, 0.014, 0.024, 1.0)
        bg_node.inputs[1].default_value = 0.55

    # ==========================================
    # MATERIALS
    # ==========================================
    # 1. Aluminum Soda Can (Shiny Red & Silver Printed Aluminum)
    mat_can = bpy.data.materials.new("AluminumCan")
    mat_can.use_nodes = True
    bs_cn = mat_can.node_tree.nodes.get("Principled BSDF")
    bs_cn.inputs['Base Color'].default_value = (0.92, 0.12, 0.15, 1.0) # Vibrant Red Cola Can
    bs_cn.inputs['Metallic'].default_value = 0.95
    bs_cn.inputs['Roughness'].default_value = 0.18

    # 2. Heavy Heavy Copper Pinch Coil (Gleaming Thick Copper Wire)
    mat_coil = bpy.data.materials.new("HeavyPinchCoil")
    mat_coil.use_nodes = True
    bs_cl = mat_coil.node_tree.nodes.get("Principled BSDF")
    bs_cl.inputs['Base Color'].default_value = (0.95, 0.45, 0.2, 1.0)
    bs_cl.inputs['Metallic'].default_value = 0.98
    bs_cl.inputs['Roughness'].default_value = 0.15

    # 3. High-Voltage Spark Gap Arc (Intense White/Cyan Lightning)
    mat_spark = bpy.data.materials.new("PinchSpark")
    mat_spark.use_nodes = True
    bs_sp = mat_spark.node_tree.nodes.get("Principled BSDF")
    bs_sp.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bs_sp.inputs['Emission Color'].default_value = (0.7, 0.95, 1.0, 1.0)
    bs_sp.inputs['Emission Strength'].default_value = 0.0

    # 4. Inward Magnetic Pinch Force Vectors (Glowing Magenta/Violet Plasma Rings)
    mat_flux = bpy.data.materials.new("PinchFlux")
    mat_flux.use_nodes = True
    bs_fx = mat_flux.node_tree.nodes.get("Principled BSDF")
    bs_fx.inputs['Base Color'].default_value = (1.0, 0.1, 0.7, 1.0)
    bs_fx.inputs['Emission Color'].default_value = (1.0, 0.1, 0.8, 1.0)
    bs_fx.inputs['Emission Strength'].default_value = 0.0

    # 5. Laboratory Test Bench
    mat_bench = bpy.data.materials.new("LabBench")
    mat_bench.use_nodes = True
    bs_bn = mat_bench.node_tree.nodes.get("Principled BSDF")
    bs_bn.inputs['Base Color'].default_value = (0.08, 0.09, 0.12, 1.0)
    bs_bn.inputs['Metallic'].default_value = 0.7
    bs_bn.inputs['Roughness'].default_value = 0.35

    # ==========================================
    # GEOMETRY
    # ==========================================
    # Test Bench
    bpy.ops.mesh.primitive_cylinder_add(radius=2.0, depth=0.3, location=(0, 0, -2.1))
    bench = bpy.context.active_object
    bench.data.materials.append(mat_bench)

    # Aluminum Soda Can (Cylinder in the center)
    can_r = 0.65
    can_h = 2.8
    bpy.ops.mesh.primitive_cylinder_add(radius=can_r, depth=can_h, vertices=48, location=(0, 0, -0.4))
    can_obj = bpy.context.active_object
    can_obj.name = "SodaCan"
    can_obj.data.materials.append(mat_can)
    bpy.ops.object.shade_smooth()

    # 3-Turn Heavy Copper Coil surrounding the center waist of the can
    coil_turns = []
    for turn_i in range(-1, 2):
        tz = -0.4 + turn_i * 0.42
        bpy.ops.mesh.primitive_torus_add(major_radius=0.92, minor_radius=0.08, major_segments=48, minor_segments=24, location=(0, 0, tz))
        turn = bpy.context.active_object
        turn.name = f"CoilTurn_{turn_i}"
        turn.data.materials.append(mat_coil)
        bpy.ops.object.shade_smooth()
        coil_turns.append(turn)

    # Spark Gap Electrodes (Two spheres above)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(-0.35, 0, 1.8))
    e1 = bpy.context.active_object
    e1.data.materials.append(mat_coil)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0.35, 0, 1.8))
    e2 = bpy.context.active_object
    e2.data.materials.append(mat_coil)

    # Spark Arc in gap
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.6, location=(0, 0, 1.8))
    spark_arc = bpy.context.active_object
    spark_arc.name = "SparkGapArc"
    spark_arc.rotation_euler = (0, math.pi / 2.0, 0)
    spark_arc.data.materials.append(mat_spark)
    spark_arc.scale = (0.01, 0.01, 0.01)

    # Inward Magnetic Pinch Force Rings (3 glowing magenta rings contracting inward)
    flux_rings = []
    for f_i in range(3):
        fz = -0.4 + (f_i - 1) * 0.35
        bpy.ops.mesh.primitive_torus_add(major_radius=1.1, minor_radius=0.025, location=(0, 0, fz))
        f_ring = bpy.context.active_object
        f_ring.name = f"FluxRing_{f_i}"
        f_ring.data.materials.append(mat_flux)
        flux_rings.append(f_ring)

    # ==========================================
    # LIGHTING
    # ==========================================
    key_light = bpy.data.lights.new(name="PinchKey", type='SPOT')
    key_light.energy = 2200
    key_light.spot_size = math.radians(45)
    key_light.spot_blend = 0.25
    key_light.color = (1.0, 0.95, 0.9)
    key_obj = bpy.data.objects.new("PinchKeyObj", key_light)
    key_obj.location = (2.2, -3.2, 2.6)
    key_obj.rotation_euler = (math.radians(65), 0, math.radians(35))
    scene.collection.objects.link(key_obj)

    # Blinding Spark Discharge Flash Light
    flash_light = bpy.data.lights.new(name="SparkFlashLight", type='POINT')
    flash_light.energy = 0
    flash_light.color = (0.7, 0.9, 1.0)
    flash_obj = bpy.data.objects.new("SparkFlashLightObj", flash_light)
    flash_obj.location = (0, 0, -0.4)
    scene.collection.objects.link(flash_obj)

    rim_light = bpy.data.lights.new(name="PinchRim", type='POINT')
    rim_light.energy = 950
    rim_light.color = (0.2, 0.8, 1.0)
    rim_obj = bpy.data.objects.new("PinchRimObj", rim_light)
    rim_obj.location = (-2.2, 2.5, 1.2)
    scene.collection.objects.link(rim_obj)

    # ==========================================
    # CAMERA (Cinematic Pacing)
    # ==========================================
    cam_data = bpy.data.cameras.new("PinchCamera")
    cam_data.lens = 28
    cam_obj = bpy.data.objects.new("PinchCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera Animation:
    # Frames 1-100: Overview, pristine red soda can inside copper coil, capacitors humming
    # Frames 100-210: Zoom into the gap between can and coil
    # Frames 210-360: THE PINCH! Spark triggers, lightning arcs, magnetic rings crush inward in 100,000 fps slow-mo!
    # Frames 360-570: Pull out showing pinched hourglass can sliced in half!
    cam_obj.location = (0.0, -7.0, 0.2)
    cam_obj.rotation_euler = (math.radians(88), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Macro zoom to coil and can waist
    cam_obj.location = (0.6, -3.2, -0.2)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(16))
    cam_obj.keyframe_insert(data_path="location", frame=180)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Extreme impact hold
    cam_obj.location = (0.45, -2.4, -0.3)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(14))
    cam_obj.keyframe_insert(data_path="location", frame=280)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=280)

    # Pull out for crushed hourglass reveal
    cam_obj.location = (0.8, -6.0, 0.8)
    cam_obj.rotation_euler = (math.radians(78), 0, math.radians(12))
    cam_obj.keyframe_insert(data_path="location", frame=440)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=440)

    cam_obj.location = (0.9, -5.6, 1.0)
    cam_obj.rotation_euler = (math.radians(75), 0, math.radians(14))
    cam_obj.keyframe_insert(data_path="location", frame=570)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=570)

    # ==========================================
    # PINCH & SPARK ANIMATION
    # ==========================================
    # Can stays intact until Frame 220
    can_obj.scale = (1.0, 1.0, 1.0)
    can_obj.keyframe_insert(data_path="scale", frame=1)
    can_obj.keyframe_insert(data_path="scale", frame=219)

    # VIOLENT PINCH at Frame 220-230! Waist crushes down to 18% width (hourglass pinch)
    can_obj.scale = (0.18, 0.18, 0.88)
    can_obj.keyframe_insert(data_path="scale", frame=230)
    can_obj.keyframe_insert(data_path="scale", frame=570)

    # Spark Gap Arc at Frame 220
    spark_arc.scale = (0.01, 0.01, 0.01)
    spark_arc.keyframe_insert(data_path="scale", frame=218)
    spark_arc.scale = (1.2, 1.2, 1.0)
    spark_arc.keyframe_insert(data_path="scale", frame=220)
    spark_arc.scale = (0.01, 0.01, 0.01)
    spark_arc.keyframe_insert(data_path="scale", frame=240)

    # Spark & Flux Emissions
    bs_sp.inputs['Emission Strength'].default_value = 0.0
    bs_sp.inputs['Emission Strength'].keyframe_insert("default_value", frame=218)
    bs_sp.inputs['Emission Strength'].default_value = 16.0
    bs_sp.inputs['Emission Strength'].keyframe_insert("default_value", frame=220)
    bs_sp.inputs['Emission Strength'].default_value = 0.0
    bs_sp.inputs['Emission Strength'].keyframe_insert("default_value", frame=245)

    flash_light.energy = 0
    flash_light.keyframe_insert(data_path="energy", frame=218)
    flash_light.energy = 5500 # Super bright discharge flash!
    flash_light.keyframe_insert(data_path="energy", frame=221)
    flash_light.energy = 0
    flash_light.keyframe_insert(data_path="energy", frame=245)

    # Magnetic Flux Rings contracting violently inward (Pinch force)
    bs_fx.inputs['Emission Strength'].default_value = 0.0
    bs_fx.inputs['Emission Strength'].keyframe_insert("default_value", frame=215)
    bs_fx.inputs['Emission Strength'].default_value = 10.0
    bs_fx.inputs['Emission Strength'].keyframe_insert("default_value", frame=220)
    bs_fx.inputs['Emission Strength'].default_value = 0.0
    bs_fx.inputs['Emission Strength'].keyframe_insert("default_value", frame=280)

    for fr in flux_rings:
        fr.scale = (1.0, 1.0, 1.0)
        fr.keyframe_insert(data_path="scale", frame=215)
        # Contracts tightly onto can waist
        fr.scale = (0.28, 0.28, 1.0)
        fr.keyframe_insert(data_path="scale", frame=226)
        fr.scale = (0.01, 0.01, 1.0)
        fr.keyframe_insert(data_path="scale", frame=280)

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
        test_out = f"scratch/pinch_frame_{test_frame}.png"
        scene.render.filepath = os.path.abspath(test_out)
        print(f"Rendering test frame {test_frame} -> {test_out}...", flush=True)
        bpy.ops.render.render(write_still=True)
        print("Test frame complete!", flush=True)
    elif do_render:
        print(f"Starting EEVEE Next Render (Frames 1 - {scene.frame_end})...", flush=True)
        bpy.ops.render.render(animation=True)
        print("Render complete!", flush=True)

if __name__ == "__main__":
    build_pinch_scene()
