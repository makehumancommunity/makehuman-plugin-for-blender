#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_StartMocapRecordingOperator(bpy.types.Operator):
    """Begin a motion capture session."""
    bl_idname = 'mh_community.start_mocap'
    bl_label = 'Record'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..mocap.sensor_runtime import Sensor

        device = context.scene.MhSensorType
        problemMsg = Sensor.beginRecording(device)
        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)

        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from ..mocap.sensor_runtime import Sensor
        return not Sensor.recording