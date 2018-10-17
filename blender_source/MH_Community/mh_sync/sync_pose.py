#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Synchronize MakeHuman armature pose",
    "category": "Armature",
}

from .sync_ops import SyncOperator
from MH_Community.rig_info import *

import bpy
from mathutils import Matrix, Vector

class SyncPose(SyncOperator):
    def __init__(self, poseFilename = None, isExpression = False):
        super().__init__('getPose')
        if poseFilename is not None:
            self.call.setParam("poseFilename", poseFilename)

        self.isExpression = isExpression # used in callback
        self.executeJsonCall()

    def callback(self,json_obj):
        print("Update pose")

        self.skeleton = bpy.context.active_object
        self.rigInfo = RigInfo.determineRig(self.skeleton)
        feetOnGround = self.rigInfo.hasFeetOnGround()

        self.bones = self.skeleton.pose.bones
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        self.haveDots = self.bonesHaveDots()

        #apply as passed back
        for bone in self.bones:
            # Could have been exported with a Pose not currently matching MH session.
            # For expressions, only set bones with an ancestor of head to avoid extra stuff in pose library.
            # Still might work if both are facing forward.
            if not self.isExpression or self.hasAncestor(bone, 'head'):
                self.apply(bone, json_obj, bpy.context.scene.MhNoLocation)

        #feet on Ground processing
        if feetOnGround:
            rootBone = self.getRootBone()
            rootBone.location[0] = 0
            rootBone.location[1] = 0
            rootBone.location[2] = 0

    def apply(self, bone, json_obj, MhNoLocation):
        # the dots in collada exported bone names are replaced with '_', check for data with that changed back
        name = bone.name.replace("_", ".") if not self.haveDots else bone.name

        if name in json_obj.data:
            bone.matrix = Matrix(json_obj.data[name])
            if MhNoLocation:
                bone.location[0] = 0
                bone.location[1] = 0
                bone.location[2] = 0
            bpy.context.scene.update()

        else:
            print(name + ' bone not found coming from MH')

    def bonesHaveDots(self):
        for bone in self.bones:
            if "." in bone.name:
                return True

        return False

    def getRootBone(self):
        for bone in self.bones:
            if bone.parent is None:
                return bone

        # cannot really happen, but
        return None

    def hasAncestor(self, poseBone, ancestorName):
        while poseBone.parent is not None:
            if poseBone.parent.name == ancestorName:
                return True
            else:
                poseBone = poseBone.parent

    def getRestTranslation(self, bone):
        # need to change to edit mode to work with editbones
        bpy.ops.object.mode_set(mode='EDIT')
        for editBone in self.skeleton.data.edit_bones:
            if editBone.name == bone.name:
                ret = editBone.matrix.to_translation()
                bpy.ops.object.mode_set(mode='POSE')
                return ret
