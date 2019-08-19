#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_MocapAssignmentOperator(bpy.types.Operator):
    """Assign an animation to an action of the selected skeleton."""
    bl_idname = 'mh_community.assign_mocap'
    bl_label = 'Assign'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mocap.sensor_runtime import Sensor

        armature = context.object
        problemMsg = None
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            problemMsg = 'Unknown rigs are not supported.'
        elif not rigInfo.isMocapCapable():
            problemMsg = 'Rig is not capable of motion capture.'
        elif rigInfo.hasIKRigs():
            problemMsg = 'Cannot be done while rig has an IK snap-on.'
        elif len(context.scene.MhSensorAnimations) == 0:
            problemMsg = 'No current capture being buffered.'
        elif rigInfo.name == 'Default Rig' and not rigInfo.hasRestTpose():
            problemMsg = 'The default rig can only be assigned when it has a rest T-Pose.'

        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)
        else:
            baseActionName = context.scene.MhSensorBaseActionName
            Sensor.assign(rigInfo, context.scene.MhSensorAnimation_index, baseActionName)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob is not None and ob.type == 'ARMATURE'