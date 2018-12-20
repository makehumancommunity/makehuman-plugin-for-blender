#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class StartKinectRecordingOperator(bpy.types.Operator):
    """Begin a Kinect motion capture session.\n\nCan only be done on Windows."""
    bl_idname = 'mh_community.start_kinect'
    bl_label = 'Record'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..kinect_sensor.kinect2_runtime import KinectSensor

        KinectSensor.capture()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from ..kinect_sensor.kinect2_runtime import KinectSensor
        return KinectSensor.isKinectReady() and not KinectSensor.recording