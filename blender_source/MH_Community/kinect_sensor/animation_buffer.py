from .to_kinect2 import *
from .calibrate_armature import *
from .capture_armature import *
from .empties import *

from mathutils import Matrix, Vector

import bpy
#===============================================================================
class AnimationBuffer:
    tracked_only = False

    def __init__(self, name):
        self.name = name
        self.frames = []
        self.bones = []
        self.hands = []
        self.clipPlanes = []

        self.frame = -1 # nuke for production

    def loadSensorFrame(self, frame, bones, hands, clipPlane):
        self.frames.append(frame)
        self.bones.append(bones)
        self.hands.append(hands)
        self.clipPlanes.append(clipPlane)
        
        # if this is the first frame (not neccessarily 0) for all bodies, set root location basis
        if len(self.bones) == 1:
            raw = bones[ROOT_BONE]['location']
            self.RootLocBasis = Vector((raw['x'], raw['y'], raw['z']))
            print('root basis:  x:' + ('%.4f' % self.RootLocBasis.x) + ', y:' + ('%.4f' % self.RootLocBasis.y) + ', z:' + ('%.4f' % self.RootLocBasis.z) + '\n')
        
    def isFinger(self, boneName):
        return boneName.find('Hand') >= 0 or boneName.find('HandTip') >= 0 or boneName.find('Thumb') >= 0

    def assign(self, armature, baseActionName, excludeFingers):
        # only does something on the first call for an armature
        CalibrateArmature(armature, self.bones[0])

        # temp code to only do the first frame
        if not armature.animation_data:
            armature.animation_data_create()
            armature.animation_data.action = bpy.data.actions.new(armature.name + '-' + baseActionName)
            
        # determine the root bone height, by looking at the head.z of spine mid
        # use it to get scaling factor for root location data
        bpy.ops.object.mode_set(mode='EDIT')
        skelRootHeight = armature.data.edit_bones[SPINE_MID].head.z
        self.rootScaling = self.RootLocBasis.y / skelRootHeight
        print('RootLocBasis.y' + str(self.RootLocBasis.y) + ', skelRootHeight ' + str(skelRootHeight) + ', rootScaling ' + str(self.rootScaling))
        bpy.ops.object.mode_set(mode='POSE')

        self.assignLoc(armature, excludeFingers)
            
        bpy.context.scene.frame_set(0) # puts at first frame, not last
 
    def relativeRootLoc(self, frameNum):
        raw = self.bones[frameNum][ROOT_BONE]['location']
        loc = self.RootLocBasis - Vector((raw['x'], raw['y'], raw['z']))
        # scale in a way which works in both pre- post- 2.8
        loc.x = loc.x / self.rootScaling
        loc.y = loc.y / self.rootScaling
        loc.z = loc.z / self.rootScaling
     #   print('rel root loc frame: ' + str(frameNum) + ', x:' + ('%.4f' % loc.x) + ', y:' + ('%.4f' % loc.y) + ', z:' + ('%.4f' % loc.z) + '\n')
        return loc        
    #===========================================================================
    def reset(self):
        if self.empties is not None:
            self.empties.nukeConstraints()
            self.empties.nuke()
            self.empties = None
            
        if self.capture is not None:
            self.capture.cleanUp()
            self.capture = None
            
        self.frame = -1
    #===========================================================================
    def assignLoc(self, armature, excludeFingers):
        self.reset()
        
        self.capture = CaptureArmature(armature)
        self.empties = Empties(self.capture.captureSkel)
        bpy.ops.object.mode_set(mode='POSE')

        for i in range(len(self.frames)):
            # assign the empties to position capture skel, copy rotations to orig, then assign animation frame
            self.empties.assign(self.bones[i])
            self.assignFrame(armature, self.frames[i], excludeFingers)

        self.reset()
        bpy.ops.pose.transforms_clear()

    def assignFrame(self, armature, frameNum, excludeFingers):
        # this is REQUIRED to get something to actually get recorded other than just before assignment
        bpy.context.scene.update()
        
        for name in KINECT_BONES:
            if excludeFingers and self.isFinger(name): continue
            if name not in armature.data.bones: continue

            bone = armature.pose.bones[name]

            objectSpace = bone.matrix
            localSpace = Matrix(armature.convert_space(bone, objectSpace, 'POSE', 'LOCAL'))
            loc, rot, scale = localSpace.decompose()

            if name == ROOT_BONE:
                bone.location = self.relativeRootLoc(frameNum)
                bone.keyframe_insert('location', frame = frameNum, group = name)

            bone.rotation_quaternion = rot
            bone.keyframe_insert('rotation_quaternion', frame = frameNum, group = name)

    def oneRight(self, armature, scale):
        self.capture = CaptureArmature(armature)
        beginning = self.frame == -1
        if beginning:
            self.empties = Empties(self.capture.captureSkel, scale) # 39.3701 for inches

        self.frame = self.frame + 1 if self.frame + 1 < len(self.bones) else 0
        self.empties.assign(self.bones[self.frame])