import bpy
#===============================================================================
HIPOLY_VERTS  = 1064
LOWPOLY_VERTS = 96

class SeparateEyes(bpy.types.Operator):
    """Separate The Eye mesh into left & right meshes, and move origin to center of mass of each."""
    bl_idname = 'mh_community.separate_eyes'
    bl_label = 'Separate Eye'

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):     
        combinedMesh = context.object
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
        
        # set base class, and also ignore skeleton for BabylonJS export
        combinedMesh.data.baseClass = 'BEING.EyeBall'
        combinedMesh.data.ignoreSkeleton = True # now needs to be parented to Body; do that yourself
        
        # select left side, make active, rename, move origin, 
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        left = bpy.data.objects[priorName + '.001']
        left.select = True
        context.scene.objects.active = left
        left.name =  priorName + '_L'
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        
        # set base class, and also ignore skeleton for BabylonJS export
        left.data.baseClass = 'BEING.EyeBall'
        left.data.ignoreSkeleton = True  # now needs to be parented to Body; do that yourself

        return {'FINISHED'}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -           
    @classmethod
    def poll(cls, context):
        ob = context.object
        
        # must be a mesh
        if not ob or ob.type != 'MESH': 
            return False
        
        # vertex count must match
        nVerts = len(ob.data.vertices)
        return nVerts == HIPOLY_VERTS or nVerts == LOWPOLY_VERTS