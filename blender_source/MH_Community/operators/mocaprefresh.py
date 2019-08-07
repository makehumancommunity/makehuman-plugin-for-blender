#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_MocapRefreshOperator(bpy.types.Operator):
    """Re-populate any captures recorded with a previously loaded blend.\nGood for populating multi-character animation across .blend files."""
    bl_idname = 'mh_community.refresh_mocap'
    bl_label = 'Refresh List'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from ..mocap.sensor_runtime import Sensor

        Sensor.displayRecordings()
        return {'FINISHED'}