#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class RigInfo:
    @staticmethod
    def determineRig(armature):
        from .gameriginfo import GameRigInfo
        from .defaultriginfo import DefaultRigInfo
        from .cmuriginfo import CMURigInfo
        from .kinect2riginfo import Kinect2RigInfo

        # in the case where a test bone (wt dot) is not truely unique, order of tests might be important
        game = GameRigInfo(armature)
        if game.matches(): return game

        default = DefaultRigInfo(armature)
        if default.matches(): return default

        cmu = CMURigInfo(armature)
        if cmu.matches(): return cmu

        kinect2 = Kinect2RigInfo(armature)
        if kinect2.matches(): return kinect2

        return None
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # pass not only a unique bone name, but one that has a dot.  Collada would change that to a '_'
    def __init__(self, armature, name, uniqueBoneName):
        self.armature = armature
        self.name = name
        self.uniqueBoneName = uniqueBoneName
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def matches(self):
        boneWithoutDot = self.uniqueBoneName.replace(".", "_")
        for bone in self.armature.data.bones:
            # test without dot version first in case skeleton has no dots
            if bone.name == boneWithoutDot:
                self.dot = '_'
                return True

            if bone.name == self.uniqueBoneName:
                self.dot = '.'
                return True

        return False
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasFeetOnGround(self):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        # test if the Z of calf is negative, should be negative when feet NOT on ground
        calfZ = eBones[self.calf(False)].head.z

        bpy.ops.object.mode_set(mode=current_mode)
        return calfZ > 0
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # While MHX2 may set this, do not to rely on MHX.
    def determineExportedUnits(self):
        if len(self.armature.data.exportedUnits) > 0: return self.armature.data.exportedUnits

        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        headTail = eBones[self.head].tail.z
        footTail = eBones[self.foot(False)].tail.z
        bpy.ops.object.mode_set(mode=current_mode)

        totalHeight = headTail - footTail # done this way to be feet on ground independent
        if totalHeight < 5: ret = 'METERS' # decimeter threshold
        elif totalHeight <= 22: ret = 'DECIMETERS' # 21.7 to 23.9 is sort of no man's land of decimeters of tallest & inches of smallest
        else: ret = 'INCHES'

        print ('armature exported units is ' + ret + ', headTail: ' + str(headTail) + ', footTail: ' + str(footTail))

        self.armature.data.exportedUnits = ret
        return ret
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unitMultplierToExported(self):
        units = self.determineExportedUnits()

        if units == 'METERS': return 0.1
        elif units == 'DECIMETERS': return 1
        else: return 3.93701
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasIKRigs(self):
        return self.hasFingerIK() or self.hasIK()
    def hasFingerIK(self):
        return 'thumb.ik.L' in self.armature.data.bones
    def hasIK(self):
        return 'elbow.ik.L' in self.armature.data.bones
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasFingers(self):
        hand = self.hand(False)
        if hand not in self.armature.data.bones:
            return False

        for bone in self.armature.data.bones:
            if bone.parent is not None and bone.parent.name == hand:
                return True

        return False
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isExpressionCapable(self):
        return 'special03' in self.armature.data.bones
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isPoseCapable(self):
        return self.name == 'Default Rig' and not self.hasIKRigs()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # determine all the meshes which are controlled by skeleton,
    def getMeshesForRig(self, scene):
        meshes = []
        for object in [object for object in scene.objects]:
            if object.type == 'MESH' and len(object.vertex_groups) > 0 and self.armature == object.find_armature():
                meshes.append(object)

        return meshes
