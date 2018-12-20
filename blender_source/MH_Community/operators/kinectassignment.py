#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class KinectAssignmentOperator(bpy.types.Operator):
    """Assign an animation to an action of the selected skeleton.\n\nCan only be done to a Kinect2 rig."""
    bl_idname = 'mh_community.assign_kinect'
    bl_label = 'Assign'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..kinect_sensor.kinect2_runtime import KinectSensor

        armature = context.object
        baseActionName = context.scene.MhKinectBaseActionName
        excludeFingers = context.scene.MhExcludeFingers

        KinectSensor.assign(armature, context.scene.MhKinectAnimation_index, baseActionName, excludeFingers)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or rigInfo.name != 'Kinect2 Rig' or rigInfo.hasIKRigs(): return False

        return len(context.scene.MhKinectAnimations) > 0