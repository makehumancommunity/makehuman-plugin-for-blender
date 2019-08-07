from .capture_armature import *
from ..rig.riginfo import *

import bpy
#===============================================================================
TWITCH_NFRAMES = 5
class AnimationBuffer:
    #===========================================================================
    #                     Called during sensor capture
    #===========================================================================
    def __init__(self, name):
        self.name = name
        self.frameNums = []
        self.joints = []
        self.hands = []
        self.clipPlanes = []

        self.frame = -1
        self.capture = None

    def loadSensorFrame(self, frame, joints, hands, clipPlane):
        self.frameNums.append(frame)
        self.joints.append(joints)
        self.hands.append(hands)
        self.clipPlanes.append(clipPlane)

    # shaves a little off of peaks as well, but may make keyframe reduction easier as well
    def removeTwitching(self, jointDict):
        nTwitches = 0
        lastIdx = len(self.frameNums) - 1 # since looking one in future, can only iterate to one less than total
        for jointName, parentName in jointDict.items():
            for i in range(1, lastIdx):
                prev = self.joints[i - 1][jointName]['location']
                curr = self.joints[i    ][jointName]['location']
                next = self.joints[i + 1][jointName]['location']

                if self.twitched(prev['x'], curr['x'], next['x']):
                    self.joints[i][jointName]['location']['x'] = prev['x']
                    nTwitches += 1

                if self.twitched(prev['y'], curr['y'], next['y']):
                    self.joints[i][jointName]['location']['y'] = prev['y']
                    nTwitches += 1

                if self.twitched(prev['z'], curr['z'], next['z']):
                    self.joints[i][jointName]['location']['z'] = prev['z']
                    nTwitches += 1

        print('number of twitches ' + str(nTwitches))

    def twitched(self, prev, curr, next):
        if prev < curr and curr > next: return True
        if prev > curr and curr < next: return True
        return False

    #===========================================================================
    #                         Called post capture
    #===========================================================================
    def assign(self, rigInfo, baseActionName, mappingToBones, sensorJointDict):
        armature = rigInfo.armature
        if not armature.animation_data:
            armature.animation_data_create()
            armature.animation_data.action = bpy.data.actions.new(armature.name + '-' + baseActionName)

        self.reset()

        self.capture = CaptureArmature(rigInfo, mappingToBones, sensorJointDict)
        bpy.ops.object.mode_set(mode='POSE')

        # - - - - - - - - - - - - - - - - - - - - - - -
        # get the smoothing amount; set to less than 0 to turn off
        self.maxRadiansPerFrame = 0 # radians(bpy.context.scene.MhMaxRotationPerFrame)
        self.doSmoothing = self.maxRadiansPerFrame > 0
        if self.doSmoothing:
             self.prevAsEuler = {}

        for idx, frameNum in enumerate(self.frameNums):
            self.capture.assignAndRetargetFrame(self.joints[idx])
            self.insertFrame(rigInfo, mappingToBones, frameNum)

        self.reset()
        bpy.context.scene.frame_set(0) # puts at first frame, not last
    #===========================================================================
    def reset(self):
        if self.capture is not None:
            self.capture.cleanUp()
            self.capture = None

        self.frame = -1
    #===========================================================================
    def insertFrame(self, rigInfo, mappingToBones, frameNum):
        armature = rigInfo.armature
        for jointName, boneName in mappingToBones.items():
            if boneName is None or boneName not in armature.pose.bones: continue
            if bpy.context.scene.MhExcludeFingers and self.isFinger(boneName): continue

            bone = armature.pose.bones[boneName]
            localMat = armature.convert_space(pose_bone = bone, matrix = bone.matrix, from_space = 'POSE',  to_space = 'LOCAL')
            rot = localMat.to_quaternion()

            # not in use, but wanted on the repo at least once
            if self.doSmoothing:
                asEuler = rot.to_euler("XYZ")
                if boneName in self.prevAsEuler:
                    asEuler.x = self.smooth(self.prevAsEuler[boneName].x, asEuler.x, boneName + 'x')
                    asEuler.y = self.smooth(self.prevAsEuler[boneName].y, asEuler.y, boneName + 'y')
                    asEuler.z = self.smooth(self.prevAsEuler[boneName].z, asEuler.z, boneName + 'z')
                    rot = asEuler.to_quaternion()

                # assign smoothed value for next frame
                self.prevAsEuler[boneName] = asEuler

            bone.rotation_quaternion = rot
            bone.keyframe_insert('rotation_quaternion', frame = frameNum, group = boneName)

        # add translation key for root bone
        bone = armature.pose.bones[rigInfo.root]
        bone.location = localMat.to_translation()
        bone.keyframe_insert('location', frame = frameNum, group = boneName)

    #===========================================================================
    # not currently in use
    def smooth(self, prev, curr, name):
        if prev > curr:
            ret =  prev - self.maxRadiansPerFrame if prev > curr + self.maxRadiansPerFrame else curr
#            if ret != curr: print(name + ' prev greater by ' + ('%.4f' % (prev - curr)) + ', returned ' + ('%.4f' % ret) + ', input ' + ('%.4f' % curr) + ', prev ' + ('%.4f' % prev))
        else:
            ret = prev + self.maxRadiansPerFrame if prev < curr - self.maxRadiansPerFrame else curr
#            if ret != curr: print(name + ' prev less by ' + ('%.4f' % (curr - prev)) + ', returned ' + ('%.4f' % ret) + ', input ' + ('%.4f' % curr) + ', prev ' + ('%.4f' % prev))

        return ret
    #===========================================================================
    def oneRight(self, rigInfo, mappingToBones, sensorJointDict):
        if self.capture is None:
            self.capture = CaptureArmature(rigInfo, mappingToBones, sensorJointDict)

        self.frame = self.frame + 1 if self.frame + 1 < len(self.joints) else 0

        print('--------------------------------------------')
        self.capture.assignAndRetargetFrame(self.joints[self.frame])
