#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..mh_sync.presets import *

class MHC_OT_LoadPresetOperator(bpy.types.Operator):
    """Load an importer UI preset"""
    bl_idname = "mh_community.load_preset"
    bl_label = "Load preset"
    bl_options = {'REGISTER'}

    def execute(self, context):
        what = context.scene.MhGeneralPreset
        settings = None

        if what == "DEFAULT":
            settings = loadOrCreateDefaultSettings()
        if what == "MAKETARGET":
            settings = loadOrCreateMakeTargetSettings()
        if what == "MAKECLOTHES":
            settings = loadOrCreateMakeClothesSettings()

        if settings is None:
            self.report({'ERROR'}, "Could not find settings")
            return {'FINISHED'}

        applySettings(settings)

        self.report({'INFO'}, "Presets " + what + " loaded")
        return {'FINISHED'}
