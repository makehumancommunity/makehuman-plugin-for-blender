import bpy
#===============================================================================

class SeparateEyes():
    def __init__(self, combinedMesh):
        priorName = combinedMesh.name
        nVertsHalf = len(combinedMesh.data.vertices) / 2

        # switch to edit, and de-select all verts Change selection mode
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.context.tool_settings.mesh_select_mode = (True , False , False)

        #selection using code do not actually work unless in object mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # select the first half of  the vertices, which is the lest side
        for vIndex, vert in enumerate(combinedMesh.data.vertices):
           if vIndex == nVertsHalf: break
           vert.select = True

        # switch back to edit & separate, which leaves the right side mesh still selected
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='SELECTED')

        # interface is in a strange state, combinedMesh is Right side, switch to Object mode, rename, & move origin
        bpy.ops.object.mode_set(mode='OBJECT')
        combinedMesh.name = priorName + '_R'
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        # select left side, make active, rename, move origin,
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        left = bpy.data.objects[priorName + '.001']
        left.select_set(True)
        bpy.context.view_layer.objects.active = left
        left.name =  priorName + '_L'
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
