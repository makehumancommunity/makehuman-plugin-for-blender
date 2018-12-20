#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo, FingerRig

class RemoveFingerRigOperator(bpy.types.Operator):
    """Remove the finger IK rig previously added."""
    bl_idname = 'mh_community.remove_finger_rig'
    bl_label = '-'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        FingerRig(rigInfo).remove()

        self.report({'INFO'}, 'Removed finger IK Rig')
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.hasFingerIK()