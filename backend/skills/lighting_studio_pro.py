import bpy # type: ignore

# Description: Professional 3-Point Studio Lighting (Key, Fill, Rim)
# Created by BlendAI Inbuilt Library

def setup_studio_lighting():
    # Clear existing lights
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()

    # 1. Key Light (Main highlight)
    bpy.ops.object.light_add(type='AREA', location=(4, -4, 5))
    key = bpy.context.object
    key.name = "Key_Light"
    key.data.energy = 1000
    key.data.size = 3
    
    # 2. Fill Light (Softens shadows)
    bpy.ops.object.light_add(type='AREA', location=(-4, -2, 3))
    fill = bpy.context.object
    fill.name = "Fill_Light"
    fill.data.energy = 300
    fill.data.size = 5
    
    # 3. Rim Light (Edge separation)
    bpy.ops.object.light_add(type='AREA', location=(0, 5, 4))
    rim = bpy.context.object
    rim.name = "Rim_Light"
    rim.data.energy = 800
    rim.data.size = 2

    # Point all at world center
    for light in [key, fill, rim]:
        constraint = light.constraints.new(type='TRACK_TO')
        constraint.target = None # Usually we create an empty at 0,0,0
        # If no target, AI will handle pointing in the main script logic

if __name__ == "__main__":
    setup_studio_lighting()
