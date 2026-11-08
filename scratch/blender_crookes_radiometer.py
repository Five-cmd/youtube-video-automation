import bpy
import math
import random
import os
import sys

def build_crookes_radiometer_scene(out_file="scratch/blender_radiometer_1080x1920.mp4", do_render=True):
    # Clean up existing objects
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

    # Dark cinematic background
    if not scene.world:
        scene.world = bpy.data.worlds.new("World")
    world = scene.world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (0.015, 0.018, 0.028, 1.0)
        bg_node.inputs[1].default_value = 0.6

    # ==========================================
    # MATERIALS
    # ==========================================
    # 1. Glass Bulb (Clean outer contour with sliced open front for crystal clarity)
    mat_glass = bpy.data.materials.new("GlassBulb")
    mat_glass.use_nodes = True
    bs_g = mat_glass.node_tree.nodes.get("Principled BSDF")
    bs_g.inputs['Base Color'].default_value = (0.85, 0.95, 1.0, 0.35)
    bs_g.inputs['Roughness'].default_value = 0.05
    bs_g.inputs['Transmission Weight'].default_value = 0.85
    bs_g.inputs['IOR'].default_value = 1.45

    # 2. Stand & Base (Dark Brushed Mahogany/Bronze)
    mat_stand = bpy.data.materials.new("StandBase")
    mat_stand.use_nodes = True
    bs_st = mat_stand.node_tree.nodes.get("Principled BSDF")
    bs_st.inputs['Base Color'].default_value = (0.12, 0.08, 0.05, 1.0)
    bs_st.inputs['Metallic'].default_value = 0.4
    bs_st.inputs['Roughness'].default_value = 0.4

    # 3. Needle Pivot & Spindle Wire (Polished Chrome Steel)
    mat_chrome = bpy.data.materials.new("NeedleChrome")
    mat_chrome.use_nodes = True
    bs_ch = mat_chrome.node_tree.nodes.get("Principled BSDF")
    bs_ch.inputs['Base Color'].default_value = (0.95, 0.95, 0.98, 1.0)
    bs_ch.inputs['Metallic'].default_value = 0.98
    bs_ch.inputs['Roughness'].default_value = 0.1

    # 4. White / Silver Vane Face (Reflective)
    mat_silver = bpy.data.materials.new("VaneSilver")
    mat_silver.use_nodes = True
    bs_sv = mat_silver.node_tree.nodes.get("Principled BSDF")
    bs_sv.inputs['Base Color'].default_value = (0.92, 0.94, 0.98, 1.0)
    bs_sv.inputs['Metallic'].default_value = 0.9
    bs_sv.inputs['Roughness'].default_value = 0.15

    # 5. Black Vane Face (Matte Absorbing + Glowing Heat Emission)
    mat_black = bpy.data.materials.new("VaneBlack")
    mat_black.use_nodes = True
    bs_bk = mat_black.node_tree.nodes.get("Principled BSDF")
    bs_bk.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
    bs_bk.inputs['Roughness'].default_value = 0.85
    bs_bk.inputs['Emission Color'].default_value = (1.0, 0.35, 0.05, 1.0) # Radiant heat
    bs_bk.inputs['Emission Strength'].default_value = 0.0

    # 6. Gas Molecules (Glowing Cyan Spheres)
    mat_molecule = bpy.data.materials.new("GasMolecule")
    mat_molecule.use_nodes = True
    bs_mol = mat_molecule.node_tree.nodes.get("Principled BSDF")
    bs_mol.inputs['Base Color'].default_value = (0.1, 0.8, 1.0, 1.0)
    bs_mol.inputs['Emission Color'].default_value = (0.2, 0.9, 1.0, 1.0)
    bs_mol.inputs['Emission Strength'].default_value = 4.0

    # 7. Hot Rocket Molecule (High Energy Orange/White Flash)
    mat_hot_mol = bpy.data.materials.new("HotMolecule")
    mat_hot_mol.use_nodes = True
    bs_hm = mat_hot_mol.node_tree.nodes.get("Principled BSDF")
    bs_hm.inputs['Base Color'].default_value = (1.0, 0.5, 0.1, 1.0)
    bs_hm.inputs['Emission Color'].default_value = (1.0, 0.6, 0.1, 1.0)
    bs_hm.inputs['Emission Strength'].default_value = 7.0

    # ==========================================
    # GEOMETRY
    # ==========================================
    # 1. Heavy Base Stand
    bpy.ops.mesh.primitive_cylinder_add(radius=1.3, depth=0.25, location=(0, 0, -2.1))
    base_obj = bpy.context.active_object
    base_obj.name = "RadiometerBase"
    base_obj.data.materials.append(mat_stand)

    # 2. Central Spindle Stem inside (Polished Chrome)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.2, location=(0, 0, -1.0))
    stem_obj = bpy.context.active_object
    stem_obj.name = "GlassStem"
    stem_obj.data.materials.append(mat_chrome)
    bpy.ops.object.shade_smooth()

    # 3. Fine Needle Pivot
    bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.005, depth=0.8, location=(0, 0, 0.2))
    needle_obj = bpy.context.active_object
    needle_obj.name = "NeedlePivot"
    needle_obj.data.materials.append(mat_chrome)

    # 4. Spindle Glass Cap (balanced on needle)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.14, location=(0, 0, 0.55))
    cap_obj = bpy.context.active_object
    cap_obj.name = "SpindleCap"
    cap_obj.data.materials.append(mat_chrome)

    # 5. Rotor Assembly (Parent of 4 Vanes and wire arms)
    rotor_parent = bpy.data.objects.new("RotorAssembly", None)
    rotor_parent.location = (0, 0, 0.55)
    scene.collection.objects.link(rotor_parent)
    cap_obj.parent = rotor_parent

    # 4 Wire Arms and 4 Dual-Sided Vanes
    vane_dist = 1.05
    vane_w = 0.45
    vane_h = 0.55
    vane_thick = 0.02

    vane_objects = []
    black_faces = []

    for i in range(4):
        angle = i * (math.pi / 2.0)
        arm_x = math.cos(angle) * (vane_dist / 2.0)
        arm_y = math.sin(angle) * (vane_dist / 2.0)

        # Wire Arm
        bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=vane_dist, location=(arm_x, arm_y, 0))
        arm = bpy.context.active_object
        arm.rotation_euler = (0, math.pi / 2.0, angle)
        arm.data.materials.append(mat_chrome)
        arm.parent = rotor_parent

        # Vane position
        vx = math.cos(angle) * vane_dist
        vy = math.sin(angle) * vane_dist

        # Silver Plate (Front/White face)
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(vx, vy, 0))
        vane_sv = bpy.context.active_object
        vane_sv.scale = (vane_thick / 2.0, vane_w / 2.0, vane_h / 2.0)
        vane_sv.rotation_euler = (0, 0, angle + math.pi / 2.0)
        vane_sv.data.materials.append(mat_silver)
        vane_sv.parent = rotor_parent

        # Black Plate (Back face, slightly offset to make dual-face vane)
        # Tangential offset:
        # In a radiometer, when light shines, black absorbs heat and retreats.
        # So black face is on one side, silver on the other.
        offset_x = -math.sin(angle) * 0.015
        offset_y = math.cos(angle) * 0.015
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(vx + offset_x, vy + offset_y, 0))
        vane_bk = bpy.context.active_object
        vane_bk.scale = (vane_thick / 2.0, vane_w / 2.0, vane_h / 2.0)
        vane_bk.rotation_euler = (0, 0, angle + math.pi / 2.0)
        vane_bk.data.materials.append(mat_black)
        vane_bk.parent = rotor_parent
        black_faces.append(vane_bk)

    # 6. Sleek Bulb Outline Ring (Zero Noise, crystal clear view inside!)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.85, minor_radius=0.015, location=(0, 0, 0.45))
    bulb_ring = bpy.context.active_object
    bulb_ring.name = "BulbOutlineRing"
    bulb_ring.data.materials.append(mat_chrome)

    # 7. Residual Gas Molecules (Cyan Spheres floating inside bulb)
    random.seed(42)
    molecules = []
    num_mols = 45
    for m in range(num_mols):
        rad = random.uniform(0.3, 1.4)
        th = random.uniform(0, 2 * math.pi)
        mz = random.uniform(-0.2, 1.1)
        mx = rad * math.cos(th)
        my = rad * math.sin(th)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(mx, my, mz))
        mol = bpy.context.active_object
        mol.name = f"Mol_{m}"
        mol.data.materials.append(mat_molecule)
        molecules.append({
            "obj": mol,
            "base_x": mx,
            "base_y": my,
            "base_z": mz,
            "speed": random.uniform(0.8, 1.8),
            "phase": random.uniform(0, 2 * math.pi)
        })

    # ==========================================
    # LIGHTING (Zack D. Dramatic Lighting)
    # ==========================================
    # Main Key Spotlight (Shining on the Radiometer from front-right)
    light_data = bpy.data.lights.new(name="MainBeam", type='SPOT')
    light_data.energy = 2200
    light_data.spot_size = math.radians(45)
    light_data.spot_blend = 0.25
    light_data.color = (1.0, 0.95, 0.85) # Warm sunlight
    light_obj = bpy.data.objects.new(name="MainBeamObj", object_data=light_data)
    light_obj.location = (2.5, -3.2, 1.8)
    light_obj.rotation_euler = (math.radians(65), 0, math.radians(35))
    scene.collection.objects.link(light_obj)

    # Rim Backlight (Vibrant Cyan Rim)
    rim_data = bpy.data.lights.new(name="RimLight", type='POINT')
    rim_data.energy = 900
    rim_data.color = (0.2, 0.8, 1.0)
    rim_obj = bpy.data.objects.new(name="RimLightObj", object_data=rim_data)
    rim_obj.location = (-2.0, 2.5, 2.2)
    scene.collection.objects.link(rim_obj)

    # Fill Ambient
    fill_data = bpy.data.lights.new(name="FillLight", type='POINT')
    fill_data.energy = 350
    fill_data.color = (0.7, 0.75, 0.9)
    fill_obj = bpy.data.objects.new(name="FillLightObj", object_data=fill_data)
    fill_obj.location = (0, -2.5, -0.5)
    scene.collection.objects.link(fill_obj)

    # ==========================================
    # CAMERA (Dynamic Cinematics)
    # ==========================================
    cam_data = bpy.data.cameras.new("RadiometerCamera")
    cam_data.lens = 48
    cam_obj = bpy.data.objects.new("RadiometerCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera Animation:
    # 1. Frames 1-120: Overview, looking at glass bulb and vanes beginning to spin
    # 2. Frames 120-220: Dramatic swoop zoom into the single vane cutaway
    # 3. Frames 220-380: Extreme macro view showing air molecules rebounding off hot black face
    # 4. Frames 380-570: Pull out to high angle watching entire radiometer spinning at 3,000 RPM!
    cam_obj.location = (0.0, -4.6, 0.9)
    cam_obj.rotation_euler = (math.radians(85), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Zoom in to Vane (macro)
    cam_obj.location = (0.8, -1.9, 0.58)
    cam_obj.rotation_euler = (math.radians(88), 0, math.radians(22))
    cam_obj.keyframe_insert(data_path="location", frame=180)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=180)

    # Extreme macro hold
    cam_obj.location = (0.95, -1.5, 0.55)
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(28))
    cam_obj.keyframe_insert(data_path="location", frame=340)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=340)

    # Pull out for High-Speed Spin Climax
    cam_obj.location = (1.2, -4.2, 2.6)
    cam_obj.rotation_euler = (math.radians(65), 0, math.radians(16))
    cam_obj.keyframe_insert(data_path="location", frame=440)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=440)

    cam_obj.location = (1.4, -3.8, 2.8)
    cam_obj.rotation_euler = (math.radians(63), 0, math.radians(20))
    cam_obj.keyframe_insert(data_path="location", frame=570)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=570)

    # ==========================================
    # ROTOR & HEAT ANIMATION
    # ==========================================
    # The rotor accelerates as thermal energy builds up!
    # Frame 1: 0 deg
    # Frame 120: slow start (2 revs)
    # Frame 240: macro vane passing by slowly to show molecules (controlled speed)
    # Frame 380-570: explosive acceleration to 3,000 RPM!
    cur_rot = 0.0
    for f in range(1, 571, 10):
        if f < 100:
            speed = 0.04 # gentle spin
        elif f < 220:
            speed = 0.08
        elif f < 360:
            speed = 0.05 # slow macro demonstration
        else:
            t = (f - 360) / 210.0
            speed = 0.08 + (t ** 1.8) * 0.75 # accelerating blur!

        cur_rot += speed * 10
        rotor_parent.rotation_euler = (0, 0, cur_rot)
        rotor_parent.keyframe_insert(data_path="rotation_euler", frame=f)

    # Heat Emission on Black Vanes (Glows hotter as light strikes)
    bs_bk.inputs['Emission Strength'].default_value = 0.0
    bs_bk.inputs['Emission Strength'].keyframe_insert("default_value", frame=1)

    bs_bk.inputs['Emission Strength'].default_value = 1.2
    bs_bk.inputs['Emission Strength'].keyframe_insert("default_value", frame=120)

    bs_bk.inputs['Emission Strength'].default_value = 5.5 # Glowing hot!
    bs_bk.inputs['Emission Strength'].keyframe_insert("default_value", frame=220)

    bs_bk.inputs['Emission Strength'].default_value = 6.0
    bs_bk.inputs['Emission Strength'].keyframe_insert("default_value", frame=360)

    bs_bk.inputs['Emission Strength'].default_value = 3.5
    bs_bk.inputs['Emission Strength'].keyframe_insert("default_value", frame=570)

    # Animate Gas Molecules (Jittering and blasting off during macro frames 180-360)
    for m_data in molecules:
        obj = m_data["obj"]
        bx, by, bz = m_data["base_x"], m_data["base_y"], m_data["base_z"]
        sp = m_data["speed"]
        ph = m_data["phase"]

        for f in [1, 100, 180, 240, 300, 360, 480, 570]:
            t = f / 24.0
            # Brownain motion
            dx = math.sin(t * sp + ph) * 0.12
            dy = math.cos(t * sp * 1.2 + ph) * 0.12
            dz = math.sin(t * sp * 0.8 + ph) * 0.08

            # If near the front vane at macro phase (around x=0.9, y=-0.5, z=0.55), launch away like a rocket!
            if 180 <= f <= 340 and (bx > 0.5 and by < 0):
                # Rocket kick away in Y direction!
                launch = ((f - 180) % 60) / 60.0
                dy -= launch * 0.45
                dx += launch * 0.2

            obj.location = (bx + dx, by + dy, bz + dz)
            obj.keyframe_insert(data_path="location", frame=f)

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

    print(f"Prepared Crookes Radiometer 3D Scene! Output: {out_file}", flush=True)

    test_frame = None
    if "-f" in sys.argv:
        idx = sys.argv.index("-f")
        if idx + 1 < len(sys.argv):
            test_frame = int(sys.argv[idx + 1])

    if test_frame is not None:
        scene.frame_set(test_frame)
        scene.render.image_settings.file_format = 'PNG'
        test_out = f"scratch/radiometer_frame_{test_frame}.png"
        scene.render.filepath = os.path.abspath(test_out)
        print(f"Rendering test frame {test_frame} -> {test_out}...", flush=True)
        bpy.ops.render.render(write_still=True)
        print("Test frame complete!", flush=True)
    elif do_render:
        print(f"Starting EEVEE Next Render (Frames 1 - {scene.frame_end})...", flush=True)
        bpy.ops.render.render(animation=True)
        print("Render complete!", flush=True)

if __name__ == "__main__":
    import sys
    build_crookes_radiometer_scene()
