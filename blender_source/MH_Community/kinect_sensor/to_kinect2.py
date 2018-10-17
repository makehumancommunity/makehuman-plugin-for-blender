from MH_Community.rig_info import *
from MH_Community.bone_surgery import *

import bpy

ROOT_BONE      = 'SpineBase'
SPINE_BASE     = ROOT_BONE
SPINE_MID      = 'SpineMid'
NECK           = 'Neck'
HEAD           = 'Head'
SHOULDER_LEFT  = 'ShoulderLeft'
ELBOW_LEFT     = 'ElbowLeft'
WRIST_LEFT     = 'WristLeft'
HAND_LEFT      = 'HandLeft'
SHOULDER_RIGHT = 'ShoulderRight'
ELBOW_RIGHT    = 'ElbowRight'
WRIST_RIGHT    = 'WristRight'
HAND_RIGHT     = 'HandRight'
HIP_LEFT       = 'HipLeft'
KNEE_LEFT      = 'KneeLeft'
ANKLE_LEFT     = 'AnkleLeft'
FOOT_LEFT      = 'FootLeft'
HIP_RIGHT      = 'HipRight'
KNEE_RIGHT     = 'KneeRight'
ANKLE_RIGHT    = 'AnkleRight'
FOOT_RIGHT     = 'FootRight'
SPINE_SHOULDER = 'SpineShoulder'
HAND_TIP_LEFT  = 'HandTipLeft'
THUMB_LEFT     = 'ThumbLeft'
HAND_TIP_RIGHT = 'HandTipRight'
THUMB_RIGHT    = 'ThumbRight'

# in the same order reported by kinect v2, but not really important
KINECT_BONES = [
    SPINE_BASE    ,
    SPINE_MID     ,
    NECK          ,
    HEAD          ,
    SHOULDER_LEFT ,
    ELBOW_LEFT    ,
    WRIST_LEFT    ,
    HAND_LEFT     ,
    SHOULDER_RIGHT,
    ELBOW_RIGHT   ,
    WRIST_RIGHT   ,
    HAND_RIGHT    ,
    HIP_LEFT      ,
    KNEE_LEFT     ,
    ANKLE_LEFT    ,
    FOOT_LEFT     ,
    HIP_RIGHT     ,
    KNEE_RIGHT    ,
    ANKLE_RIGHT   ,
    FOOT_RIGHT    ,
    SPINE_SHOULDER,
    HAND_TIP_LEFT ,
    THUMB_LEFT    ,
    HAND_TIP_RIGHT,
    THUMB_RIGHT
]
#===============================================================================
class ToKinectV2():
    def __init__(self, rigInfo):
        self.rigInfo = rigInfo

    def convert(self):
        armature = self.rigInfo.armature

        # get root bone length while in POSE mode for later
        bpy.ops.object.mode_set(mode='POSE')
        rootLength = armature.pose.bones[self.rigInfo.root].length
        print ('root len ' + str(rootLength))

        # find all meshes which use this armature
        meshes = self.rigInfo.getMeshesForRig(bpy.context.scene)

        # nuke all the facial expression bones
        BoneSurgery.amputate(armature, meshes, 'head')
        armature.data.bones['head'].name = HEAD

        # spine & breast reductions
        weightToBoneName = 'spine05'
        BoneSurgery.deleteBone(armature, meshes, 'spine04', weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, 'spine03', weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = SPINE_MID

        weightToBoneName = 'spine02'
        BoneSurgery.deleteBone(armature, meshes, self.rigInfo.boneFor('breast', True ), weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, self.rigInfo.boneFor('breast', False), weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, 'spine01', weightToBoneName)
        armature.data.bones[weightToBoneName].name = SPINE_SHOULDER

        # neck reduction
        weightToBoneName = 'neck01'
        BoneSurgery.deleteBone(armature, meshes, 'neck02', weightToBoneName)
        BoneSurgery.deleteBone(armature, meshes, 'neck03', weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = NECK

        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones

        self.processSide(armature, meshes, True )
        self.processSide(armature, meshes, False)

        # joint spine neck & the height of clavicles
        rightShoulderName = Kinect2RigInfo.boneFor('Shoulder', False) # does not matter which side
        z = eBones[rightShoulderName].head.z
        y = eBones[rightShoulderName].head.y
        eBones[SPINE_SHOULDER].tail.z = z
        eBones[SPINE_SHOULDER].tail.y = y

        # not required since connecting
#        eBones[NECK].head.z = z
#        eBones[NECK].head.y = y

        # connect everything
        # except spine mid, so Ik snap-on works; prior to changing Root to get separation
        ToKinectV2.connectBones(armature, True)
        eBones[SPINE_MID].use_connect = False
        eBones[HIP_LEFT ].use_connect = False
        eBones[HIP_RIGHT].use_connect = False

        # Root bone work
        eRoot = eBones['root']
        eRoot.head.y = eRoot.tail.y # make vertical, so offset to empty used for capture can be easier to place
        # move root bone to ground
        eRoot.tail.z = rootLength
        eRoot.head.z = 0
        #eRoot.head.z = eRoot.head.z - rootLength
        armature.data.bones['root'].name = SPINE_BASE

        self.assignForCalibrationDetection(armature)
        self.unlockLocations(armature.pose.bones)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # The tail y of hip bones are re-assigned in calibration, so setting to head
    # will not be permanent.  In any case, values almost the same anyway.
    def assignForCalibrationDetection(self, armature):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones

        bone = eBones[HIP_LEFT ]
        bone.tail.y = bone.head.y

        bone = eBones[HIP_RIGHT]
        bone.tail.y = bone.head.y

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def processSide(self, armature, meshes, isLeft):
        # amputate the toe(s)
        sheerBoneName = self.rigInfo.boneFor('foot', isLeft)
        BoneSurgery.amputate(armature, meshes, sheerBoneName)
        armature.data.bones[sheerBoneName].name = Kinect2RigInfo.boneFor('Foot', isLeft)

        #shorten the lower & upper legs to 2 total bones
        weightToBoneName = self.rigInfo.boneFor('lowerleg01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, self.rigInfo.boneFor('lowerleg02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor('Ankle', isLeft)

        weightToBoneName = self.rigInfo.boneFor('upperleg01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, self.rigInfo.boneFor('upperleg02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor('Knee', isLeft)

        # shorten the shoulder
        weightToBoneName = self.rigInfo.boneFor('clavicle', isLeft)
        BoneSurgery.deleteBone(armature, meshes, self.rigInfo.boneFor('shoulder01', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor('Shoulder', isLeft)

        # shorten the upper arm
        weightToBoneName = self.rigInfo.boneFor('upperarm01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, self.rigInfo.boneFor('upperarm02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor('Elbow', isLeft)

        # shorten the lower arm
        weightToBoneName = self.rigInfo.boneFor('lowerarm01', isLeft)
        BoneSurgery.deleteBone(armature, meshes, self.rigInfo.boneFor('lowerarm02', isLeft), weightToBoneName, True)
        armature.data.bones[weightToBoneName].name = Kinect2RigInfo.boneFor('Wrist', isLeft)

        # shorten the thumb
        sheerBoneName = self.rigInfo.thumbParent(isLeft)
        BoneSurgery.amputate(armature, meshes, sheerBoneName)
        armature.data.bones[sheerBoneName].name = Kinect2RigInfo.boneFor('Thumb', isLeft)

        # shorten all fingers for later consolidation to 1, middles done differently, so bone ends at tip of finger
        indexes = self.rigInfo.indexFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, indexes[0])

        middles = self.rigInfo.middleFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, middles[0])
        BoneSurgery.deleteBone(armature, meshes, middles[1], middles[0])
        BoneSurgery.deleteBone(armature, meshes, middles[2], middles[0])

        rings = self.rigInfo.ringFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, rings[0])

        pinkies = self.rigInfo.pinkyFingerBones(isLeft)
        BoneSurgery.amputate(armature, meshes, pinkies[0])

        # consolidate fingers
        BoneSurgery.deleteBone(armature, meshes, indexes[0], middles[0])
        BoneSurgery.deleteBone(armature, meshes, rings  [0], middles[0])
        BoneSurgery.deleteBone(armature, meshes, pinkies[0], middles[0])
        armature.data.bones[middles[0]].name = Kinect2RigInfo.boneFor('HandTip', isLeft)

        # finger consolidation of wrist
        weightToBoneName = self.rigInfo.boneFor('wrist', isLeft)

        fingerBaseName = self.rigInfo.indexFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName)

        fingerBaseName = self.rigInfo.middleFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName)

        fingerBaseName = self.rigInfo.ringFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName, True)

        fingerBaseName = self.rigInfo.pinkyFingerParent(isLeft)
        BoneSurgery.deleteBone(armature, meshes, fingerBaseName, weightToBoneName)

        # rename the MH wrist to the hand
        handName = Kinect2RigInfo.boneFor('Hand', isLeft)
        armature.data.bones[self.rigInfo.boneFor('wrist', isLeft)].name = handName

        # rename pelvis sides, and re-parent for IK; always want the parent to be consistent
        hipName = Kinect2RigInfo.boneFor('Hip', isLeft)
        armature.data.bones[self.rigInfo.boneFor('pelvis', isLeft)].name = hipName

        # change to edit mode to do some reparenting & moving (probably already that way)
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones

        # parent thumb up higher & hip to spine mid
        eBones[Kinect2RigInfo.boneFor('Thumb', isLeft)].parent = eBones[Kinect2RigInfo.boneFor('Wrist', isLeft)]
       # eBones[hipName].parent = eBones[SPINE_MID]
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unlockLocations(self, poseBones):
        bpy.ops.object.mode_set(mode='POSE')
        for bone in poseBones:
            bone.lock_location[0] = False
            bone.lock_location[1] = False
            bone.lock_location[2] = False

            #bone.rotation_mode = 'XYZ'
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # static so can be called from kinect_runtime
    @staticmethod
    def connectBones(armature, value = True):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones

        for name in KINECT_BONES:
            # The root bone cannot be connected, so skip & leave as is
            # Finger bones could have been amputated, when called from kinect_runtime
            if name != SPINE_BASE and name in armature.data.bones:
                eBones[name].use_connect = value