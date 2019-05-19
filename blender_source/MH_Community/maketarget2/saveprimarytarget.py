#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy


class MHC_OT_SavePrimaryTargetOperator(bpy.types.Operator):
    """Print all differing vertices to console"""
    bl_idname = "mh_community.save_primary_target"
    bl_label = "Save primary target"
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

        scaleFactor = 10.0
        scaleMode = str(bpy.context.scene.MhScaleMode)

        if scaleMode == "DECIMETER":
            scaleFactor = 1.0

        if scaleMode == "CENTIMETER":
            scaleFactor = 0.1

        obj = context.active_object
        sks = obj.data.shape_keys
        bt = sks.key_blocks["Basis"]
        pt = sks.key_blocks["PrimaryTarget"]

        with open("/tmp/target.target","w") as f:
            f.write("# This is a target file for MakeHuman. It was written by MakeTarget2, which is a\n")
            f.write("# part of the MakeHuman Community plugin for Blender.\n#\n")
            f.write("# basemesh hm08\n")
            numverts = len(bt.data)
            i = 0
            while i < numverts:
                btvco = bt.data[i].co
                ptvco = pt.data[i].co
                if btvco != ptvco:
                    diffco = ptvco - btvco
                    x = str(diffco[0] * scaleFactor)
                    y = str(-diffco[1] * scaleFactor)
                    z = str(diffco[2] * scaleFactor)
                    f.write(str(i) + " " + x + " " + z + " " + y + "\n")
                i = i + 1
        return {'FINISHED'}
