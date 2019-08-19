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
        else: ret = 'CENTIMETERS'

        print ('armature exported units is ' + ret + ', headTail: ' + str(headTail) + ', footTail: ' + str(footTail))

        self.armature.data.exportedUnits = ret
        return ret
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unitMultplierToExported(self):
        units = self.determineExportedUnits()

        if units == 'METERS': return 1
        elif units == 'DECIMETERS': return 10
        else: return 100
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

    #===========================================================================
    # for mocap support
    # the retargeting constraint space for arm bones is 'WORLD', while 'LOCAL' for rest
    def isArmBone(self, boneName):
        bones = self.clavicle(True) + self.clavicle(False) + \
                self.upperArm(True) + self.upperArm(False) + \
                self.lowerArm(True) + self.lowerArm(False) + \
                self.hand(True) + self.hand(False)
        return self.isFinger(boneName) or boneName in bones

    def isFinger(self, boneName):
        # for some skeleton, no thumbs or hand tips, so defensively coded
        if boneName == self.handTip(True ): return True
        if boneName == self.handTip(False): return True
        if boneName == self.thumb  (True ): return True
        if boneName == self.thumb  (False): return True
        return False

    # for animation scaling when compared with sensor's equivalent
    # being in world space also includes any amount the armature may have been raised / lowered to allow mesh to touch ground
    def pelvisInWorldSpace(self):
        return self.getBoneInWorldSpace(self.armature.pose.bones[self.pelvis])

    # for animation root placement
    def rootInWorldSpace(self):
        return self.getBoneInWorldSpace(self.armature.pose.bones[self.root])

    # for animation root placement
    def getBoneInWorldSpace(self, bone):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='POSE')

        worldMat = self.armature.convert_space(pose_bone = bone, matrix = bone.matrix, from_space = 'POSE',  to_space = 'WORLD')
        bpy.ops.object.mode_set(mode=current_mode)

        offset = worldMat.to_translation()
        return offset

    def getSensorMapping(self, sensorType = 'KINECT2'):
        if sensorType == 'KINECT2':

            return {
            # keys are kinect joints names coming from the sensor
            # values are bone names whose tail is at the joint
            'SpineBase'    : None,
            'SpineMid'     : self.pelvis,
            'SpineShoulder': self.upperSpine,

            'Neck'         : self.neckBase,
            'Head'         : self.head,

            'ShoulderLeft' : self.clavicle(True, True),
            'ElbowLeft'    : self.upperArm(True, True),
            'WristLeft'    : self.lowerArm(True, True),
            'HandLeft'     : self.hand(True, True),
            'HandTipLeft'  : self.handTip(True, True),
            'ThumbLeft'    : self.thumb(True, True),

            'ShoulderRight': self.clavicle(False, True),
            'ElbowRight'   : self.upperArm(False, True),
            'WristRight'   : self.lowerArm(False, True),
            'HandRight'    : self.hand(False, True),
            'HandTipRight' : self.handTip(False, True),
            'ThumbRight'   : self.thumb(False, True),

            'HipLeft'      : self.hip(True, True),
            'KneeLeft'     : self.thigh(True, True),
            'AnkleLeft'    : self.calf(True, True),
            'FootLeft'     : self.foot(True, True),

            'HipRight'     : self.hip(False, True),
            'KneeRight'    : self.thigh(False, True),
            'AnkleRight'   : self.calf(False, True),
            'FootRight'    : self.foot(False, True)
        }
        # add next sensor, eg., KINECT_AZURE
        elif sensorType == 'KINECT_AZURE':
            return None

        # this sensor is not supported
        else: return None
