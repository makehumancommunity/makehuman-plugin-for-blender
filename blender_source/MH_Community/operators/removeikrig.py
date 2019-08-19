#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo, IkRig

class MHC_OT_RemoveIkRigOperator(bpy.types.Operator):
    """Remove the IK rig previously added."""
    bl_idname = 'mh_community.remove_ik_rig'
    bl_label = '-'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object
        problemMsg = None
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            problemMsg = 'Unknown rigs are not supported.'

        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)
        else:
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

        # just need to check IK is there to be removed
        return rigInfo is not None and rigInfo.hasIK()