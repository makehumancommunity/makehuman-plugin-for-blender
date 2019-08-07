#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_MocapAssignmentOperator(bpy.types.Operator):
    """Assign an animation to an action of the selected skeleton."""
    bl_idname = 'mh_community.assign_mocap'
    bl_label = 'Assign'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mocap.sensor_runtime import Sensor

        armature = context.object
        rigInfo = RigInfo.determineRig(armature)
        baseActionName = context.scene.MhSensorBaseActionName

        Sensor.assign(rigInfo, context.scene.MhSensorAnimation_index, baseActionName)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or not rigInfo.isMocapCapable() or rigInfo.hasIKRigs(): return False

        return len(context.scene.MhSensorAnimations) > 0