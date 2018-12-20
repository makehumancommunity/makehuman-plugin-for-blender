#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from .riginfo import RigInfo

class Kinect2RigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'Kinect2 Rig', 'SpineShoulder')

        self.pelvis = 'SpineMid'
        self.root = 'SpineBase'
        self.head = 'Head'
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def boneFor(baseName, isLeft):
        return baseName + ('Left' if isLeft else 'Right')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
     # for IK rigging support
    def IKCapable(self): return True
    def clavicle(self, isLeft): return Kinect2RigInfo.boneFor('Shoulder', isLeft)
    def upperArm(self, isLeft): return Kinect2RigInfo.boneFor('Elbow'   , isLeft)
    def lowerArm(self, isLeft): return Kinect2RigInfo.boneFor('Wrist'   , isLeft)
    def hand    (self, isLeft): return Kinect2RigInfo.boneFor('Hand'    , isLeft) # also used for amputation
    # - - -
    def thigh   (self, isLeft): return Kinect2RigInfo.boneFor('Knee'    , isLeft)
    def calf    (self, isLeft): return Kinect2RigInfo.boneFor('Ankle'   , isLeft) # also used by super.hasFeetOnGround()
    def foot    (self, isLeft): return Kinect2RigInfo.boneFor('Foot'    , isLeft) # also used for super.determineExportedUnits()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return False
