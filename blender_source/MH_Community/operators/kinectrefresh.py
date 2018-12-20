#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_KinectRefreshOperator(bpy.types.Operator):
    """Re-populate any captures recorded with a previously loaded blend.\nGood for populating multi-character animation across .blend files."""
    bl_idname = 'mh_community.refresh_kinect'
    bl_label = 'Refresh List'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..kinect_sensor.kinect2_runtime import KinectSensor

        KinectSensor.displayRecordings()
        return {'FINISHED'}