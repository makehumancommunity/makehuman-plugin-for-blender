#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_PoseSyncOperator(bpy.types.Operator):
    """Synchronize the pose of the skeleton of a human with MH.  Requirements:\n\nMust be the Default armature.\nMust be exported in decimeters to allow location translation."""
    bl_idname = "mh_community.sync_pose"
    bl_label = "Synchronize MH Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mh_sync.sync_pose import SyncPose

        sp = SyncPose()
        sp.process()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.isPoseCapable()