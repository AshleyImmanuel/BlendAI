import bpy # type: ignore

# Description: Physical Scene Defaults (Metric Units, Camera 50mm, Scene Scale)
# Created by BlendAI Inbuilt Library

def setup_scene_physics():
    # Set Metric Units
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1.0
    
    # Configure Camera Defaults
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
        cam.data.lens = 50 # Standard portrait lens
        cam.data.clip_start = 0.1
        cam.data.clip_end = 1000

if __name__ == "__main__":
    setup_scene_physics()
