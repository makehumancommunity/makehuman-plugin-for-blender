from .rig_info import *

import bpy
#===============================================================================
CUSTOM_SHAPE = 'GZM_Knuckle' # name of mesh to use as custom shape if found
#===============================================================================
class FingerRig():
    def __init__(self, rigInfo):
        self.rigInfo = rigInfo
        self.armature = self.rigInfo.armature
        self.scene = bpy.context.scene
#===============================================================================
    def add(self):
        self.buildThumb(True)
        self.buildThumb(False)
        self.buildFingerPair(2)
        self.buildFingerPair(3)
        self.buildFingerPair(4)
        self.buildFingerPair(5)

        # tell BabylonJS exporter not to export IK bones
        if hasattr(self.scene, "ignoreIKBones"):
            self.scene.ignoreIKBones = True
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def buildThumb(self, isLeft):
        side = 'L' if isLeft else 'R'

        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        parent = eBones[self.rigInfo.thumbParent(isLeft)]
        thumbBoneNames = self.rigInfo.thumbBones(isLeft)

        self.build(eBones, 'thumb.ik.' + side, parent, thumbBoneNames, False)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def buildFingerPair(self, which):
        self.buildFinger(which, True)
        self.buildFinger(which, False)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def buildFinger(self, which, isLeft):
        side = 'L' if isLeft else 'R'

        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        if which == 2:
            name = 'index.ik.'
            parent = eBones[self.rigInfo.indexFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.indexFingerBones(isLeft)

        elif which == 3:
            name = 'middle.ik.'
            parent = eBones[self.rigInfo.middleFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.middleFingerBones(isLeft)

        elif which == 4:
            name = 'ring.ik.'
            parent = eBones[self.rigInfo.ringFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.ringFingerBones(isLeft)

        elif which == 5:
            name = 'pinky.ik.'
            parent = eBones[self.rigInfo.pinkyFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.pinkyFingerBones(isLeft)

        self.build(eBones, name + side, parent, fingerBoneNames, True)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def build(self, eBones, controlBoneName, parent, fingerBoneNames, hide):
        lastIdx = len(fingerBoneNames) - 1
        firstFinger = eBones[fingerBoneNames[0      ]]
        lastFinger  = eBones[fingerBoneNames[lastIdx]]

        controlBone = eBones.new(controlBoneName)
        controlBone.head = firstFinger.head.copy()
        controlBone.tail = lastFinger .tail.copy()
        controlBone.parent = parent

        # make changes that must be done in pose mode
        bpy.ops.object.mode_set(mode='POSE')
        controlPBone = self.armature.pose.bones[controlBoneName]
        controlPBone.lock_location[0] = True
        controlPBone.lock_location[1] = True
        controlPBone.lock_location[2] = True

        # apply custom_shape to the pose bone version
        if CUSTOM_SHAPE in self.scene.objects:
            controlPBone.custom_shape = self.scene.objects [CUSTOM_SHAPE]

        for bIndex, boneName in enumerate(fingerBoneNames):
            self.addCopyRotation(boneName, controlBoneName, bIndex == 0)
            if hide:
                self.armature.data.bones[boneName].hide = True

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCopyRotation(self, boneName, subtargetName, use_z):
        # apply constraints to the pose bone version
        bpy.ops.object.mode_set(mode='POSE')
        pBones = self.armature.pose.bones

        pBone = pBones[boneName]
        con = pBone.constraints.new('COPY_ROTATION')
        con.target = self.armature
        con.subtarget = subtargetName
        con.use_y = False
        con.use_z = use_z
        con.use_offset = True
        con.target_space = 'LOCAL'
        con.owner_space  = 'LOCAL'
#===============================================================================
    def remove(self):
        self.removeSide(True)
        self.removeSide(False)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def removeSide(self, isLeft):
        side = 'L' if isLeft else 'R'
        self.demolish('thumb.ik.'  + side, self.rigInfo.thumbBones       (isLeft))
        self.demolish('index.ik.'  + side, self.rigInfo.indexFingerBones (isLeft))
        self.demolish('middle.ik.' + side, self.rigInfo.middleFingerBones(isLeft))
        self.demolish('ring.ik.'   + side, self.rigInfo.ringFingerBones  (isLeft))
        self.demolish('pinky.ik.'  + side, self.rigInfo.pinkyFingerBones (isLeft))
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # no need of BoneSurgery module, since no weights to give back
    def demolish(self, controlBoneName, fingerBoneNames):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        self.armature.data.edit_bones[controlBoneName].select = True
        bpy.ops.armature.delete()

        bpy.ops.object.mode_set(mode='POSE')
        for bIndex, boneName in enumerate(fingerBoneNames):
            self.armature.data.bones[boneName].select = True
            self.armature.data.bones[boneName].hide = False

        for bone in bpy.context.selected_pose_bones:
            # Create a list of all the copy location constraints on this bone
            copyRotConstraints = [ c for c in bone.constraints if c.type == 'COPY_ROTATION' ]

            # Iterate over all the bone's copy location constraints and delete them all
            for c in copyRotConstraints:
                bone.constraints.remove( c ) # Remove constraint