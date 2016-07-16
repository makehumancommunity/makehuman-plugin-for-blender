import bpy
#===============================================================================
class SeparateEyes(bpy.types.Operator):
    """Separate The Eye mesh into left & right meshes, and move origin to center of mass of each."""
    bl_idname = 'mh_community.separate_eyes'
    bl_label = 'Separate Eye'

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):        
        return {'FINISHED'}
    
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'MESH'
#===============================================================================
