#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class ToKinect2Operator(bpy.types.Operator):
    """Transform a default Rig, with or without toes, to one suited for use with an XBox One Kinect-2 device.\n\nCannot be done after fingers have been amputated,\nor a finger IK has been added."""
    bl_idname = 'mh_community.to_kinect2'
    bl_label = 'Convert Rig'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..rig_info import RigInfo
        from ..kinect_sensor.to_kinect2 import ToKinectV2
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None or rigInfo.name != 'Default Rig':
            self.report({'ERROR'}, 'Rig is not the default Rig')
            return {'FINISHED'}

        #if not rigInfo.hasRestTpose():
        #    self.report({'ERROR'}, 'Must be exported in T-Pose to use sensor')
        #    return {'FINISHED'}

        ToKinectV2(rigInfo).convert()

        self.report({'INFO'}, 'Converted to a Kinect2 rig')
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from ..rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or rigInfo.name != 'Default Rig' or not rigInfo.fingerIKCapable(): return False

        # just need to check IK rig not already added
        return not rigInfo.hasIKRigs()
