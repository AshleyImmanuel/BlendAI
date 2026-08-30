import bpy # type: ignore

# Description: Advanced PBR Material Setup for Principled BSDF
# Created by BlendAI Inbuilt Library

def create_pbr_material(name="BlendAI_PBR", color=(0.8, 0.8, 0.8, 1.0), roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    
    # Get the Principled BSDF node
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    
    return mat

if __name__ == "__main__":
    create_pbr_material()
