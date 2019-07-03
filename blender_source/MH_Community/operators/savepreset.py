#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..mh_sync.presets import *

class MHC_OT_SavePresetOperator(bpy.types.Operator):
    """Overwrite the selected preset with the current settings"""
    bl_idname = "mh_community.save_preset"
    bl_label = "Save preset"
    bl_options = {'REGISTER'}

    def execute(self, context):
        what = context.scene.MhGeneralPreset

        if what == "DEFAULT":
            saveDefaultSettings(context.scene)
            self.report({'INFO'}, "Presets " + what + " saved")
            return {'FINISHED'}
        if what == "MAKETARGET":
            saveMakeTargetSettings(context.scene)
            self.report({'INFO'}, "Presets " + what + " saved")
            return {'FINISHED'}
        if what == "MAKECLOTHES":
            saveMakeClothesSettings(context.scene)
            self.report({'INFO'}, "Presets " + what + " saved")
            return {'FINISHED'}

        self.report({'ERROR'}, "Could not find settings")
        return {'FINISHED'}




