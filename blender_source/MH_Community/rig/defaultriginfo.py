#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from .riginfo import RigInfo

class DefaultRigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'Default Rig', 'shoulder01.L')

        self.pelvis = 'spine05'
        self.root = 'root'
        self.head = 'head'
        self.kneeIKChainLength =  2
        self.footIKChainLength =  4
        self.handIKChainLength =  4
        self.elbowIKChainLength = 2
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # cannot be static, since dot is only at instance level
    def boneFor(self, baseName, isLeft):
        return baseName + self.dot + ('L' if isLeft else 'R')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # specific to DefaultRigInfo
    def hasRestTpose(self):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        # test that both sides have wrist Z greater than the head of spine1 head, & are equal
        minZ = eBones['spine01'].head.z
        left  = round(eBones[self.hand(True )].tail.z, 4)
        right = round(eBones[self.hand(False)].tail.z, 4)

        bpy.ops.object.mode_set(mode=current_mode)
        return left > minZ and left == right

    def clavicle(self, isLeft): return 'clavicle.' + ('L' if isLeft else 'R')
    def upperArm(self, isLeft): return 'upperarm02.' + ('L' if isLeft else 'R')
    def lowerArm(self, isLeft): return 'lowerarm02.' + ('L' if isLeft else 'R')
    def thigh(self, isLeft): return 'upperleg02.' + ('L' if isLeft else 'R')

    def _defaultLockInfo(self):
        out = {}
        out["lockX"] = True
        out["lockY"] = False
        out["lockZ"] = True
        out["limitXMin"] = None
        out["limitXMax"] = None
        out["limitYMin"] = -20
        out["limitYMax"] = 20
        out["limitZMin"] = None
        out["limitZMax"] = None
        return out

    def additionalLocks(self):

        bones = {}
        bones["lowerarm02"] = self._defaultLockInfo()
        bones["upperarm02"] = self._defaultLockInfo()
        bones["lowerleg02"] = self._defaultLockInfo()
        bones["upperleg02"] = self._defaultLockInfo()

        out = {}
        for key in bones.keys():
            out[key + ".L"] = bones[key]
            out[key + ".R"] = bones[key]

        return out


    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for IK rigging support, which DefaultRig does not have
    def IKCapable(self): return True
    def hand(self, isLeft): return self.boneFor('wrist', isLeft) # also used for amputation
    def calf(self, isLeft): return 'lowerleg02.' + ('L' if isLeft else 'R')
    def foot(self, isLeft): return self.boneFor('foot', isLeft) # used for super.determineExportedUnits()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return self.pinkyFingerParent(False) in self.armature.data.bones
    def thumbParent(self, isLeft): return self.boneFor('finger1-1', isLeft)
    def thumbBones (self, isLeft):
        ret = []
        ret.append(self.boneFor('finger1-2', isLeft))
        ret.append(self.boneFor('finger1-3', isLeft))
        return ret

    def indexFingerParent(self, isLeft): return self.boneFor('metacarpal1', isLeft)
    def indexFingerBones (self, isLeft):
        ret = []
        ret.append(self.boneFor('finger2-1', isLeft))
        ret.append(self.boneFor('finger2-2', isLeft))
        ret.append(self.boneFor('finger2-3', isLeft))
        return ret

    def middleFingerParent(self, isLeft): return self.boneFor('metacarpal2', isLeft)
    def middleFingerBones(self , isLeft):
        ret = []
        ret.append(self.boneFor('finger3-1', isLeft))
        ret.append(self.boneFor('finger3-2', isLeft))
        ret.append(self.boneFor('finger3-3', isLeft))
        return ret

    def ringFingerParent(self, isLeft): return self.boneFor('metacarpal3', isLeft)
    def ringFingerBones(self , isLeft):
        ret = []
        ret.append(self.boneFor('finger4-1', isLeft))
        ret.append(self.boneFor('finger4-2', isLeft))
        ret.append(self.boneFor('finger4-3', isLeft))
        return ret

    def pinkyFingerParent(self, isLeft): return self.boneFor('metacarpal4', isLeft)
    def pinkyFingerBones(self , isLeft):
        ret = []
        ret.append(self.boneFor('finger5-1', isLeft))
        ret.append(self.boneFor('finger5-2', isLeft))
        ret.append(self.boneFor('finger5-3', isLeft))
        return ret
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for mocap support
    def isMocapCapable(self): return False