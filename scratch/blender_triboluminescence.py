import bpy
import math
import random
import os
import sys

def build_tribo_scene(out_file="scratch/blender_tribo_1080x1920.mp4", do_render=True):
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

    # Dark studio background
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.010, 0.012, 0.020, 1.0)
        bg_node.inputs[1].default_value = 0.45

    # ==========================================
    # MATERIALS
    # ==========================================
    # 1. Sugar Candy Crystal (Gleaming Translucent Quartz Crystal)
    mat_crystal = bpy.data.materials.new("SugarCrystal")
    mat_crystal.use_nodes = True
    bs_c = mat_crystal.node_tree.nodes.get("Principled BSDF")
    bs_c.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 1.0)
    bs_c.inputs['Roughness'].default_value = 0.08
    bs_c.inputs['Transmission Weight'].default_value = 0.0
    bs_c.inputs['Alpha'].default_value = 0.75
    bs_c.inputs['Emission Color'].default_value = (0.3, 0.6, 0.9, 1.0)
    bs_c.inputs['Emission Strength'].default_value = 0.25

    # 2. Heavy Steel Pestle / Crusher
    mat_metal = bpy.data.materials.new("CrusherSteel")
    mat_metal.use_nodes = True
    bs_m = mat_metal.node_tree.nodes.get("Principled BSDF")
    bs_m.inputs['Base Color'].default_value = (0.22, 0.24, 0.28, 1.0)
    bs_m.inputs['Metallic'].default_value = 0.95
    bs_m.inputs['Roughness'].default_value = 0.22

    # 3. Lab Anvil / Base Plate
    mat_base = bpy.data.materials.new("AnvilBase")
    mat_base.use_nodes = True
    bs_b = mat_base.node_tree.nodes.get("Principled BSDF")
    bs_b.inputs['Base Color'].default_value = (0.06, 0.07, 0.09, 1.0)
    bs_b.inputs['Metallic'].default_value = 0.8
    bs_b.inputs['Roughness'].default_value = 0.4

    # 4. Triboluminescent Blue Light Flash (Neon Cyan/Blue Emission)
    mat_flash = bpy.data.materials.new("TriboBlueFlash")
    mat_flash.use_nodes = True
    bs_f = mat_flash.node_tree.nodes.get("Principled BSDF")
    bs_f.inputs['Base Color'].default_value = (0.0, 0.8, 1.0, 1.0)
    bs_f.inputs['Emission Color'].default_value = (0.1, 0.75, 1.0, 1.0)
    bs_f.inputs['Emission Strength'].default_value = 0.0

    # 5. High-Voltage Spark Discharge (Intense Electric White/Cyan)
    mat_spark = bpy.data.materials.new("ElectricSpark")
    mat_spark.use_nodes = True
    bs_sp = mat_spark.node_tree.nodes.get("Principled BSDF")
    bs_sp.inputs['Base Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    bs_sp.inputs['Emission Color'].default_value = (0.8, 0.95, 1.0, 1.0)
    bs_sp.inputs['Emission Strength'].default_value = 0.0

    # Electrostatic Positive Charges (+) Glowing Red
    mat_pos = bpy.data.materials.new("ChargePos")
    mat_pos.use_nodes = True
    bs_pos = mat_pos.node_tree.nodes.get("Principled BSDF")
    bs_pos.inputs['Base Color'].default_value = (1.0, 0.1, 0.1, 1.0)
    bs_pos.inputs['Emission Color'].default_value = (1.0, 0.2, 0.2, 1.0)
    bs_pos.inputs['Emission Strength'].default_value = 0.0

    # Electrostatic Negative Charges (-) Glowing Cyan
    mat_neg = bpy.data.materials.new("ChargeNeg")
    mat_neg.use_nodes = True
    bs_neg = mat_neg.node_tree.nodes.get("Principled BSDF")
    bs_neg.inputs['Base Color'].default_value = (0.1, 0.9, 1.0, 1.0)
    bs_neg.inputs['Emission Color'].default_value = (0.2, 0.95, 1.0, 1.0)
    bs_neg.inputs['Emission Strength'].default_value = 0.0

    # 6. Nitrogen Air Molecules (Spheres)
    mat_n2 = bpy.data.materials.new("NitrogenMolecule")
    mat_n2.use_nodes = True
    bs_n2 = mat_n2.node_tree.nodes.get("Principled BSDF")
    bs_n2.inputs['Base Color'].default_value = (0.15, 0.45, 0.9, 1.0)
    bs_n2.inputs['Emission Color'].default_value = (0.2, 0.6, 1.0, 1.0)
    bs_n2.inputs['Emission Strength'].default_value = 0.0

    # ==========================================
    # GEOMETRY
    # ==========================================
    # 1. Base Anvil
    bpy.ops.mesh.primitive_cylinder_add(radius=1.8, depth=0.4, location=(0, 0, -1.2))
    anvil = bpy.context.active_object
    anvil.name = "Anvil"
    anvil.data.materials.append(mat_base)

    # 2. Main Candy / Sugar Crystal Chunk (A faceted gem-like stone)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.75, location=(0, 0, -0.4))
    crystal_main = bpy.context.active_object
    crystal_main.name = "CrystalMain"
    crystal_main.scale = (1.2, 1.0, 0.8)
    crystal_main.data.materials.append(mat_crystal)

    # 3. Crystal Left Fragment (Splits away on crush)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.42, location=(-0.35, 0, -0.4))
    c_left = bpy.context.active_object
    c_left.name = "CrystalLeft"
    c_left.scale = (0.9, 0.8, 0.7)
    c_left.data.materials.append(mat_crystal)

    # 4. Crystal Right Fragment (Splits away on crush)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.42, location=(0.35, 0, -0.4))
    c_right = bpy.context.active_object
    c_right.name = "CrystalRight"
    c_right.scale = (0.9, 0.8, 0.7)
    c_right.data.materials.append(mat_crystal)

    # 5. Heavy Steel Crusher / Piston (Slamming down from top with angled chisel tip)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=2.4, location=(0, 0, 2.5))
    crusher = bpy.context.active_object
    crusher.name = "SteelCrusher"
    crusher.data.materials.append(mat_metal)
    bpy.ops.object.shade_smooth()

    # 6. High-Voltage Fracture Spark Mesh (Jagged discharge in the crack, angled forward)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.9, location=(0, -0.2, -0.25))
    spark_mesh = bpy.context.active_object
    spark_mesh.name = "FractureSpark"
    spark_mesh.rotation_euler = (0, math.pi / 2.0, math.radians(15))
    spark_mesh.data.materials.append(mat_spark)
    spark_mesh.scale = (0.01, 0.01, 0.01)

    # Visible (+) and (-) Charge Indicators on fracture faces
    pos_charges = []
    for p_z in [-0.55, -0.4, -0.25]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(-0.15, 0, p_z))
        pos_s = bpy.context.active_object
        pos_s.data.materials.append(mat_pos)
        pos_s.parent = c_left
        pos_charges.append(pos_s)

    neg_charges = []
    for n_z in [-0.55, -0.4, -0.25]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(0.15, 0, n_z))
        neg_s = bpy.context.active_object
        neg_s.data.materials.append(mat_neg)
        neg_s.parent = c_right
        neg_charges.append(neg_s)

    # 7. Radiant Blue Glow Core (Expanding sphere of light)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, -0.4))
    glow_core = bpy.context.active_object
    glow_core.name = "TriboGlowCore"
    glow_core.data.materials.append(mat_flash)
    glow_core.scale = (0.01, 0.01, 0.01)

    # 8. Surrounding Nitrogen Gas Molecules (Excited into glowing during fracture)
    random.seed(99)
    molecules = []
    for i in range(35):
        rx = random.uniform(-0.8, 0.8)
        ry = random.uniform(-0.6, 0.6)
        rz = random.uniform(-0.7, 0.3)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.03, location=(rx, ry, rz))
        mol = bpy.context.active_object
        mol.name = f"N2_{i}"
        mol.data.materials.append(mat_n2)
        molecules.append(mol)

    # ==========================================
    # LIGHTING
    # ==========================================
    # Key Light (Dull ambient at start, dims to black at crush)
    key_light = bpy.data.lights.new(name="KeyStudio", type='SPOT')
    key_light.energy = 1200
    key_light.spot_size = math.radians(50)
    key_light.color = (0.85, 0.9, 1.0)
    key_obj = bpy.data.objects.new("KeyStudioObj", key_light)
    key_obj.location = (2.0, -3.0, 3.0)
    key_obj.rotation_euler = (math.radians(60), 0, math.radians(30))
    scene.collection.objects.link(key_obj)

    # Dynamic Triboluminescence Point Light (Explodes in brightness inside fracture)
    tribo_light = bpy.data.lights.new(name="TriboBurstLight", type='POINT')
    tribo_light.energy = 0
    tribo_light.color = (0.1, 0.85, 1.0) # Vivid electric cyan-blue
    tribo_obj = bpy.data.objects.new("TriboLightObj", tribo_light)
    tribo_obj.location = (0, -0.4, -0.1) # Positioned in front toward camera!
    scene.collection.objects.link(tribo_obj)

    # Rim Light
    rim_light = bpy.data.lights.new(name="RimStudio", type='POINT')
    rim_light.energy = 400
    rim_light.color = (0.3, 0.4, 0.7)
    rim_obj = bpy.data.objects.new("RimStudioObj", rim_light)
    rim_obj.location = (-2.5, 2.5, 1.5)
    scene.collection.objects.link(rim_obj)

    # ==========================================
    # CAMERA (Cinematic Dynamic Angles)
    # ==========================================
    cam_data = bpy.data.cameras.new("TriboCamera")
    cam_data.lens = 30
    cam_obj = bpy.data.objects.new("TriboCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera Animation:
    # Frames 1-120: Studio overview, candy on anvil, room lights dimming
    # Frames 120-220: Extreme macro zoom as steel crusher approaches candy
    # Frames 220-380: CRUSH IMPACT & SLOW-MOTION BLUE LIGHT EMISSION!
    # Frames 380-570: Flying glowing fractures & spectacular wintergreen fluorescence
    cam_obj.location = (0.0, -5.8, 0.5)
    cam_obj.rotation_euler = (math.radians(82), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Macro zoom to contact point
    cam_obj.location = (0.4, -2.6, -0.15)
    cam_obj.rotation_euler = (math.radians(88), 0, math.radians(12))
    cam_obj.keyframe_insert(data_path="location", frame=180)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Impact hold
    cam_obj.location = (0.2, -2.0, -0.22)
    cam_obj.rotation_euler = (math.radians(88), 0, math.radians(8))
    cam_obj.keyframe_insert(data_path="location", frame=280)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=280)

    # Climax pull back showing full burst
    cam_obj.location = (0.8, -5.2, 1.2)
    cam_obj.rotation_euler = (math.radians(70), 0, math.radians(12))
    cam_obj.keyframe_insert(data_path="location", frame=440)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=440)

    cam_obj.location = (1.0, -4.8, 1.4)
    cam_obj.rotation_euler = (math.radians(68), 0, math.radians(15))
    cam_obj.keyframe_insert(data_path="location", frame=570)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=570)

    # ==========================================
    # ACTION & FRACTURE ANIMATION
    # ==========================================
    # Steel Crusher Descent
    crusher.location = (0, 0, 2.5)
    crusher.keyframe_insert(data_path="location", frame=1)
    crusher.keyframe_insert(data_path="location", frame=100)

    crusher.location = (0, 0, 0.45) # Just above candy
    crusher.keyframe_insert(data_path="location", frame=180)

    # SLAM CRUSH at Frame 220!
    crusher.location = (0, 0, -0.25)
    crusher.keyframe_insert(data_path="location", frame=220)
    crusher.keyframe_insert(data_path="location", frame=570)

    # Crystal Fracture Splitting at Frame 220
    # Left fragment moves left and rolls
    c_left.location = (-0.35, 0, -0.4)
    c_left.rotation_euler = (0, 0, 0)
    c_left.keyframe_insert(data_path="location", frame=219)
    c_left.keyframe_insert(data_path="rotation_euler", frame=219)

    c_left.location = (-0.95, -0.2, -0.48)
    c_left.rotation_euler = (0, math.radians(-35), math.radians(20))
    c_left.keyframe_insert(data_path="location", frame=320)
    c_left.keyframe_insert(data_path="rotation_euler", frame=320)

    # Right fragment moves right and rolls
    c_right.location = (0.35, 0, -0.4)
    c_right.rotation_euler = (0, 0, 0)
    c_right.keyframe_insert(data_path="location", frame=219)
    c_right.keyframe_insert(data_path="rotation_euler", frame=219)

    c_right.location = (0.95, 0.15, -0.48)
    c_right.rotation_euler = (0, math.radians(35), math.radians(-25))
    c_right.keyframe_insert(data_path="location", frame=320)
    c_right.keyframe_insert(data_path="rotation_euler", frame=320)

    # Dim room lights before impact (studio hold, never pitch black!)
    key_light.energy = 1600
    key_light.keyframe_insert(data_path="energy", frame=1)
    key_light.energy = 1200
    key_light.keyframe_insert(data_path="energy", frame=100)
    key_light.energy = 550 # Studio hold!
    key_light.keyframe_insert(data_path="energy", frame=210)
    key_light.energy = 850
    key_light.keyframe_insert(data_path="energy", frame=570)

    # Dynamic Tribo Light Burst (FRAMES 220 - 450)
    tribo_light.energy = 0
    tribo_light.keyframe_insert(data_path="energy", frame=218)

    tribo_light.energy = 8500 # INTENSE ELECTRIC BLUE FLASH!
    tribo_light.keyframe_insert(data_path="energy", frame=222)

    tribo_light.energy = 3200 # Sustained glowing sparks
    tribo_light.keyframe_insert(data_path="energy", frame=280)

    tribo_light.energy = 3000 # Secondary fracture flash!
    tribo_light.keyframe_insert(data_path="energy", frame=340)

    tribo_light.energy = 0
    tribo_light.keyframe_insert(data_path="energy", frame=480)

    # Spark & Glow Core Emission Animation
    bs_sp.inputs['Emission Strength'].default_value = 0.0
    bs_sp.inputs['Emission Strength'].keyframe_insert("default_value", frame=218)
    bs_sp.inputs['Emission Strength'].default_value = 15.0 # Radiant lightning!
    bs_sp.inputs['Emission Strength'].keyframe_insert("default_value", frame=222)
    bs_sp.inputs['Emission Strength'].default_value = 2.0
    bs_sp.inputs['Emission Strength'].keyframe_insert("default_value", frame=360)
    bs_sp.inputs['Emission Strength'].default_value = 0.0
    bs_sp.inputs['Emission Strength'].keyframe_insert("default_value", frame=480)

    bs_f.inputs['Emission Strength'].default_value = 0.0
    bs_f.inputs['Emission Strength'].keyframe_insert("default_value", frame=218)
    bs_f.inputs['Emission Strength'].default_value = 9.0 # Neon blue flash!
    bs_f.inputs['Emission Strength'].keyframe_insert("default_value", frame=224)
    bs_f.inputs['Emission Strength'].default_value = 4.0
    bs_f.inputs['Emission Strength'].keyframe_insert("default_value", frame=360)
    bs_f.inputs['Emission Strength'].default_value = 0.0
    bs_f.inputs['Emission Strength'].keyframe_insert("default_value", frame=480)

    # Animate (+) and (-) charge emissions at fracture (frame 220-320)
    bs_pos.inputs['Emission Strength'].default_value = 0.0
    bs_pos.inputs['Emission Strength'].keyframe_insert("default_value", frame=218)
    bs_pos.inputs['Emission Strength'].default_value = 7.0
    bs_pos.inputs['Emission Strength'].keyframe_insert("default_value", frame=222)
    bs_pos.inputs['Emission Strength'].default_value = 0.0
    bs_pos.inputs['Emission Strength'].keyframe_insert("default_value", frame=340)

    bs_neg.inputs['Emission Strength'].default_value = 0.0
    bs_neg.inputs['Emission Strength'].keyframe_insert("default_value", frame=218)
    bs_neg.inputs['Emission Strength'].default_value = 7.0
    bs_neg.inputs['Emission Strength'].keyframe_insert("default_value", frame=222)
    bs_neg.inputs['Emission Strength'].default_value = 0.0
    bs_neg.inputs['Emission Strength'].keyframe_insert("default_value", frame=340)

    # Scale glow core & spark
    glow_core.scale = (0.01, 0.01, 0.01)
    glow_core.keyframe_insert(data_path="scale", frame=218)
    glow_core.scale = (1.8, 1.4, 1.2)
    glow_core.keyframe_insert(data_path="scale", frame=230)
    glow_core.scale = (0.01, 0.01, 0.01)
    glow_core.keyframe_insert(data_path="scale", frame=460)

    spark_mesh.scale = (0.01, 0.01, 0.01)
    spark_mesh.keyframe_insert(data_path="scale", frame=218)
    spark_mesh.scale = (1.5, 1.5, 1.2)
    spark_mesh.keyframe_insert(data_path="scale", frame=222)
    spark_mesh.scale = (0.01, 0.01, 0.01)
    spark_mesh.keyframe_insert(data_path="scale", frame=380)

    # Animate Nitrogen Gas Molecules lighting up
    bs_n2.inputs['Emission Strength'].default_value = 0.0
    bs_n2.inputs['Emission Strength'].keyframe_insert("default_value", frame=218)
    bs_n2.inputs['Emission Strength'].default_value = 6.0
    bs_n2.inputs['Emission Strength'].keyframe_insert("default_value", frame=225)
    bs_n2.inputs['Emission Strength'].default_value = 0.0
    bs_n2.inputs['Emission Strength'].keyframe_insert("default_value", frame=420)

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
        test_out = f"scratch/tribo_frame_{test_frame}.png"
        scene.render.filepath = os.path.abspath(test_out)
        print(f"Rendering test frame {test_frame} -> {test_out}...", flush=True)
        bpy.ops.render.render(write_still=True)
        print("Test frame complete!", flush=True)
    elif do_render:
        print(f"Starting EEVEE Next Render (Frames 1 - {scene.frame_end})...", flush=True)
        bpy.ops.render.render(animation=True)
        print("Render complete!", flush=True)

if __name__ == "__main__":
    build_tribo_scene()
