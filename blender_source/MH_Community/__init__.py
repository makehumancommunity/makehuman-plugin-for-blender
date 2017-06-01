#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "MH Community Plug-in",
    "author": "Joel Palmius",
    "version": (0, 3),
    "blender": (2, 77, 0),
    "location": "View3D > Properties > MH",
    "description": "Post import MakeHuman operations",
    "wiki_url": "https://github.com/makehumancommunity/community-plugins/tree/master/blender_source/MH_Community",
    "category": "MakeHuman"}

if "bpy" in locals():
    print("Reloading MH community plug-in v %d.%d" % bl_info["version"])
    import imp
    imp.reload(mh_sync)  # directory
    imp.reload(separate_eyes)
    imp.reload(snap_on_finger_rig)
    imp.reload(snap_on_ik_rig)
    imp.reload(amputate_fingers)
    imp.reload(rig_info)
else:
    print("Loading MH community plug-in v %d.%d" % bl_info["version"])
    from . import mh_sync # directory
    from . import separate_eyes
    from . import snap_on_finger_rig
    from . import snap_on_ik_rig
    from . import amputate_fingers
    from . import rig_info

import bpy
from bpy.props import BoolProperty,StringProperty
#===============================================================================
def register():
    bpy.types.Scene.MhFeetOnGround = BoolProperty(name="Feet on Ground", description="Model was exported with feet on ground.  Checking this causes\nroot bone location translation to be cleared.", default=False)
    bpy.types.Scene.MhNoLocation = BoolProperty(name="No Location Translation", description="Some Expressions have bone translation on locked bones.\nChecking this causes it to be cleared.  When false,\nALT-G will NOT clear these.", default=False)
    bpy.types.Scene.MhExprFilterTag = StringProperty(name="Tag:", description="", default="")
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    unregister()
    register()

print("MH community plug-in load complete")
#===============================================================================
class Community_Panel(bpy.types.Panel):
    bl_label = "Community"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MakeHuman"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        layout.label(text="Mesh Operations:", icon="MESH_DATA")
        layout.operator("mh_community.sync_mh_mesh", text="Sync with MH")
        layout.operator("mh_community.separate_eyes", text="Separate Eyes")

        layout.separator()

        layout.label(text="Bone Operations:", icon="ARMATURE_DATA")
        layout.operator("mh_community.sync_pose", text="Sync with MH")
        layout.prop(scn, "MhFeetOnGround")
        layout.prop(scn, "MhNoLocation")
        layout.separator()
        layout.operator("mh_community.ik_rig", text="Convert to IK rig")
        layout.operator("mh_community.finger_rig", text="Add Finger IK Bones")
        layout.operator("mh_community.amputate_fingers", text="Remove Finger Bones")
        
        layout.separator()
        layout.label(text="Expression Transfer:")
        layout.prop(scn, "MhExprFilterTag")
        layout.operator("mh_community.expressions_trans", text="To Pose Lib")
#===============================================================================
class MeshSyncOperator(bpy.types.Operator):
    """Synchronize the shape of a human with MH"""
    bl_idname = "mh_community.sync_mh_mesh"
    bl_label = "Synchronize MH Mesh"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from .mh_sync.sync_mesh import SyncMesh
        SyncMesh()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'MESH'
#===============================================================================
class PoseSyncOperator(bpy.types.Operator):
    """Synchronize the pose of the skeleton of a human with MH"""
    bl_idname = "mh_community.sync_pose"
    bl_label = "Synchronize MH Pose"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from .mh_sync.sync_pose import SyncPose
        SyncPose()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'ARMATURE'
#===============================================================================
class ExpressionTransOperator(bpy.types.Operator):
    """Transfer MakeHuman expressions to a pose library"""
    bl_idname = "mh_community.expressions_trans"
    bl_label = "Expressions to Poselib"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        from .mh_sync.expr_to_poselib import ExprToPoselib
        ExprToPoselib()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'ARMATURE' and ob.pose_library
#===============================================================================
