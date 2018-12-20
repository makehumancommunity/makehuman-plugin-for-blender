#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_BodyImportOperator(bpy.types.Operator):
    """Import a human from MH"""
    bl_idname = "mh_community.import_body"
    bl_label = "Import body from MH"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mh_sync.import_body_binary import ImportBodyBinary
        ImportBodyBinary()
        return {'FINISHED'}