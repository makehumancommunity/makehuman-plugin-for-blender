#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Synchronize MakeHuman armature pose",
    "category": "Armature",
}

from .sync_ops import SyncOperator
from ..rig import RigInfo

import bpy
from mathutils import Matrix
import time

FIRST_BONE_NOT_FOR_EXPRESSIONS = 'head'
HEAD_PARENTS = 'head-neck03-neck02-neck01-spine01-spine02-spine03-spine04-spine05-root'

class SyncPose(SyncOperator):
    def __init__(self):
        super().__init__('getPose')
        
        self.skeleton = bpy.context.active_object
        self.rigInfo = RigInfo.determineRig(self.skeleton)
        self.unitMultplier = self.rigInfo.unitMultplierToExported() / 10  # makehuman is internally in decimeters

        self.bones = self.skeleton.pose.bones
        self.haveDots = self.bonesHaveDots()
        self.rootBone = self.getRootBone()
        
        # when allowing translation it is a must that previous rest pose be saved & applied, but always doing
        self.restPoses = {}
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        for bone in self.bones:
            self.restPoses[bone.name] = bone.matrix
        
#        self.bonesInOrder = self.getChildBones(self.rootBone)
        
    def process(self, poseFilename = None, isExpression = False):
        if poseFilename is not None:
            self.call.setParam("poseFilename", poseFilename)

        self.isExpression = isExpression # used in callback
        self.executeJsonCall()

    def callback(self,json_obj):
        self.startCallBack = time.time()

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()

        #apply as passed back
        for bone in self.bones:
            # Could have been exported with a Pose not currently matching MH session.
            # For expressions, only set bones with an ancestor of head to avoid extra stuff in pose library.
            # Still might work if both are facing forward.
            if not self.isExpression or self.hasAncestor(bone, FIRST_BONE_NOT_FOR_EXPRESSIONS) or bone.name in HEAD_PARENTS:
                self.apply(bone, json_obj, bpy.context.scene.MhNoLocation)
            
        if self.isExpression:
            self.selectRootToHead();
            bpy.ops.pose.transforms_clear()
            self.selectFaceBones()

        self.callBackComplete = time.time()

    def apply(self, bone, json_obj, MhNoLocation):
        # the dots in collada exported bone names are replaced with '_', check for data with that changed back
        name = bone.name.replace("_", ".") if not self.haveDots else bone.name

        if name in json_obj.data:
            matrix = Matrix(json_obj.data[name])
            matrix.translation.x *= self.unitMultplier
            matrix.translation.y *= self.unitMultplier
            matrix.translation.z *= self.unitMultplier

# An alternative to just assigning the matrix, which almost works, just here show what was tried
#            local = self.skeleton.convert_space(pose_bone = bone, matrix = matrix, from_space = 'WORLD', to_space = 'LOCAL_WITH_PARENT')
#            loc, rot, scale = local.decompose()
            
#            bone.location = loc
#            bone.rotation_quaternion = rot
#            bone.scale = scale
            bone.matrix = matrix
            
            if MhNoLocation:
                bone.location[0] = 0
                bone.location[1] = 0
                bone.location[2] = 0
                
            if bpy.app.version < (2, 80, 0):
                bpy.context.scene.update()
            else:
                bpy.context.view_layer.update()

        else:
            print(name + ' bone not found coming from MH')

    def bonesHaveDots(self):
        for bone in self.bones:
            if "." in bone.name:
                return True

        return False

    def getRootBone(self):
        for bone in self.bones:
            if bone.parent is None:
                return bone

        # cannot really happen, but
        return None
    
    def restoreOriginal(self):
        for bone in self.bones:
            bone.matrix = self.restPoses[bone.name]
            
        if bpy.app.version < (2, 80, 0):
            bpy.context.scene.update()
        else:
            bpy.context.view_layer.update()
        
    def getChildBones(self, pBone):
        ret = []
        # recursively call against all direct children
        for bone in self.bones:
            if bone.parent is not None and bone.parent.name == pBone.name:
                kids = self.getChildBones(bone)
                for kid in kids:
                    ret.append(kid)
        ret.append(pBone)
        return ret       

    def selectRootToHead(self, clearFirst = True):
        if clearFirst:
            bpy.ops.pose.select_all(action='DESELECT')
        
        # cannot use pose bones for selections
        for bone in self.skeleton.data.bones:
            if not self.hasAncestor(bone, FIRST_BONE_NOT_FOR_EXPRESSIONS):
                bone.select = True        

    def selectFaceBones(self, clearFirst = True):
        if clearFirst:
            bpy.ops.pose.select_all(action='DESELECT')
        
        # cannot use pose bones for selections
        for bone in self.skeleton.data.bones:
            if self.hasAncestor(bone, FIRST_BONE_NOT_FOR_EXPRESSIONS):
                bone.select = True        

    def hasAncestor(self, poseBone, ancestorName):
        while poseBone.parent is not None:
            if poseBone.parent.name == ancestorName:
                return True
            else:
                poseBone = poseBone.parent

        return False

    def getRestTranslation(self, bone):
        # need to change to edit mode to work with editbones
        bpy.ops.object.mode_set(mode='EDIT')
        for editBone in self.skeleton.data.edit_bones:
            if editBone.name == bone.name:
                ret = editBone.matrix.to_translation()
                bpy.ops.object.mode_set(mode='POSE')
                return ret
            
    def selectRootToHeadHold(self):
        bpy.ops.pose.select_all(action='DESELECT')
        headBone = self.skeleton.data.bones[FIRST_BONE_NOT_FOR_EXPRESSIONS]
        headBone.select = True

        bpy.ops.pose.select_hierarchy(direction='PARENT')

    def selectFaceBonesHold(self):
        bpy.ops.pose.select_all(action='DESELECT')
        headBone = self.skeleton.data.bones[FIRST_BONE_NOT_FOR_EXPRESSIONS]
        headBone.select = True

        bpy.ops.pose.select_hierarchy(direction='CHILD')

        headBone.select = False

