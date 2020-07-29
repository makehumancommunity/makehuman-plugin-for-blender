#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigifyUtils

class MHC_OT_RigifyOperator(bpy.types.Operator):
    """Set up rigify for a MH mesh"""
    bl_idname = "mh_community.rigify"
    bl_label = "Set up rigify"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        objs = context.selected_objects
        if len(objs) == 0: return False
        if obj.type != 'MESH': return False
        if not obj in objs: return False
        if not "MhObjectType" in obj: return False                               
        return obj.MhObjectType == "Basemesh";     
        
    def execute(self, context):
        
        obj = context.active_object
        if obj.parent:
            if obj.parent.type == "ARMATURE":
                self.report({'ERROR'}, "Mesh is already rigged")
                return {'FINISHED'}
        if obj.MhScaleFactor > 0.2 or obj.MhScaleFactor < 0.09:
            self.report({'ERROR'}, "Mesh must have been imported with blender unit = \"meter\"")
            return {'FINISHED'}
        if obj.location.z > 0.1:
            self.report({'ERROR'}, "Must first apply all transforms (click ctrl-a do to this)")
            return {'FINISHED'}
        
        ru = RigifyUtils(obj)
        if not ru.hasDetailedHelpers():
            self.report({'ERROR'}, "Mesh must have been imported with \"detailed helpers\" enabled")
            return {'FINISHED'}
        ru.createMetaRig()
        return {'FINISHED'}