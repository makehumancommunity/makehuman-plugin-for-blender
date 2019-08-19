from mathutils import Quaternion, Vector, Euler
import bpy
#===============================================================================
class AnimationTrimming():

    def __init__(self, armature):
        self.armature = armature
        self.action = armature.animation_data.action
        self.first = int(self.action.frame_range[0])
        self.last  = int(self.action.frame_range[1])
        
        # get the actual frames with data
        self.frames = dict() # use dictionary, so frames common amoung bones only listed once
        for fcurve in self.action.fcurves:
            for key in fcurve.keyframe_points:
                frame = key.co.x
                self.frames[frame] = True # actual value has no meaning

        self.frames = sorted(self.frames)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                         operation entry points
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def deleteAndShift(self):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='POSE')

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
        bpy.ops.object.mode_set(mode=current_mode)

    def dropToRight(self):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='POSE')

        # drop all frames for the bones after the current frame
        lastGoodFrame = bpy.context.scene.frame_current
        self.dropRange(lastGoodFrame + 1, self.last + 1)

        # dope sheet not reflecting deletions immediately, so do "something"
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        bpy.ops.object.mode_set(mode=current_mode)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                       below only called internally
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def dropRange(self, first, lastNotIncluded):
        for bone in self.armature.pose.bones:
            for frameNum in range(first, lastNotIncluded):
                # does not error when location property missing, so just do all possiblities
                rotProperty = 'rotation_quaternion' if bone.rotation_mode == 'QUATERNION' else 'rotation_euler'
                bone.keyframe_delete(rotProperty, -1, frameNum)
                bone.keyframe_delete('location' , -1, frameNum)

    def shiftLeft(self, bone, property, firstGoodFrame):
        newFrameNum = firstGoodFrame

        # for each kept frame shift it, then delete the old one
        for oldFrameNum in self.frames:
            if oldFrameNum < firstGoodFrame: continue

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
            bone.keyframe_insert(property, frame = oldFrameNum - newFrameNum, group = bone.name)

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
