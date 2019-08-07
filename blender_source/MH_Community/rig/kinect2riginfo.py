#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from .riginfo import RigInfo
from .bonesurgery import BoneSurgery

# static values of the actual bone names
K2_ROOT        = 'K2-Root'
K2_SPINE_LOWER = 'K2-SpineLower'
K2_SPINE_UPPER = 'K2-SpineUpper'

K2_NECK        = 'K2-Neck'
K2_HEAD        = 'K2-Head'

K2_SHOULDER    = 'K2-Shoulder'
K2_ARM         = 'K2-Arm'
K2_FORE_ARM    = 'K2-ForeArm'
K2_HAND        = 'K2-Hand'
K2_HAND_TIP    = 'K2-HandTip'
K2_THUMB       = 'K2-Thumb'

K2_HIP         = 'K2-Hip'
K2_THIGH       = 'K2-Thigh'
K2_CALF        = 'K2-Calf'
K2_FOOT        = 'K2-Foot'

#===============================================================================
class Kinect2RigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'Kinect2 Rig', K2_SPINE_UPPER)

        self.pelvis = K2_SPINE_LOWER
        self.root = K2_ROOT
        self.head = K2_HEAD
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def boneFor(baseName, isLeft):
        return baseName + ('.L' if isLeft else '.R')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for kinect animation scaling
    def getSpineBaseHeightWorldSpace(self):
        spineBaseBone = self.armature.pose.bones[self.pelvis]
        worldMat = self.armature.convert_space(pose_bone = spineBaseBone, matrix = spineBaseBone.matrix, from_space = 'POSE',  to_space = 'WORLD')
        return worldMat.to_translation()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
     # for IK rigging support
    def IKCapable(self): return True
    def clavicle(self, isLeft): return Kinect2RigInfo.boneFor(K2_SHOULDER, isLeft)
    def upperArm(self, isLeft): return Kinect2RigInfo.boneFor(K2_ARM     , isLeft)
    def lowerArm(self, isLeft): return Kinect2RigInfo.boneFor(K2_FORE_ARM, isLeft)
    def hand    (self, isLeft): return Kinect2RigInfo.boneFor(K2_HAND    , isLeft) # also used for amputation
    # - - -
    def thigh   (self, isLeft): return Kinect2RigInfo.boneFor(K2_THIGH   , isLeft)
    def calf    (self, isLeft): return Kinect2RigInfo.boneFor(K2_CALF    , isLeft) # also used by super.hasFeetOnGround()
    def foot    (self, isLeft): return Kinect2RigInfo.boneFor(K2_FOOT    , isLeft) # also used for super.determineExportedUnits()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return False
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for mocap support
    def isMocapCapable(self): return True

    # the retargeting constraint space for arm bones is 'WORLD', while 'LOCAL' for rest
    def isArmBone(self, boneName):
        return K2_SHOULDER in boneName or K2_ARM in boneName or K2_FORE_ARM in boneName or K2_HAND in boneName or K2_HAND_TIP in boneName or K2_THUMB in boneName

    def isFinger(self, boneName):
        return K2_HAND_TIP in boneName or K2_THUMB in boneName

    def getSensorMapping(self, sensorType = 'KINECT2'):
        if sensorType == 'KINECT2':

            return {
            # keys are kinect joints names coming from the sensor
            # values are bone names whose tail is at the joint
            'SpineBase'    : None,
            'SpineMid'     : self.pelvis,
            'SpineShoulder': K2_SPINE_UPPER,

            'Neck'         : K2_NECK,
            'Head'         : self.head,

            'ShoulderLeft' : K2_SHOULDER + '.L',
            'ElbowLeft'    : K2_ARM + '.L',
            'WristLeft'    : K2_FORE_ARM + '.L',
            'HandLeft'     : K2_HAND + '.L',
            'HandTipLeft'  : K2_HAND_TIP + '.L',
            'ThumbLeft'    : K2_THUMB + '.L',

            'ShoulderRight': K2_SHOULDER + '.R',
            'ElbowRight'   : K2_ARM + '.R',
            'WristRight'   : K2_FORE_ARM + '.R',
            'HandRight'    : K2_HAND + '.R',
            'HandTipRight' : K2_HAND_TIP + '.R',
            'ThumbRight'   : K2_THUMB + '.R',

            'HipLeft'      : K2_HIP + '.L',
            'KneeLeft'     : K2_THIGH + '.L',
            'AnkleLeft'    : K2_CALF + '.L',
            'FootLeft'     : K2_FOOT + '.L',

            'HipRight'     : K2_HIP + '.R',
            'KneeRight'    : K2_THIGH + '.R',
            'AnkleRight'   : K2_CALF + '.R',
            'FootRight'    : K2_FOOT + '.R',
        }
        # add next sensor, eg., KINECT_AZURE
        elif sensorType == 'KINECT_AZURE':
            return None

        # this rig not supported by this sensor
        else: return None

    @staticmethod
    def convertFromDefault(defaultRigInfo):
        armature = defaultRigInfo.armature

        # get root bone length while in POSE mode for later
        bpy.ops.object.mode_set(mode='POSE')
        rootLength = armature.pose.bones[defaultRigInfo.root].length
        print ('root len ' + str(rootLength))

        # find all meshes which use this armature
        meshes = defaultRigInfo.getMeshesForRig(bpy.context.scene)

        # nuke all the facial expression bones
        BoneSurgery.amputate(armature, meshes, 'head')
        armature.data.bones[defaultRigInfo.head].name = K2_HEAD

        # spine & breast reductions
        weightToBoneName = 'spine05'
        BoneSurgery.deleteBone(armature, meshes, 'spine04', weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, 'spine03', weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = K2_SPINE_LOWER

        weightToBoneName = 'spine02'
        BoneSurgery.deleteBone(armature, meshes, defaultRigInfo.boneFor('breast', True ), weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, defaultRigInfo.boneFor('breast', False), weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, 'spine01', weightToBoneName)
        armature.data.bones[weightToBoneName].name = K2_SPINE_UPPER

        # neck reduction
        weightToBoneName = 'neck01'
        BoneSurgery.deleteBone(armature, meshes, 'neck02', weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, 'neck03', weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = K2_NECK

        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones

        Kinect2RigInfo.processSide(defaultRigInfo, meshes, True )
        Kinect2RigInfo.processSide(defaultRigInfo, meshes, False)

        # joint spine neck & the height of clavicles
        shoulderBone = eBones[K2_SHOULDER + '.R'] # does not matter which side
        z = shoulderBone.head.z
        y = shoulderBone.head.y
        eBones[K2_SPINE_UPPER].tail.z = z
        eBones[K2_SPINE_UPPER].tail.y = y

        # connect everything
        BoneSurgery.connectSkeleton(armature, True, [K2_THUMB + '.L', K2_THUMB + '.R'])

        # Root bone work, # make vertical, with head a origin, so offset to empty used for capture can be easier to place
        eRoot = eBones['root']
        eRoot.head.x = 0
        eRoot.head.y = 0
        eRoot.head.z = 0

        eRoot.tail.x = 0
        eRoot.tail.y = 0
        eRoot.tail.z = eBones[K2_SPINE_LOWER].head.z

        # also make spine lower vertical
        eBones[K2_SPINE_LOWER].tail.y = 0

        armature.data.bones['root'].name = K2_ROOT

        # certain things kinect seems to want are always the same, so make them defaults
        bone = eBones[ K2_HIP + '.L' ]
        xDiff = abs(bone.head.x - bone.tail.x)
        bone.tail.y = bone.head.y - (0.5 * xDiff)

        bone = eBones[ K2_HIP + '.R' ]
        bone.tail.y = bone.head.y - (0.5 * xDiff)

        Kinect2RigInfo.unlockLocations(armature.pose.bones)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def processSide(defaultRigInfo, meshes, isLeft):
        armature = defaultRigInfo.armature

        # amputate the toe(s)
        sheerBoneName = defaultRigInfo.boneFor('foot', isLeft)
        BoneSurgery.amputate(armature, meshes, sheerBoneName)
        armature.data.bones[sheerBoneName].name = Kinect2RigInfo.boneFor(K2_FOOT, isLeft)

        #shorten the lower & upper legs to 2 total bones
        weightToBoneName = defaultRigInfo.boneFor('lowerleg01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, defaultRigInfo.boneFor('lowerleg02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor(K2_CALF, isLeft)

        weightToBoneName = defaultRigInfo.boneFor('upperleg01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, defaultRigInfo.boneFor('upperleg02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor(K2_THIGH, isLeft)

        # shorten the shoulder
        weightToBoneName = defaultRigInfo.boneFor('clavicle', isLeft)
        BoneSurgery.deleteBone(armature, meshes, defaultRigInfo.boneFor('shoulder01', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor(K2_SHOULDER, isLeft)

        # shorten the upper arm
        weightToBoneName = defaultRigInfo.boneFor('upperarm01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, defaultRigInfo.boneFor('upperarm02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor(K2_ARM, isLeft)

        # shorten the lower arm
        weightToBoneName = defaultRigInfo.boneFor('lowerarm01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, defaultRigInfo.boneFor('lowerarm02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor(K2_FORE_ARM, isLeft)

        # shorten the thumb
        sheerBoneName = defaultRigInfo.thumbParent(isLeft)
        BoneSurgery.amputate(armature, meshes, sheerBoneName)
        armature.data.bones[sheerBoneName].name = Kinect2RigInfo.boneFor(K2_THUMB, isLeft)

        # shorten all fingers for later consolidation to 1, middles done differently, so bone ends at tip of finger
        indexes = defaultRigInfo.indexFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, indexes[0])

        middles = defaultRigInfo.middleFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, middles[0])
        BoneSurgery.deleteBone(armature, meshes, middles[1], middles[0])
        BoneSurgery.deleteBone(armature, meshes, middles[2], middles[0])

        rings = defaultRigInfo.ringFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, rings[0])

        pinkies = defaultRigInfo.pinkyFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, pinkies[0])

        # consolidate fingers
        BoneSurgery.deleteBone(armature, meshes, indexes[0], middles[0])
        BoneSurgery.deleteBone(armature, meshes, rings  [0], middles[0])
        BoneSurgery.deleteBone(armature, meshes, pinkies[0], middles[0])
        armature.data.bones[middles[0]].name = Kinect2RigInfo.boneFor(K2_HAND_TIP, isLeft)

        # finger consolidation of wrist
        weightToBoneName = defaultRigInfo.boneFor('wrist', isLeft)

        fingerBaseName = defaultRigInfo.indexFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName)

        fingerBaseName = defaultRigInfo.middleFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName)

        fingerBaseName = defaultRigInfo.ringFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName, True)

        fingerBaseName = defaultRigInfo.pinkyFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName)

        # rename the MH wrist to the hand
        handName = Kinect2RigInfo.boneFor(K2_HAND, isLeft)
        armature.data.bones[defaultRigInfo.boneFor('wrist', isLeft)].name = handName

        # rename pelvis sides, and re-parent for IK; always want the parent to be consistent
        hipName = Kinect2RigInfo.boneFor(K2_HIP, isLeft)
        armature.data.bones[defaultRigInfo.boneFor('pelvis', isLeft)].name = hipName

        # change to edit mode to do some reparenting & moving (probably already that way)
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones
        eBones[Kinect2RigInfo.boneFor(K2_HAND_TIP, isLeft)].roll = 0
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # not really needed anymore with the model not exported / imported anymore
    @staticmethod
    def unlockLocations(poseBones):
        bpy.ops.object.mode_set(mode='POSE')
        for bone in poseBones:
            bone.lock_location[0] = False
            bone.lock_location[1] = False
            bone.lock_location[2] = False
