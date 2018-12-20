#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class StopKinectRecordingOperator(bpy.types.Operator):
    """Complete a Kinect motion capture session."""
    bl_idname = 'mh_community.stop_kinect'
    bl_label = 'Stop'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..kinect_sensor.kinect2_runtime import KinectSensor

        KinectSensor.close()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from ..kinect_sensor.kinect2_runtime import KinectSensor
        return KinectSensor.isKinectReady() and KinectSensor.recording