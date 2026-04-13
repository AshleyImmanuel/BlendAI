import bpy # type: ignore

# Description: Full Scene Data Cleanup (Purge Orphans)
# Created by BlendAI Inbuilt Library

def purge_scene_data():
    # Recursively purge unused data-blocks
    bpy.ops.outliner.orphans_purge(do_local=True, do_linked=True, do_recursive=True)

if __name__ == "__main__":
    purge_scene_data()
