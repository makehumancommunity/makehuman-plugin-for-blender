#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class RemoveIkRigOperator(bpy.types.Operator):
    """Remove the IK rig previously added."""
    bl_idname = 'mh_community.remove_ik_rig'
    bl_label = '-'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..snap_on_ik_rig import IkRig
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        IkRig(rigInfo).remove()

        self.report({'INFO'}, 'Removed IK Rig')
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.hasIK()