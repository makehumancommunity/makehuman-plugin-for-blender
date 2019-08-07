#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_ToSensorRigOperator(bpy.types.Operator):
    """Transform a default Rig, with or without toes, to one suited for use with the selected device.\n\nCannot be done after fingers have been amputated,\nor a finger IK has been added."""
    bl_idname = 'mh_community.to_sensor_rig'
    bl_label = 'Custom Rig Conversion'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..kinect_sensor.to_kinect2 import ToKinectV2
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None or rigInfo.name != 'Default Rig':
            self.report({'ERROR'}, 'Rig is not the default Rig')
            return {'FINISHED'}

        sensorType = context.scene.MhSensorType
        if sensorType == 'KINECT2':
            from ..rig.kinect2riginfo import Kinect2RigInfo
            Kinect2RigInfo.convertFromDefault(rigInfo)

        elif device == 'KINECT_AZURE':
            pass

        self.report({'INFO'}, 'Converted to a sensor specific rig')
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or rigInfo.name != 'Default Rig' or not rigInfo.fingerIKCapable(): return False

        # just need to check IK rig not already added
        return not rigInfo.hasIKRigs()
