from mathutils import Quaternion, Vector, Euler
import bpy
#===============================================================================
class AnimationTrimming():

    def __init__(self, armature):
        self.armature = armature
        self.action = armature.animation_data.action
        self.first = int(self.action.frame_range[0])
        self.last  = int(self.action.frame_range[1])
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                         operation entry points
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def deleteAndShift(self):
        # drop from the front up to, but not including, the current frame
        firstGoodFrame = bpy.context.scene.frame_current
        self.dropRange(self.first, firstGoodFrame)

        # shift remaining keys on a bone, property basis, to the left
        for bone in self.armature.pose.bones:
            rotProperty = 'rotation_quaternion' if bone.rotation_mode == 'QUATERNION' else 'rotation_euler'
            self.shiftLeft(bone, rotProperty, firstGoodFrame)
            if self.hasLocationKeys(bone):
                self.shiftLeft(bone, 'location', firstGoodFrame)

        # dope sheet not reflecting deletions immediately, so do "something"
        bpy.context.scene.frame_set(self.first)

    def dropToRight(self):
        # drop all frames for the bones after the current frame
        lastGoodFrame = bpy.context.scene.frame_current
        self.dropRange(lastGoodFrame + 1, self.last + 1)

        # dope sheet not reflecting deletions immediately, so do "something"
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                       below only called internally
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dropRange(self, first, lastNotIncluded):
        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.armature.pose.bones:
            for frameNum in range(first, lastNotIncluded):
                # does not error when location property missing, so just do all possiblities
                rotProperty = 'rotation_quaternion' if bone.rotation_mode == 'QUATERNION' else 'rotation_euler'
                bone.keyframe_delete(rotProperty, -1, frameNum)
                bone.keyframe_delete('location' , -1, frameNum)

    def shiftLeft(self, bone, property, firstGoodFrame):
        bpy.ops.object.mode_set(mode='POSE')
        newFrameNum = self.first

        # for each kept frame shift it, then delete the old one
        for oldFrameNum in range(firstGoodFrame, self.last + 1):
            # find the value of property of the bone at a given frame & set the bone to it
            values = self.findKeyValues(bone, property, oldFrameNum)
            if len(values) == 0: continue

            if property == 'rotation_quaternion':
                bone.rotation_quaternion = Quaternion(values)
            elif property == 'rotation_euler':
                bone.rotation_euler = Euler(values)
            elif property == 'location':
                bone.location = Vector(values)

            # add a new keyframe
            bone.keyframe_insert(property, frame = newFrameNum, group = bone.name)
            newFrameNum += 1

            # delete the old key frame
            bone.keyframe_delete(property, -1, oldFrameNum)

    # a given key only contains a single float, so return all found for a given property / frame number
    def findKeyValues(self, bone, property, frameNum):
        ret = []
        dataPath = 'pose.bones["' + bone.name + '"].' + property
        for c in self.action.fcurves:
            if c.data_path == dataPath:
                ret.append(c.evaluate(frameNum))

        return ret

    def hasLocationKeys(self, bone):
        dataPath = 'pose.bones["' + bone.name + '"].location'

        for c in self.action.fcurves:
            if c.data_path == dataPath:
                return True

        return False
