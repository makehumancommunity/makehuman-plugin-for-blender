#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo, IkRig

class MHC_OT_SnapOnIkRigOperator(bpy.types.Operator):
    """Add bones which convert this to an IK Rig\n\nOnly Game or Kinect2 rigs."""
    bl_idname = 'mh_community.add_ik_rig'
    bl_label = '+'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object
        problemMsg = None
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            problemMsg = 'Unknown rigs are not supported.'
        elif not rigInfo.IKCapable():
            problemMsg = 'Rig is not capable of having an IK rig.'

        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)
        else:
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

        # just need to check not already added
        return rigInfo is not None and not rigInfo.hasIK()