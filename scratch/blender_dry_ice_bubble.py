import bpy
import math
import random
import os
import sys

def build_dry_ice_bubble_scene(out_file="scratch/blender_dry_ice_1080x1920.mp4", do_render=True):
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
        bg_node.inputs[0].default_value = (0.010, 0.012, 0.022, 1.0)
        bg_node.inputs[1].default_value = 0.5

    # ==========================================
    # MATERIALS
    # ==========================================
    # 1. Glass Lab Bowl
    mat_bowl = bpy.data.materials.new("GlassLabBowl")
    mat_bowl.use_nodes = True
    bs_b = mat_bowl.node_tree.nodes.get("Principled BSDF")
    bs_b.inputs['Base Color'].default_value = (0.85, 0.95, 1.0, 0.35)
    bs_b.inputs['Roughness'].default_value = 0.05
    bs_b.inputs['Transmission Weight'].default_value = 0.9
    bs_b.inputs['IOR'].default_value = 1.48

    # 2. Iridescent Soap Bubble Dome (Thin-film rainbow shimmer)
    mat_bubble = bpy.data.materials.new("SoapBubbleMembrane")
    mat_bubble.use_nodes = True
    bs_bb = mat_bubble.node_tree.nodes.get("Principled BSDF")
    bs_bb.inputs['Base Color'].default_value = (0.9, 0.95, 1.0, 0.15)
    bs_bb.inputs['Roughness'].default_value = 0.02
    bs_bb.inputs['Metallic'].default_value = 0.25
    bs_bb.inputs['Transmission Weight'].default_value = 0.92
    bs_bb.inputs['Emission Color'].default_value = (0.4, 0.8, 1.0, 1.0) # Faint iridescent edge
    bs_bb.inputs['Emission Strength'].default_value = 0.8

    # 3. Trapped Dense White CO2 Fog / Clouds
    mat_fog = bpy.data.materials.new("DenseWhiteFog")
    mat_fog.use_nodes = True
    bs_fg = mat_fog.node_tree.nodes.get("Principled BSDF")
    bs_fg.inputs['Base Color'].default_value = (0.92, 0.95, 0.98, 0.75)
    bs_fg.inputs['Roughness'].default_value = 0.6
    bs_fg.inputs['Emission Color'].default_value = (0.85, 0.9, 1.0, 1.0)
    bs_fg.inputs['Emission Strength'].default_value = 0.6

    # 4. Green Laser Beam (Illuminating the swirling fog)
    mat_laser = bpy.data.materials.new("GreenLaser")
    mat_laser.use_nodes = True
    bs_ls = mat_laser.node_tree.nodes.get("Principled BSDF")
    bs_ls.inputs['Base Color'].default_value = (0.1, 1.0, 0.2, 1.0)
    bs_ls.inputs['Emission Color'].default_value = (0.1, 1.0, 0.2, 1.0)
    bs_ls.inputs['Emission Strength'].default_value = 8.0

    # 5. Laboratory Table Stand
    mat_table = bpy.data.materials.new("LabTable")
    mat_table.use_nodes = True
    bs_tb = mat_table.node_tree.nodes.get("Principled BSDF")
    bs_tb.inputs['Base Color'].default_value = (0.08, 0.09, 0.12, 1.0)
    bs_tb.inputs['Metallic'].default_value = 0.6
    bs_tb.inputs['Roughness'].default_value = 0.35

    # ==========================================
    # GEOMETRY
    # ==========================================
    # Table surface
    bpy.ops.mesh.primitive_cylinder_add(radius=2.2, depth=0.3, location=(0, 0, -1.5))
    table = bpy.context.active_object
    table.data.materials.append(mat_table)

    # Glass Bowl (Hemisphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.2, location=(0, 0, -0.6))
    bowl = bpy.context.active_object
    bowl.name = "GlassBowl"
    bowl.data.materials.append(mat_bowl)

    # Cut upper half of bowl so it's an open bowl
    bpy.ops.mesh.primitive_cube_add(size=3.0, location=(0, 0, 1.0))
    cutter_b = bpy.context.active_object
    mod_b = bowl.modifiers.new("OpenRim", "BOOLEAN")
    mod_b.operation = 'DIFFERENCE'
    mod_b.object = cutter_b
    cutter_b.hide_render = True
    cutter_b.hide_viewport = True

    # Swelling Giant Soap Bubble Dome (Starts flat at rim Z=-0.1, swells to giant sphere!)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.22, location=(0, 0, -0.5))
    bubble_dome = bpy.context.active_object
    bubble_dome.name = "SoapBubbleDome"
    bubble_dome.data.materials.append(mat_bubble)
    bubble_dome.scale = (1.0, 1.0, 0.05) # Flat initially

    # Trapped Swirling Fog Cloud Cluster inside
    fog_particles = []
    random.seed(77)
    for f_i in range(28):
        fx = random.uniform(-0.6, 0.6)
        fy = random.uniform(-0.6, 0.6)
        fz = random.uniform(-0.8, 0.1)
        fr = random.uniform(0.18, 0.35)
        bpy.ops.mesh.primitive_uv_sphere_add(radius=fr, location=(fx, fy, fz))
        fog_c = bpy.context.active_object
        fog_c.name = f"Fog_{f_i}"
        fog_c.data.materials.append(mat_fog)
        fog_particles.append({
            "obj": fog_c,
            "base_x": fx,
            "base_y": fy,
            "base_z": fz,
            "speed": random.uniform(1.2, 2.5),
            "phase": random.uniform(0, 2 * math.pi)
        })

    # Green Laser Line slicing through fog
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=3.5, location=(0, 0, 0.2))
    laser = bpy.context.active_object
    laser.name = "LaserBeam"
    laser.rotation_euler = (0, math.pi / 2.0, math.radians(20))
    laser.data.materials.append(mat_laser)

    # ==========================================
    # LIGHTING
    # ==========================================
    key_light = bpy.data.lights.new(name="BubbleKey", type='SPOT')
    key_light.energy = 2200
    key_light.spot_size = math.radians(45)
    key_light.spot_blend = 0.3
    key_light.color = (1.0, 0.95, 0.9)
    key_obj = bpy.data.objects.new("BubbleKeyObj", key_light)
    key_obj.location = (2.2, -3.2, 2.4)
    key_obj.rotation_euler = (math.radians(65), 0, math.radians(35))
    scene.collection.objects.link(key_obj)

    rim_light = bpy.data.lights.new(name="BubbleRim", type='POINT')
    rim_light.energy = 950
    rim_light.color = (0.2, 0.8, 1.0)
    rim_obj = bpy.data.objects.new("BubbleRimObj", rim_light)
    rim_obj.location = (-2.2, 2.5, 1.2)
    scene.collection.objects.link(rim_obj)

    # ==========================================
    # CAMERA (Cinematic Pacing)
    # ==========================================
    cam_data = bpy.data.cameras.new("BubbleCamera")
    cam_data.lens = 45
    cam_obj = bpy.data.objects.new("BubbleCamera", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    # Camera Animation:
    # Frames 1-100: Wipe soap across bowl rim
    # Frames 100-240: Soap bubble dome swells up, trapping glowing vapor
    # Frames 240-360: Macro view of green laser scattering inside the trapped vortex
    # Frames 360-460: Bubble reaches massive giant size, wobbles delicately
    # Frames 460-570: POP! Slow-motion explosion of cloud releasing into room!
    cam_obj.location = (0.0, -4.2, 0.4)
    cam_obj.rotation_euler = (math.radians(86), 0, 0)
    cam_obj.keyframe_insert(data_path="location", frame=1)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=1)

    # Macro zoom to swelling dome & laser
    cam_obj.location = (0.6, -2.0, 0.3)
    cam_obj.rotation_euler = (math.radians(88), 0, math.radians(16))
    cam_obj.keyframe_insert(data_path="location", frame=200)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=200)

    # Extreme macro on swirling fog
    cam_obj.location = (0.4, -1.4, 0.25)
    cam_obj.rotation_euler = (math.radians(88), 0, math.radians(14))
    cam_obj.keyframe_insert(data_path="location", frame=340)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=340)

    # Pull out for giant burst climax
    cam_obj.location = (0.8, -3.8, 1.0)
    cam_obj.rotation_euler = (math.radians(75), 0, math.radians(12))
    cam_obj.keyframe_insert(data_path="location", frame=440)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=440)

    cam_obj.location = (0.9, -3.5, 1.2)
    cam_obj.rotation_euler = (math.radians(72), 0, math.radians(15))
    cam_obj.keyframe_insert(data_path="location", frame=570)
    cam_obj.keyframe_insert(data_path="rotation_euler", frame=570)

    # ==========================================
    # SWELL & POP ANIMATION
    # ==========================================
    # Bubble Dome Growth:
    # Frame 1: Flat film across rim
    bubble_dome.scale = (1.0, 1.0, 0.02)
    bubble_dome.location = (0, 0, -0.1)
    bubble_dome.keyframe_insert(data_path="scale", frame=1)
    bubble_dome.keyframe_insert(data_path="location", frame=1)

    # Swells to dome by Frame 200
    bubble_dome.scale = (1.1, 1.1, 0.65)
    bubble_dome.location = (0, 0, 0.25)
    bubble_dome.keyframe_insert(data_path="scale", frame=200)
    bubble_dome.keyframe_insert(data_path="location", frame=200)

    # Swells to giant sphere dome by Frame 450
    bubble_dome.scale = (1.35, 1.35, 1.25)
    bubble_dome.location = (0, 0, 0.75)
    bubble_dome.keyframe_insert(data_path="scale", frame=450)
    bubble_dome.keyframe_insert(data_path="location", frame=450)

    # POP at Frame 460!
    bubble_dome.scale = (1.38, 1.38, 1.28)
    bubble_dome.keyframe_insert(data_path="scale", frame=459)
    # Explodes / vanishes!
    bubble_dome.scale = (0.001, 0.001, 0.001)
    bubble_dome.keyframe_insert(data_path="scale", frame=462)

    # Fog Swirling & Expansion at Pop
    for fp in fog_particles:
        f_obj = fp["obj"]
        bx, by, bz = fp["base_x"], fp["base_y"], fp["base_z"]
        sp = fp["speed"]
        ph = fp["phase"]

        for f in [1, 100, 200, 300, 400, 459, 480, 520, 570]:
            t = f / 24.0
            # Swirling inside
            swirl_x = math.sin(t * sp + ph) * 0.15
            swirl_y = math.cos(t * sp + ph) * 0.15
            swell_z = (f / 450.0) * 0.6 if f < 460 else 0.6

            # When pop occurs at 460, fog mushrooms outward!
            if f >= 460:
                burst_t = (f - 460) / 110.0
                swirl_x += math.cos(ph) * (burst_t * 2.2)
                swirl_y += math.sin(ph) * (burst_t * 2.2)
                swell_z += burst_t * 1.5

            f_obj.location = (bx + swirl_x, by + swirl_y, bz + swell_z)
            f_obj.keyframe_insert(data_path="location", frame=f)

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
        test_out = f"scratch/dry_ice_frame_{test_frame}.png"
        scene.render.filepath = os.path.abspath(test_out)
        print(f"Rendering test frame {test_frame} -> {test_out}...", flush=True)
        bpy.ops.render.render(write_still=True)
        print("Test frame complete!", flush=True)
    elif do_render:
        print(f"Starting EEVEE Next Render (Frames 1 - {scene.frame_end})...", flush=True)
        bpy.ops.render.render(animation=True)
        print("Render complete!", flush=True)

if __name__ == "__main__":
    build_dry_ice_bubble_scene()
