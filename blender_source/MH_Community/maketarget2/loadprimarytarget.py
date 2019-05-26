#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bpy_extras, os, re
from bpy_extras.io_utils import ImportHelper
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

class MHC_OT_LoadPrimaryTargetOperator(bpy.types.Operator, ImportHelper):
    """Load required shape keys from file (i.e load a target)"""
    bl_idname = "mh_community.load_primary_target"
    bl_label = "Load primary target"

    filter_glob = StringProperty(default='*.target', options={'HIDDEN'})

    def execute(self, context):
        filename, extension = os.path.splitext(self.filepath)
        bn = os.path.basename(filename)
        context.scene.MhPrimaryTargetName = bn

        obj = context.active_object
        basis = obj.shape_key_add(name="Basis", from_mix=False)
        primaryTarget = obj.shape_key_add(name="PrimaryTarget", from_mix=True)
        primaryTarget.value = 1.0

        idx = context.active_object.data.shape_keys.key_blocks.find('PrimaryTarget')
        context.active_object.active_shape_key_index = idx

        sks = obj.data.shape_keys
        pt = sks.key_blocks["PrimaryTarget"]

        scaleFactor = 0.1
        scaleMode = str(bpy.context.scene.MhScaleMode)

        if scaleMode == "DECIMETER":
            scaleFactor = 1.0

        if scaleMode == "CENTIMETER":
            scaleFactor = 10.0

        with open(self.filepath,'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = re.compile(r"\s+").split(line.strip())
                    index = int(parts[0])
                    x = float(parts[1]) * scaleFactor
                    z = float(parts[2]) * scaleFactor
                    y = -float(parts[3]) * scaleFactor

                    print(str(index) + " " + str(x) + " " + str(y) + " " + str(z))

                    pt.data[index].co[0] = pt.data[index].co[0] + x
                    pt.data[index].co[1] = pt.data[index].co[1] + y
                    pt.data[index].co[2] = pt.data[index].co[2] + z


        return {'FINISHED'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if context.active_object.select_get():
                if context.active_object.MhObjectType == "Basemesh":
                    if not context.active_object.data.shape_keys:
                        return True
        return False
