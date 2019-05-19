#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy


class MHC_OT_PrintPrimaryTargetOperator(bpy.types.Operator):
    """Print all differing vertices to console"""
    bl_idname = "mh_community.print_primary_target"
    bl_label = "Print primary target"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if context.active_object.select_get():
                if context.active_object.MhObjectType == "Basemesh":
                    if context.active_object.data.shape_keys and context.active_object.data.shape_keys.key_blocks and "PrimaryTarget" in context.active_object.data.shape_keys.key_blocks:
                        return True
        return False

    def execute(self, context):

        obj = context.active_object
        sks = obj.data.shape_keys
        bt = sks.key_blocks["Basis"]
        pt = sks.key_blocks["PrimaryTarget"]

        numverts = len(bt.data)
        i = 0
        while i < numverts:
            btvco = bt.data[i].co
            ptvco = pt.data[i].co
            if btvco != ptvco:
                diffco = ptvco - btvco
                print(str(i) + " " + str(diffco))
            i = i + 1
        return {'FINISHED'}
