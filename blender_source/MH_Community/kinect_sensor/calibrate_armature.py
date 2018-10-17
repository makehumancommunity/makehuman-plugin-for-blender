from .to_kinect2 import *

from mathutils import Vector

import bpy
#===============================================================================
# TODO shoulders & fingers
class CalibrateArmature:
    # assumed data is a T-Pose; data can only have one body
    def __init__(self, armature, data):
        self.armature = armature
        self.bonesData = data
        self.diffs = {}
        self.zRateYs = {}
        self.xRateYs = {}

        actualBones = self.armature.data.bones

        # determine changes per bone & add to data
        for boneName in self.bonesData:
            actualBone = actualBones[boneName]
            if actualBone.parent is None: continue

            parentName = actualBone.parent.name

            loc  = self.bonesData[boneName  ]['location']
            pLoc = self.bonesData[parentName]['location']

            # switch Y & Z at the same time
            diff = Vector((loc['x'] - pLoc['x'], loc['z'] - pLoc['z'], loc['y'] - pLoc['y']))
            zRateY = 0 if diff.z == 0 else diff.y / diff.z
            xRateY = 0 if diff.x == 0 else diff.y / diff.x

            # assign into self data, for easier access in other methods
            self.diffs  [boneName] = diff
            self.xRateYs[boneName] = xRateY
            self.zRateYs[boneName] = zRateY

        # determine left / right avgs
        self.xRateAvgs = {}
        self.xRateAvgs['HIPS'] = (abs(self.xRateYs[HIP_LEFT]) + abs(self.xRateYs[HIP_RIGHT])) / 2

        self.zRateAvgs = {}
        self.zRateAvgs['KNEES' ] = (abs(self.zRateYs[KNEE_LEFT ]) + abs(self.zRateYs[KNEE_RIGHT])) / 2
        self.zRateAvgs['ANKLES'] = (abs(self.zRateYs[ANKLE_LEFT]) + abs(self.zRateYs[ANKLE_RIGHT])) / 2
        self.zRateAvgs['FEET'  ] = (abs(self.zRateYs[FOOT_LEFT ]) + abs(self.zRateYs[FOOT_RIGHT ])) / 2

        self.shapeBones()
        bpy.ops.object.mode_set(mode='POSE')

    def requiresCalibration(self):
        # called from shapeBones, where already in EDIT mode, set here for thoroughness
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        bone = eBones[HIP_LEFT ]
        if bone.tail.y != bone.head.y: return False

        bone = eBones[HIP_RIGHT]
        if bone.tail.y != bone.head.y: return False

        return True

    def log(self):
        rootY = self.bonesData[ROOT_BONE]['location']['z']
        msg = 'Bone,X,Y,Z,,"Depth vs Root",,"Diff X","Diff Y","Diff Z",,"X rate Y",Avg,"Z Rate Y",Avg\n'
        msg += self.logBone(ROOT_BONE, rootY)
        msg += self.logBone(SPINE_MID     , rootY)
        msg += self.logBone(SPINE_SHOULDER, rootY)
        msg += self.logBone(NECK          , rootY)
        msg += self.logBone(HEAD          , rootY)
        msg += '\n\n'
        msg += self.logBone(SHOULDER_LEFT , rootY)
        msg += self.logBone(SHOULDER_RIGHT, rootY)
        msg += '\n'
        msg += self.logBone(ELBOW_LEFT    , rootY)
        msg += self.logBone(ELBOW_RIGHT   , rootY)
        msg += '\n'
        msg += self.logBone(WRIST_LEFT    , rootY)
        msg += self.logBone(WRIST_RIGHT   , rootY)
        msg += '\n'
        msg += self.logBone(HAND_LEFT     , rootY)
        msg += self.logBone(HAND_RIGHT    , rootY)
        msg += '\n'
        msg += self.logBone(HAND_TIP_LEFT , rootY)
        msg += self.logBone(HAND_TIP_RIGHT, rootY)
        msg += '\n'
        msg += self.logBone(THUMB_LEFT    , rootY)
        msg += self.logBone(THUMB_RIGHT   , rootY)
        msg += '\n\n'
        msg += self.logBone(HIP_LEFT      , rootY, self.xRateAvgs['HIPS'])
        msg += self.logBone(HIP_RIGHT     , rootY)
        msg += '\n'
        msg += self.logBone(KNEE_LEFT     , rootY, 0, self.zRateAvgs['KNEES' ])
        msg += self.logBone(KNEE_RIGHT    , rootY)
        msg += '\n'
        msg += self.logBone(ANKLE_LEFT    , rootY, 0, self.zRateAvgs['ANKLES'])
        msg += self.logBone(ANKLE_RIGHT   , rootY)
        msg += '\n'
        msg += self.logBone(FOOT_LEFT     , rootY, 0, self.zRateAvgs['FEET'  ])
        msg += self.logBone(FOOT_RIGHT    , rootY)

        print(msg)

    def logBone(self, boneName, rootY, xRateAvg = 0, zRateAvg = 0):
        loc = self.bonesData[boneName]['location']
        ret  = '"' + boneName + '",' + ('%.4f' % loc['x']) + ',' + ('%.4f' % loc['z']) + ',' + ('%.4f' % loc['y'])
        ret +=  ',,' + ('%.4f' % (loc['z'] - rootY))
        if boneName == ROOT_BONE: return ret + '\n'

        diff   = self.diffs    [boneName]
        ret += ',,' + ('%.4f' % diff.x) + ',' + ('%.4f' % diff.y) + ',' + ('%.4f' % diff.z)

        ret += ',,' + ('%.4f' % self.xRateYs[boneName]) + ','
        ret += ('%.4f' % xRateAvg) if xRateAvg != 0 else ','

        ret += ',' + ('%.4f' % self.zRateYs[boneName]) + ','
        ret += ('%.4f' % zRateAvg) if zRateAvg != 0 else ','
        return ret + '\n'

    def shapeBones(self):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        if not self.requiresCalibration() :
            print(self.armature.name + ' armature has already been calibrated')
            return

        print ('calibration of ' + self.armature.name)
        self.log()

        # spine mid is further forward (less) from root
        bone = eBones[SPINE_MID]
        zDiff = bone.tail.z - bone.head.z
        bone.tail.y = bone.head.y + (zDiff * self.zRateYs[bone.name])

        # spine shoulder is further forward (less) from spine mid
        bone = eBones[SPINE_SHOULDER]
        zDiff = bone.tail.z - bone.head.z
        bone.tail.y = bone.head.y + (zDiff *self.zRateYs[bone.name])

        # neck is further forward (less) from spine shoulder
        bone = eBones[NECK]
        zDiff = bone.tail.z - bone.head.z
        bone.tail.y = bone.head.y + (zDiff * self.zRateYs[bone.name])

        # head is further back (more) from neck
        bone = eBones[HEAD]
        zDiff = bone.tail.z - bone.head.z
        bone.tail.y = bone.head.y + (zDiff * self.zRateYs[bone.name])

        # - - - - - - - - -
        # hip tails are closer to the from of the body from sensor; make level
        bone = eBones[HIP_LEFT ]
        xDiff = bone.tail.x - bone.head.x # head / root is zero, so subtract just for clarity

        bone.tail.y = bone.head.y - (self.xRateAvgs['HIPS'] * xDiff)
        bone.tail.z = bone.head.z

        bone = eBones[HIP_RIGHT]
        bone.tail.y = bone.head.y - (self.xRateAvgs['HIPS'] * xDiff)
        bone.tail.z = bone.head.z

        # - - - - - - - - -
        # knee is further back (more) from hip
        # diff assignment order opposite of upper body adjustments, since bone tail below head
        # also knee widen from hips
        bone = eBones[KNEE_LEFT]
        zDiff = bone.head.z - bone.tail.z
        bone.tail.y = bone.head.y + (self.zRateAvgs['KNEES' ] * zDiff)
    #    bone.tail.x = bone.head.x - (zDiff * 0.12)

        bone = eBones[KNEE_RIGHT]
        zDiff = bone.head.z - bone.tail.z
        bone.tail.y = bone.head.y + (self.zRateAvgs['KNEES' ] * zDiff)
    #    bone.tail.x = bone.head.x + (zDiff * 0.12)

        # - - - - - - - - -
        # ankle is further back (more) from knee
        # also ankle narrows from knees
        bone = eBones[ANKLE_LEFT]
        zDiff = bone.head.z - bone.tail.z
        bone.tail.y = bone.head.y + (self.zRateAvgs['ANKLES'] * zDiff)
    #    bone.tail.x = bone.head.x + (zDiff * 0.02)

        bone = eBones[ANKLE_RIGHT]
        zDiff = bone.head.z - bone.tail.z
        bone.tail.y = bone.head.y + (self.zRateAvgs['ANKLES'] * zDiff)
    #    bone.tail.x = bone.head.x - (zDiff * 0.02)

        # - - - - - - - - -
        # foot is further forward (less) from ankle
        # sign opposite of upper body adjustments, since bone tail below head
        bone = eBones[FOOT_LEFT]
        zDiff = bone.head.z - bone.tail.z
        bone.tail.y = bone.head.y - (self.zRateAvgs['FEET'  ] * zDiff)

        bone = eBones[FOOT_RIGHT]
        zDiff = bone.head.z - bone.tail.z
        bone.tail.y = bone.head.y - (self.zRateAvgs['FEET'  ] * zDiff)