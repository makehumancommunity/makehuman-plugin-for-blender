#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo


class MHC_OT_PoseRightOperator(bpy.types.Operator):
    """This is a diagnostic operator, which poses both the capture & final armatures one frame at a time."""
    bl_idname = 'mh_community.pose_right'
    bl_label = '1 Right'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..kinect_sensor.kinect2_runtime import KinectSensor

        armature = context.object
        KinectSensor.oneRight(armature, context.scene.MhKinectAnimation_index)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or rigInfo.name != 'Kinect2 Rig': return False

        return len(context.scene.MhKinectAnimations) > 0
