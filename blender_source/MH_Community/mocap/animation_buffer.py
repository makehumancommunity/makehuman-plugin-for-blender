from .capture_armature import *
from ..rig.riginfo import *

import bpy
#===============================================================================
class AnimationBuffer:
    #===========================================================================
    #                     Called during sensor capture
    #===========================================================================
    def __init__(self, name, firstBody):
        self.name = name
        self.firstBody = firstBody
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

        print('number of twitches for ' + self.name + ': ' + str(nTwitches) + ', over ' + str(len(self.frameNums)) + ' frames')

    def twitched(self, prev, curr, next):
        if prev < curr and curr > next: return True
        if prev > curr and curr < next: return True
        return False

    #===========================================================================
    #                         Called post capture
    #===========================================================================
    def assign(self, rigInfo, baseActionName, sensorMappingToBones, sensorJointDict):
        current_mode = bpy.context.object.mode

        armature = rigInfo.armature
        # when a previous action is assigned, unlink it from https://developer.blender.org/T51011
        # or problems like here appear https://blender.stackexchange.com/questions/148456/add-multiple-actions-to-an-armature
        if armature.animation_data and armature.animation_data.action:
            # save last action, so it does not get removed without user doing something
            armature.animation_data.action.use_fake_user = True

            priorAreaType = bpy.context.area.type
            bpy.context.area.type = 'DOPESHEET_EDITOR'
            bpy.context.space_data.mode = 'ACTION'
            bpy.ops.action.unlink()
            bpy.context.area.type = priorAreaType

        self.reset()
        self.capture = CaptureArmature(rigInfo, sensorMappingToBones, sensorJointDict, self.firstBody)

        for idx, frameNum in enumerate(self.frameNums):
            self.capture.assignAndRetargetFrame(self.joints[idx])
            self.insertFrame(rigInfo, sensorMappingToBones, frameNum)

        self.reset()
        bpy.context.scene.frame_set(0) # puts at first frame, not last
        armature.animation_data.action.name = armature.name + '-' + baseActionName

        bpy.ops.object.mode_set(mode=current_mode)
    #===========================================================================
    def reset(self):
        if self.capture is not None:
            self.capture.cleanUp()
            self.capture = None

        self.frame = -1
    #===========================================================================
    def insertFrame(self, rigInfo, sensorMappingToBones, frameNum):
        armature = rigInfo.armature
        for jointName, boneName in sensorMappingToBones.items():
            if boneName is None or boneName not in armature.pose.bones: continue
            if bpy.context.scene.MhExcludeFingers and rigInfo.isFinger(boneName): continue

            bone = armature.pose.bones[boneName]
            localMat = armature.convert_space(pose_bone = bone, matrix = bone.matrix, from_space = 'POSE',  to_space = 'LOCAL')
            rot = localMat.to_quaternion()

            bone.rotation_quaternion = rot
            bone.keyframe_insert('rotation_quaternion', frame = frameNum, group = boneName)

        # add translation key for root bone
        bone = armature.pose.bones[rigInfo.root]
        localMat = armature.convert_space(pose_bone = bone, matrix = bone.matrix, from_space = 'POSE',  to_space = 'LOCAL')
        bone.location = localMat.to_translation()
        bone.keyframe_insert('location', frame = frameNum, group = boneName)

    #===========================================================================
    def oneRight(self, rigInfo, sensorMappingToBones, sensorJointDict):
        if self.capture is None:
            self.capture = CaptureArmature(rigInfo, sensorMappingToBones, sensorJointDict, self.firstBody)

        self.frame = self.frame + 1 if self.frame + 1 < len(self.joints) else 0

        print('--------------------------------------------')
        self.capture.assignAndRetargetFrame(self.joints[self.frame])
