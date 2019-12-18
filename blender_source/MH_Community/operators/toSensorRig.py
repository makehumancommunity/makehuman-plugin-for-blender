#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_ToSensorRigOperator(bpy.types.Operator):
    """Transform a default Rig, with or without toes, to one suited for use with the selected device."""
    bl_idname = 'mh_community.to_sensor_rig'
    bl_label = 'Custom Rig Conversion'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..kinect_sensor.to_kinect2 import ToKinectV2
        armature = context.object
        problemMsg = None
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            problemMsg = 'Unknown rigs are not supported.'
        elif rigInfo.name != 'Default Rig':
            problemMsg = 'Only the default rig can be converted.'
        elif rigInfo.hasIKRigs():
            problemMsg = 'Cannot be done while rig has an IK snap-on.'
        elif not rigInfo.fingerIKCapable():
            problemMsg = 'Cannot be done after fingers have been amputated'

        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)
        else:
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
        return ob is not None and ob.type == 'ARMATURE'