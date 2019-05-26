#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_CreatePrimaryTargetOperator(bpy.types.Operator):
    """Setup required shape keys (i.e create a target)"""
    bl_idname = "mh_community.create_primary_target"
    bl_label = "Create primary target"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if context.active_object.select_get():
                if context.active_object.MhObjectType == "Basemesh":
                    if not context.active_object.data.shape_keys:
                        return True
        return False

    def execute(self, context):

        obj = context.active_object
        basis = obj.shape_key_add(name="Basis",from_mix=False)
        primaryTarget = obj.shape_key_add(name="PrimaryTarget", from_mix=True)
        primaryTarget.value = 1.0

        idx = context.active_object.data.shape_keys.key_blocks.find('PrimaryTarget')
        context.active_object.active_shape_key_index = idx

        return {'FINISHED'}
