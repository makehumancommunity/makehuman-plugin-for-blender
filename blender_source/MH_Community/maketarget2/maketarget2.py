#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy

class MHC_PT_MakeTarget_Panel(bpy.types.Panel):
    bl_label = "MakeTarget2"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MakeTarget2"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        createBox = layout.box()
        createBox.label(text="Create Target", icon="MESH_DATA")
        createBox.operator("mh_community.create_primary_target", text="Create primary")

        debugBox = layout.box()
        debugBox.label(text="Debug Target", icon="MESH_DATA")
        debugBox.operator("mh_community.print_primary_target", text="Print primary")

