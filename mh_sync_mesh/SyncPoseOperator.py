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
    bl_idname = "armature.sync_pose"
    bl_label = "Synchronize MH Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self):
        super().__init__('getPose')

    def callback(self,json_obj):

        print("Update pose")
        
        skeleton = bpy.context.active_object
        bones = skeleton.pose.bones
        bpy.ops.object.mode_set(mode='POSE')       
        haveDots = self.bonesHaveDots(bones)

        for bone in bones:
            # the dots in collada exported bone names are replaced with '_', check for data with that changed back
            name = bone.name.replace("_", ".") if not haveDots else bone.name
            
            if name in json_obj:
                mat = Matrix(json_obj[name])
                nmat = Matrix((mat[0], -mat[2], mat[1])).to_3x3().to_4x4()
                nmat.col[3] = bone.matrix.col[3]
                bone.matrix = nmat

            else:
                print(name + ' bone not found coming from MH')
            
    def bonesHaveDots(self, bones):
        for bone in bones:
            if "." in bone.name:
                return True
            
        return False
    
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'ARMATURE'