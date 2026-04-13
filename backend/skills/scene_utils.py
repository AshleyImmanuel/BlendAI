### SKILL: scene_utils.py
# Description: Advanced scene management, organization, and master cleanup.

def Master_Cleanup():
    """Deletes all objects, meshes, and materials to start fresh."""
    import bpy  # type: ignore
    import mathutils # type: ignore
    
    # Delete all objects in the current view layer
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Purge unused data blocks
    bpy.data.orphans_purge()
    
    return True

def Randomize_Transforms(obj, loc_range=(0,0,0), rot_range=(0,0,0), scale_range=(0,0,0)):
    """Apply professional randomization to an object."""
    import bpy  # type: ignore
    import random
    
    obj.location[0] += random.uniform(-loc_range[0], loc_range[0])
    obj.location[1] += random.uniform(-loc_range[1], loc_range[1])
    obj.location[2] += random.uniform(-loc_range[2], loc_range[2])
    
    obj.rotation_euler[0] += random.uniform(-rot_range[0], rot_range[0])
    obj.rotation_euler[1] += random.uniform(-rot_range[1], rot_range[1])
    obj.rotation_euler[2] += random.uniform(-rot_range[2], rot_range[2])
    
    return True
