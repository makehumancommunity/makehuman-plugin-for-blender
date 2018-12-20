#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from .riginfo import RigInfo

class CMURigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'CMU Rig', 'LeftUpLeg')

        self.pelvis = 'Hips'
        self.root = 'Hips'
        self.head = 'Head'
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for IK rigging support
    def IKCapable(self): return True
    def clavicle(self, isLeft): return ('Left' if isLeft else 'Right') + 'Shoulder'
    def upperArm(self, isLeft): return ('Left' if isLeft else 'Right') + 'Arm'
    def lowerArm(self, isLeft): return ('Left' if isLeft else 'Right') + 'ForeArm'
    def hand    (self, isLeft): return ('Left' if isLeft else 'Right') + 'Hand'  # also used for amputation
    # - - -
    def thigh   (self, isLeft): return ('Left' if isLeft else 'Right') + 'UpLeg'
    def calf    (self, isLeft): return ('Left' if isLeft else 'Right') + 'Leg' # also used by super.hasFeetOnGround()
    def foot    (self, isLeft): return ('Left' if isLeft else 'Right') + 'Foot' # also used for super.determineExportedUnits()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return False
