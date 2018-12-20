#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class AmputateFingersOperator(bpy.types.Operator):
    """Remove finger bones, and assign their weights to hand bone"""
    bl_idname = "mh_community.amputate_fingers"
    bl_label = "Fingers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        # find all meshes which use this armature
        meshes = rigInfo.getMeshesForRig(context.scene)

        BoneSurgery.amputate(armature, meshes, rigInfo.hand(True ))
        BoneSurgery.amputate(armature, meshes, rigInfo.hand(False))

        # kinect2 also needs to delete Thumbs, which got re-parent higher
        if rigInfo.name == 'Kinect2 Rig':
            BoneSurgery.deleteBone(armature, meshes, Kinect2RigInfo.boneFor('Thumb', True ), Kinect2RigInfo.boneFor('Hand', True ))
            BoneSurgery.deleteBone(armature, meshes, Kinect2RigInfo.boneFor('Thumb', False), Kinect2RigInfo.boneFor('Hand', False))

        self.report({'INFO'}, 'Amputated fingers to ' + rigInfo.name)
        return {'FINISHED'}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.hasFingers()