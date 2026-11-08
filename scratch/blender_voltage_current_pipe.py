import bpy
import math
import random
import os

def build_voltage_current_scene(out_file="scratch/blender_voltage_current_1080x1920.mp4", do_render=True):
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
    scene.frame_end = 580 # ~24.1s

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
        bg_node.inputs[0].default_value = (0.015, 0.018, 0.03, 1.0)
        bg_node.inputs[1].default_value = 0.55

    # ==========================================
    # MATERIALS
    # ==========================================
    # 1. Transparent Glass Pipe
    mat_pipe = bpy.data.materials.new("GlassPipe")
    mat_pipe.use_nodes = True
    b_pip = mat_pipe.node_tree.nodes.get("Principled BSDF")
    b_pip.inputs['Base Color'].default_value = (0.8, 0.9, 1.0, 1.0)
    b_pip.inputs['Transmission Weight'].default_value = 0.88
    b_pip.inputs['Roughness'].default_value = 0.1
    b_pip.inputs['IOR'].default_value = 1.33

    # 2. Polished Copper Base Cradle
    mat_cradle = bpy.data.materials.new("CopperCradle")
    mat_cradle.use_nodes = True
    b_crd = mat_cradle.node_tree.nodes.get("Principled BSDF")
    b_crd.inputs['Base Color'].default_value = (0.95, 0.45, 0.2, 1.0)
    b_crd.inputs['Metallic'].default_value = 0.95
    b_crd.inputs['Roughness'].default_value = 0.2

    # 3. Gold/Yellow "VOLT" Hydraulic Pusher
    mat_volt = bpy.data.materials.new("GoldVoltPusher")
    mat_volt.use_nodes = True
    b_v = mat_volt.node_tree.nodes.get("Principled BSDF")
    b_v.inputs['Base Color'].default_value = (1.0, 0.8, 0.1, 1.0)
    b_v.inputs['Emission Color'].default_value = (1.0, 0.75, 0.0, 1.0)
    b_v.inputs['Emission Strength'].default_value = 4.0
    b_v.inputs['Metallic'].default_value = 0.8
    b_v.inputs['Roughness'].default_value = 0.2

    # 4. Cyan "CURRENT" Electrons (The flowing army of charge)
    mat_current = bpy.data.materials.new("CyanCurrent")
    mat_current.use_nodes = True
    b_cur = mat_current.node_tree.nodes.get("Principled BSDF")
    b_cur.inputs['Base Color'].default_value = (0.05, 0.95, 1.0, 1.0)
    b_cur.inputs['Emission Color'].default_value = (0.0, 0.95, 1.0, 1.0)
    b_cur.inputs['Emission Strength'].default_value = 8.0

    # 5. Red/Steel "OHM" Resistance Clamp
    mat_ohm = bpy.data.materials.new("RedOhmClamp")
    mat_ohm.use_nodes = True
    b_o = mat_ohm.node_tree.nodes.get("Principled BSDF")
    b_o.inputs['Base Color'].default_value = (0.9, 0.15, 0.15, 1.0)
    b_o.inputs['Metallic'].default_value = 0.7
    b_o.inputs['Roughness'].default_value = 0.3

    # ==========================================
    # 3D MODEL: TRANSPARENT PIPE & HYDRAULIC CONDUIT
    # ==========================================
    # Main Polished Conduit running along X from -8 to +8 (radius 0.95)
    # SLICED OPEN ON TOP (Trough Cutaway) so all electrons & pistons are 100% UNMISTAKABLY VISIBLE!
    bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=16.0, location=(0, 0, 0))
    pipe = bpy.context.active_object
    pipe.rotation_euler = (0, math.radians(90), 0)
    pipe.data.materials.append(mat_cradle) # Metallic copper/chrome conduit

    # Boolean: Slice off top half (Z > 0.1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.75))
    cut_top = bpy.context.active_object
    cut_top.scale = (18.0, 3.0, 1.3)
    mod_c = pipe.modifiers.new(name="CutTop", type='BOOLEAN')
    mod_c.object = cut_top
    mod_c.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = pipe
    bpy.ops.object.modifier_apply(modifier="CutTop")
    bpy.data.objects.remove(cut_top, do_unlink=True)
    bpy.ops.object.shade_smooth()

    # Copper Ring Collars at ends & middle for tactile mechanical realism
    collars = [-7.0, -2.5, 2.5, 7.0]
    for cx in collars:
        bpy.ops.mesh.primitive_torus_add(major_radius=1.05, minor_radius=0.12, location=(cx, 0, 0))
        col = bpy.context.active_object
        col.rotation_euler = (0, math.radians(90), 0)
        col.data.materials.append(mat_cradle)
        bpy.ops.object.shade_smooth()

    # ==========================================
    # "VOLT" THE PUSHER (Heavy glowing hydraulic ram on the left)
    # ==========================================
    bpy.ops.mesh.primitive_cylinder_add(radius=0.88, depth=2.0, location=(-6.5, 0, 0))
    volt_piston = bpy.context.active_object
    volt_piston.name = "VoltPusher"
    volt_piston.rotation_euler = (0, math.radians(90), 0)
    volt_piston.data.materials.append(mat_volt)
    bpy.ops.object.shade_smooth()

    # Volt Piston Animation:
    # 0 - 180 (Intro & Current): Idles on left
    volt_piston.location = (-6.5, 0, 0)
    volt_piston.keyframe_insert(data_path="location", frame=1)
    volt_piston.keyframe_insert(data_path="location", frame=180)

    # 181 - 250 (Voltage Surge!): Slams forward violently with massive force!
    volt_piston.location = (-4.0, 0, 0)
    volt_piston.keyframe_insert(data_path="location", frame=230)

    # 251 - 580: Vibrates with high pressure
    for f in range(250, 581, 10):
        t = f - 250
        dx = math.sin(t * 0.4) * 0.15
        volt_piston.location = (-4.0 + dx, 0, 0)
        volt_piston.keyframe_insert(data_path="location", frame=f)

    # ==========================================
    # "OHM" THE RESISTANCE CLAMP (Constricts the pipe in the center!)
    # ==========================================
    # Top Jaw
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0, 1.8))
    jaw_top = bpy.context.active_object
    jaw_top.scale = (1.5, 1.8, 0.8)
    jaw_top.data.materials.append(mat_ohm)
    bpy.ops.object.shade_smooth()

    # Bottom Jaw
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0, -1.8))
    jaw_bot = bpy.context.active_object
    jaw_bot.scale = (1.5, 1.8, 0.8)
    jaw_bot.data.materials.append(mat_ohm)
    bpy.ops.object.shade_smooth()

    # Clamp Animation:
    # 0 - 320: Jaws are open wide (Z=1.8 and -1.8)
    jaw_top.location = (0.0, 0, 1.8)
    jaw_bot.location = (0.0, 0, -1.8)
    jaw_top.keyframe_insert(data_path="location", frame=1)
    jaw_bot.keyframe_insert(data_path="location", frame=1)
    jaw_top.keyframe_insert(data_path="location", frame=320)
    jaw_bot.keyframe_insert(data_path="location", frame=320)

    # 321 - 380: CLAMP SQUEEZES DOWN TIGHT! Constricting the pipe!
    jaw_top.location = (0.0, 0, 1.05)
    jaw_bot.location = (0.0, 0, -1.05)
    jaw_top.keyframe_insert(data_path="location", frame=360)
    jaw_bot.keyframe_insert(data_path="location", frame=360)
    jaw_top.keyframe_insert(data_path="location", frame=580)
    jaw_bot.keyframe_insert(data_path="location", frame=580)

    # ==========================================
    # "CURRENT" ELECTRONS (Marching through the pipe)
    # ==========================================
    random.seed(888)
    num_charges = 36
    charges = []
    for i in range(num_charges):
        bx = -5.0 + (i / float(num_charges)) * 12.0
        by = random.uniform(-0.45, 0.45)
        bz = random.uniform(-0.45, 0.45)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(bx, by, bz))
        ch = bpy.context.active_object
        ch.name = f"Charge_{i}"
        ch.data.materials.append(mat_current)
        bpy.ops.object.shade_smooth()

        # Phase 1: Calm flow (0 - 180)
        ch.location = (bx, by, bz)
        ch.keyframe_insert(data_path="location", frame=1)
        ch.location = (bx + 2.0, by, bz)
        ch.keyframe_insert(data_path="location", frame=180)

        # Phase 2: Voltage surge (181 - 320): Fast acceleration!
        ch.location = (bx + 5.5, by, bz)
        ch.keyframe_insert(data_path="location", frame=320)

        # Phase 3: Resistance choke (321 - 580):
        # Particles before clamp bunch up, particles through clamp struggle to squeeze!
        if bx < 0:
            # Bunched up before clamp!
            ch.location = (bx + 6.2, by * 0.8, bz * 0.8)
        else:
            # Squeezed narrow jet after clamp
            ch.location = (bx + 7.5, by * 0.3, bz * 0.3)
        ch.keyframe_insert(data_path="location", frame=580)

        charges.append(ch)

    # ==========================================
    # CAMERA ANIMATION (Dynamic Zack D. Flythrough!)
    # ==========================================
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 38
    cam_data.dof.use_dof = False

    cam = bpy.data.objects.new("Cam", cam_data)
    scene.collection.objects.link(cam)
    scene.camera = cam

    # Shot 1 (Frame 1): Wide 3/4 diagonal looking into the cutaway pipe!
    cam.location = (-1.0, -9.5, 6.5)
    cam.rotation_euler = (math.radians(60), math.radians(4), math.radians(-12))
    cam.keyframe_insert(data_path="location", frame=1)
    cam.keyframe_insert(data_path="rotation_euler", frame=1)

    # Shot 2 (Frame 120): Swoop in to focus on the flowing Cyan CURRENT electrons
    cam.location = (1.5, -5.5, 4.0)
    cam.rotation_euler = (math.radians(56), math.radians(3), math.radians(-10))
    cam.keyframe_insert(data_path="location", frame=120)
    cam.keyframe_insert(data_path="rotation_euler", frame=120)

    # Shot 3 (Frame 220): Zoom to the heavy golden VOLT hydraulic ram slamming
    cam.location = (-3.8, -4.8, 3.5)
    cam.rotation_euler = (math.radians(54), math.radians(2), math.radians(12))
    cam.keyframe_insert(data_path="location", frame=220)
    cam.keyframe_insert(data_path="rotation_euler", frame=220)

    # Shot 4 (Frame 360): Dramatic focus on the red OHM clamp constricting the pipe!
    cam.location = (0.0, -4.2, 3.2)
    cam.rotation_euler = (math.radians(50), 0, 0)
    cam.keyframe_insert(data_path="location", frame=360)
    cam.keyframe_insert(data_path="rotation_euler", frame=360)

    # Shot 5 (Frame 580): Hero overview showing the entire Ohm's law interaction!
    cam.location = (0.0, -7.5, 5.2)
    cam.rotation_euler = (math.radians(56), 0, math.radians(-6))
    cam.keyframe_insert(data_path="location", frame=580)
    cam.keyframe_insert(data_path="rotation_euler", frame=580)

    # Studio Lights
    l1 = bpy.data.lights.new("Key", type='AREA')
    l1.energy = 550
    l1.size = 5.0
    l1.color = (0.8, 0.9, 1.0)
    o1 = bpy.data.objects.new("Key", l1)
    o1.location = (2.0, -6.0, 6.5)
    scene.collection.objects.link(o1)

    l2 = bpy.data.lights.new("Rim", type='POINT')
    l2.energy = 450
    l2.color = (1.0, 0.6, 0.1)
    o2 = bpy.data.objects.new("Rim", l2)
    o2.location = (-5.0, 4.0, 4.0)
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
    build_voltage_current_scene()
