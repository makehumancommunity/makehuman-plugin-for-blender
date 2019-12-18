#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo


class MHC_OT_PoseRightOperator(bpy.types.Operator):
    """This is a diagnostic operator, which poses both the capture & final armatures one frame at a time."""
    bl_idname = 'mh_community.pose_right'
    bl_label = 'Next Frame'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mocap.sensor_runtime import Sensor

        armature = context.object
        problemMsg = None
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            problemMsg = 'Unknown rigs are not supported.'
        elif not rigInfo.isMocapCapable():
            problemMsg = 'Rig is not capable of motion capture.'
        elif len(context.scene.MhSensorAnimations) == 0:
            problemMsg = 'No current capture being buffered.'

        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)
        else:
            Sensor.oneRight(rigInfo, context.scene.MhSensorAnimation_index)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob is not None and ob.type == 'ARMATURE'