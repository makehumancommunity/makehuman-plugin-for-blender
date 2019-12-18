#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from . import RigInfo

class GameRigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'Game Rig', 'ball_r')

        self.pelvis = 'pelvis'
        self.root = 'Root'
        self.head = 'head'
        self.neckBase = 'neck_01'
        self.upperSpine = 'spine_03'
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for IK rigging & mocap support
    def IKCapable(self): return True
    def clavicle(self, isLeft, forMocap = False): return 'clavicle_' + ('l' if isLeft else 'r')
    def upperArm(self, isLeft, forMocap = False): return 'upperarm_' + ('l' if isLeft else 'r')
    def lowerArm(self, isLeft, forMocap = False): return 'lowerarm_' + ('l' if isLeft else 'r')
    def hand    (self, isLeft, forMocap = False): return 'hand_'     + ('l' if isLeft else 'r') # also used for amputation
    def handTip (self, isLeft, forMocap = False): return None # for mocap only, not IK
    def thumb   (self, isLeft, forMocap = False): return None # for mocap only, not IK
    # - - -
    def hip     (self, isLeft, forMocap = False): return None # for mocap only, not IK
    def thigh   (self, isLeft, forMocap = False): return 'thigh_'    + ('l' if isLeft else 'r')
    def calf    (self, isLeft, forMocap = False): return 'calf_'     + ('l' if isLeft else 'r') # also used by super.hasFeetOnGround()
    def foot    (self, isLeft, forMocap = False): return 'foot_'     + ('l' if isLeft else 'r') # also used for super.determineExportedUnits()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return self.pinkyFingerParent(False) in self.armature.data.bones
    def thumbParent(self, isLeft): return 'thumb_01_' + ('l' if isLeft else 'r')
    def thumbBones (self, isLeft):
        ret = []
        ret.append('thumb_02_' + ('l' if isLeft else 'r'))
        ret.append('thumb_03_' + ('l' if isLeft else 'r'))
        return ret

    def indexFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def indexFingerBones (self, isLeft):
        ret = []
        ret.append('index_01_' + ('l' if isLeft else 'r'))
        ret.append('index_02_' + ('l' if isLeft else 'r'))
        ret.append('index_03_' + ('l' if isLeft else 'r'))
        return ret

    def middleFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def middleFingerBones(self , isLeft):
        ret = []
        ret.append('middle_01_' + ('l' if isLeft else 'r'))
        ret.append('middle_02_' + ('l' if isLeft else 'r'))
        ret.append('middle_03_' + ('l' if isLeft else 'r'))
        return ret

    def ringFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def ringFingerBones(self , isLeft):
        ret = []
        ret.append('ring_01_' + ('l' if isLeft else 'r'))
        ret.append('ring_02_' + ('l' if isLeft else 'r'))
        ret.append('ring_03_' + ('l' if isLeft else 'r'))
        return ret

    def pinkyFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def pinkyFingerBones(self , isLeft):
        ret = []
        ret.append('pinky_01_' + ('l' if isLeft else 'r'))
        ret.append('pinky_02_' + ('l' if isLeft else 'r'))
        ret.append('pinky_03_' + ('l' if isLeft else 'r'))
        return ret
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for mocap support
    def isMocapCapable(self): return True