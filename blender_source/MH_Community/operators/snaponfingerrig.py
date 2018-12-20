#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo, FingerRig

class SnapOnFingerRigOperator(bpy.types.Operator):
    """Snap on finger control bones.\nNote an IK rig is always added with .ik in bones names, regardless of imported with MHX or Collada."""
    bl_idname = 'mh_community.add_finger_rig'
    bl_label = '+'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        FingerRig(rigInfo).add()

        self.report({'INFO'}, 'Added finger IK Rig to ' + rigInfo.name)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or not rigInfo.fingerIKCapable(): return False

        # just need to check not already added
        return not rigInfo.hasFingerIK()