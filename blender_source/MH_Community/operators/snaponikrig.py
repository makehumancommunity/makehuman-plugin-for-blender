#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo, IkRig

class SnapOnIkRigOperator(bpy.types.Operator):
    """Add bones which convert this to an IK Rig\n\nOnly Game or Kinect2 rigs."""
    bl_idname = 'mh_community.add_ik_rig'
    bl_label = '+'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        IkRig(rigInfo).add()

        self.report({'INFO'}, 'Added IK Rig to ' + rigInfo.name)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or not rigInfo.IKCapable(): return False

        # just need to check not already added
        return not rigInfo.hasIK()