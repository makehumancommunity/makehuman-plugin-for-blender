#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_ActionKeyframeReducerOperator(bpy.types.Operator):
    """Both smooth and reduce the number of frames by detecting key frames.\n\nDo not do multiple times.  Undo, change args, & do again."""
    bl_idname = 'mh_community.keyframe_animation'
    bl_label = 'Reduce'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mocap.keyframe_reduction import KeyFrameReduction

        armature = context.object
        problemMsg = None
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            problemMsg = 'Unknown rigs are not supported.'
        elif not rigInfo.isMocapCapable():
            problemMsg = 'Rig is not capable of motion capture.'
        elif rigInfo.hasIKRigs():
            problemMsg = 'Cannot be done while rig has an IK snap-on.'
        elif armature.animation_data is None:
            problemMsg = 'No current action on rig to keyframe'

        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)
        else:
            KeyFrameReduction(rigInfo, context.scene.MhReversalMinRetracement)

        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob is not None and ob.type == 'ARMATURE'