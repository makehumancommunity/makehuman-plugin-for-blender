#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper


class MHAPI_SyncPanel(bpy.types.Panel):
    bl_label = "Synchronize"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MakeHuman"

    def draw(self, context):
        layout = self.layout
        split = layout.split()
        col = split.column(align=True)
        col.operator("mesh.sync_mh_mesh", text="Vertices", icon='MESH_DATA')
        #col.operator("mesh.primitive_torus_add", text="Torus", icon='MESH_TORUS')
        col.operator("armature.sync_pose", text="Pose", icon='ARMATURE_DATA')

def register():
    print("reg")
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)


