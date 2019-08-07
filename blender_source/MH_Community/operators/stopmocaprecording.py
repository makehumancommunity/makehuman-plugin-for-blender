#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_StopMocapRecordingOperator(bpy.types.Operator):
    """Complete a motion capture session."""
    bl_idname = 'mh_community.stop_mocap'
    bl_label = 'Stop'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..mocap.sensor_runtime import Sensor

        problemMsg = Sensor.stopRecording()
        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)

        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from ..mocap.sensor_runtime import Sensor
        return Sensor.recording