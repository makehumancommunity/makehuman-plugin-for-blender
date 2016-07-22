from .rig_info import *

import bpy
from mathutils import Vector
#===============================================================================
CUSTOM_SHAPE = 'GZM_Knuckle' # name of mesh to use as custom shape if found
#===============================================================================
class SnapOnFingerRig(bpy.types.Operator):
    """Snap on finger control bones"""
    bl_idname = 'mh_community.finger_rig'
    bl_label = 'Erect Finger Rig'

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.scene = context.scene
        self.armature = context.object

        self.rigInfo = RigInfo.determineRig(self.armature)
        if self.rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        print("adding finger rig to " + self.rigInfo.name)

        self.buildThumb(True)
        self.buildThumb(False)
        self.buildFingerPair(2)
        self.buildFingerPair(3)
        self.buildFingerPair(4)
        self.buildFingerPair(5)

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'ARMATURE' and RigInfo.determineRig(ob) is not None
#===============================================================================
    def buildThumb(self, isLeft):
        side = 'L' if isLeft else 'R'

        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        parent = eBones[self.rigInfo.ringFingerParent(isLeft)]
        thumbBoneNames = self.rigInfo.thumbBones(isLeft)

        self.build(eBones, 'thumb.' + side, parent, thumbBoneNames, False)
#===============================================================================
    def buildFingerPair(self, which):
        self.buildFinger(which, True)
        self.buildFinger(which, False)

    def buildFinger(self, which, isLeft):
        side = 'L' if isLeft else 'R'

        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        if which == 2:
            name = 'index.'
            parent = eBones[self.rigInfo.indexFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.indexFingerBones(isLeft)

        elif which == 3:
            name = 'middle.'
            parent = eBones[self.rigInfo.middleFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.middleFingerBones(isLeft)

        elif which == 4:
            name = 'ring.'
            parent = eBones[self.rigInfo.ringFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.ringFingerBones(isLeft)

        elif which == 5:
            name = 'pinky.'
            parent = eBones[self.rigInfo.pinkyFingerParent(isLeft)]
            fingerBoneNames = self.rigInfo.pinkyFingerBones(isLeft)

        self.build(eBones, name + side, parent, fingerBoneNames, True)

#===============================================================================
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

#===============================================================================
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