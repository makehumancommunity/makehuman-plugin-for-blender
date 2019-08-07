from ..rig.riginfo import *

import bpy
#===============================================================================
class KeyFrameReduction():

    def __init__(self, rigInfo, minRetracementPct):
        print('----------------------\nminRetracement%:' + str(minRetracementPct))
        self.armature = rigInfo.armature
        self.action = self.armature.animation_data.action

        self.minRetracementRatio = minRetracementPct / 100

        self.keyBones = []
        self.keyBones.append(rigInfo.upperArm( True))
        self.keyBones.append(rigInfo.upperArm(False))
        self.keyBones.append(rigInfo.lowerArm( True))
        self.keyBones.append(rigInfo.lowerArm(False))
        self.keyBones.append(rigInfo.calf    ( True))
        self.keyBones.append(rigInfo.calf    (False))

        self.rootBone = rigInfo.root

        self.nSwitches = []
        self.frames = dict() # use dictionary, so frames common amoung bones only listed once
        for fcurve in self.action.fcurves:
            for key in fcurve.keyframe_points:
                frame = key.co.x
                self.frames[frame] = True # actual value has no meaning

        self.frames = sorted(self.frames)
        self.nFrames = len(self.frames)

        self.nSwitches = []
        for idx in range(self.nFrames):
            self.nSwitches.append(0)

        bpy.ops.object.mode_set(mode='POSE')
        for boneName in self.keyBones:
            values = self.getRotationValuesFor(self.armature.pose.bones[boneName])
            print(self.setReversals(values) + " for " + boneName)

        self.nukeNonKeyFrames()

    def getRotationValuesFor(self, bone):
        rotations = []
        for idx in range(self.nFrames):
            bpy.context.scene.frame_set(self.frames[idx])
            rotations.append(bone.rotation_quaternion.to_euler("XYZ") if bone.rotation_mode == 'QUATERNION' else bone.rotation_euler)
        return rotations

    def nukeNonKeyFrames(self):
        # always keep the first frame & last frame
        for idx in range(1, self.nFrames - 1):
            if self.nSwitches[idx] > 0: continue

            for bone in self.armature.pose.bones:
                property = 'rotation_quaternion' if bone.rotation_mode == 'QUATERNION' else 'rotation_euler'
                bone.keyframe_delete(property, -1, self.frames[idx])
                if bone.name == self.rootBone:
                    bone.keyframe_delete('location', -1, self.frames[idx])

    def setReversals(self, values):
        firstValue  = values[0]
        secondValue = values[1]

        xUp = secondValue.x - firstValue.x > 0
        xWaterMark = secondValue.x
        yUp = secondValue.y - firstValue.y > 0
        yWaterMark = secondValue.y
        zUp = secondValue.z - firstValue.z > 0
        zWaterMark = secondValue.z

        thisBones = ""

        for idx in range(2, self.nFrames):
            count = 0
            value = values[idx]
            if xUp:
                if xWaterMark < value.x:
                    xWaterMark = value.x
                else:
                    retracement = xWaterMark - value.x
                    amountMove  = xWaterMark - firstValue.x
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       count += 1
                       xUp = False
            else:
                if xWaterMark > value.x:
                    xWaterMark = value.x
                else:
                    retracement = value.x - xWaterMark
                    amountMove  = firstValue.x - xWaterMark
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       count += 1
                       xUp = True


            if yUp:
                if yWaterMark < value.y:
                    yWaterMark = value.y
                else:
                    retracement = yWaterMark - value.y
                    amountMove  = yWaterMark - firstValue.y
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       count += 1
                       yUp = False
            else:
                if yWaterMark > value.y:
                    yWaterMark = value.y
                else:
                    retracement = value.y - yWaterMark
                    amountMove  = firstValue.y - yWaterMark
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       count += 1
                       yUp = True


            if zUp:
                if zWaterMark < value.z:
                    zWaterMark = value.z
                else:
                    retracement = zWaterMark - value.z
                    amountMove  = zWaterMark - firstValue.z
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       count += 1
                       zUp = False
            else:
                if zWaterMark > value.z:
                    zWaterMark = value.z
                else:
                    retracement = value.z - zWaterMark
                    amountMove  = firstValue.z - zWaterMark
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       count += 1
                       zUp = True

            if count > 1:
                self.nSwitches[idx] += 1
                thisBones += " " + str(self.frames[idx])

        return thisBones