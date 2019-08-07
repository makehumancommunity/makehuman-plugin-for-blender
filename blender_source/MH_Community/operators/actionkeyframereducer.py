#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_ActionKeyframeReducerOperator(bpy.types.Operator):
    """Both smooth and reduce the number of frames by detecting key frames.\n\nDo not do multiple times.  Undo, change args, & do again."""
    bl_idname = 'mh_community.keyframe_animation'
    bl_label = 'Smooth'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mocap.keyframe_reduction import KeyFrameReduction

        armature = context.object
        rigInfo = RigInfo.determineRig(armature)
        KeyFrameReduction(rigInfo, context.scene.MhReversalMinRetracement)

        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None: return False

        return ob.animation_data is not None