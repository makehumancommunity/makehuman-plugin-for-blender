from collections import deque

import bpy
#===============================================================================
class JitterReduction():

    def __init__(self, armature, maxFrames, minRetracementPct):
        self.armature = armature
        self.action = armature.animation_data.action

        self.valuesQueue = deque(maxlen = maxFrames)
        self.idxQueue    = deque(maxlen = maxFrames)
        self.minRetracementRatio = minRetracementPct / 100

        self.frames = dict()
        for fcurve in self.action.fcurves:
            for key in fcurve.keyframe_points:
                frame = key.co.x
                self.frames[frame] = True # actual value has no meaning

        self.frames = sorted(self.frames)
        self.nFrames = len(self.frames)
        self.lastFrameNum = self.frames[self.nFrames - 1]

        self.scene = bpy.context.scene

        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.armature.pose.bones:
            self.smoothbone(bone)

    def smoothbone(self, bone):
        property = 'rotation_quaternion' if bone.rotation_mode == 'QUATERNION' else 'rotation_euler'
#        dataPath = 'pose.bones["' + bone.name + '"].' + ('rotation_quaternion' if bone.rotation_mode == 'QUATERNION' else 'rotation_euler')

        self.valuesQueue.clear()
        self.idxQueue   .clear()

        # iterate through the frames; easiest to get comparison data, since just use bone as source
        for idx in range(len(self.frames)):
            self.scene.frame_set(self.frames[idx])

            # when queue at maximum value from opposite side is removed automatically
            self.valuesQueue.append(bone.rotation_quaternion.to_euler("XYZ") if bone.rotation_mode == 'QUATERNION' else bone.rotation_euler)
            self.idxQueue   .append(idx)

            # revIdx is the index in queues where the data should start to be kept again
            revIdx = self.hasReversed()
            if revIdx != -1:
                # The first frame in the queues is the last one before jitter, so pass over / keep
                self.valuesQueue.popleft()
                self.idxQueue   .popleft()

                # range() takes an argument of up to, so passing if revIdx was a 2 would, delete one frame
                for nukeIdx in range(1, revIdx):
                    self.valuesQueue.popleft()
                    bone.keyframe_delete(property, -1, self.frames[self.idxQueue.popleft()])

    def hasReversed(self):
        queueLen = len(self.valuesQueue)
        if queueLen < 3:
            return -1

        firstValue  = self.valuesQueue[0]
        secondValue = self.valuesQueue[1]

        xDir = secondValue.x - firstValue.x > 0
        xWaterMark = secondValue.x
        yDir = secondValue.y - firstValue.y > 0
        yWaterMark = secondValue.y
        zDir = secondValue.z - firstValue.z > 0
        zWaterMark = secondValue.z

        for idx in range(2, queueLen):
            value = self.valuesQueue[idx]
            if xDir:
                if xWaterMark < value.x:
                    xWaterMark = value.x
                else:
                    retracement = xWaterMark - value.x
                    amountMove  = xWaterMark - firstValue.x
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       return idx
            else:
                if xWaterMark > value.x:
                    xWaterMark = value.x
                else:
                    retracement = value.x - xWaterMark
                    amountMove  = firstValue.x - xWaterMark
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       return idx


            if yDir:
                if yWaterMark < value.y:
                    yWaterMark = value.y
                else:
                    retracement = yWaterMark - value.y
                    amountMove  = yWaterMark - firstValue.y
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       return idx
            else:
                if yWaterMark > value.y:
                    yWaterMark = value.y
                else:
                    retracement = value.y - yWaterMark
                    amountMove  = firstValue.y - yWaterMark
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       return idx


            if zDir:
                if zWaterMark < value.z:
                    zWaterMark = value.z
                else:
                    retracement = zWaterMark - value.z
                    amountMove  = zWaterMark - firstValue.z
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       return idx
            else:
                if zWaterMark > value.z:
                    zWaterMark = value.z
                else:
                    retracement = value.z - zWaterMark
                    amountMove  = firstValue.z - zWaterMark
                    if amountMove > 0 and self.minRetracementRatio < retracement / amountMove:
                       return idx

        # signal no reversal
        return -1