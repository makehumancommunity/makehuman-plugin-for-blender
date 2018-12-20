#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class AmputateFaceOperator(bpy.types.Operator):
    """Remove face bones, and assign their weights to head bone"""
    bl_idname = "mh_community.amputate_face"
    bl_label = "Face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        # find all meshes which use this armature
        meshes = rigInfo.getMeshesForRig(context.scene)

        # could still have face bones on Kinect2 rig, which has different name, so check by rig
        boneName = 'head' if rigInfo.name == 'Default Rig' else 'Head'
        BoneSurgery.amputate(armature, meshes, boneName)

        self.report({'INFO'}, 'Amputated fingers to ' + rigInfo.name)
        return {'FINISHED'}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.isExpressionCapable()