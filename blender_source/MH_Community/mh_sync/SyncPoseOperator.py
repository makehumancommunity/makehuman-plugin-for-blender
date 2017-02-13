#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "Synchronize MakeHuman armature pose",
    "category": "Armature",
}

from .SyncOperator import *

import bpy
from mathutils import Quaternion, Matrix
import pprint

pp = pprint.PrettyPrinter(indent=4)

class SyncPoseOperator(SyncOperator):
    """Synchronize the pose of the skeleton of a human with MH"""
    bl_idname = "mh_community.sync_pose"
    bl_label = "Synchronize MH Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        super().__init__('getPose')

    def callback(self,json_obj):

        print("Update pose")
        
        self.skeleton = bpy.context.active_object
        self.bones = self.skeleton.pose.bones
        bpy.ops.object.mode_set(mode='POSE')       
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        self.haveDots = self.bonesHaveDots()
            
        #apply as passed back
        for bone in self.bones:
            self.apply(bone, json_obj)
            
        #feet on Ground processing
        if bpy.context.scene.MhFeetOnGround:
            bpy.ops.pose.select_all(action='DESELECT')
            self.skeleton.data.bones["root"].select = True
            bpy.ops.pose.loc_clear()

        self.report({"INFO"},"Done")

    def apply(self, bone, json_obj):
        # the dots in collada exported bone names are replaced with '_', check for data with that changed back
        name = bone.name.replace("_", ".") if not self.haveDots else bone.name
        
        if name in json_obj.data:
            bone.matrix = Matrix(json_obj.data[name])
                
            # this operation every bone causes all matrices to be applied in one run
            bpy.ops.pose.select_all(action='SELECT')
            
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
    
    def getRestTranslation(self, bone):
        # need to change to edit mode to work with editbones
        bpy.ops.object.mode_set(mode='EDIT')
        for editBone in self.skeleton.data.edit_bones:
            if editBone.name == bone.name:
                ret = editBone.matrix.to_translation()
                bpy.ops.object.mode_set(mode='POSE')
                return ret

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'ARMATURE'