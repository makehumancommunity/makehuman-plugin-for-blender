#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_ActionJitterReducerOperator(bpy.types.Operator):
    """Smooth armature movements which get quickly reversed through data reduction.\n\nCan be done with any armature based action against any rig.\n\nDo not do multiple times.  Undo, change args, & do again."""
    bl_idname = 'mh_community.smooth_animation'
    bl_label = 'Smooth'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..kinect_sensor.jitter_reduction import JitterReduction

        armature = context.object
        JitterReduction(armature, context.scene.MhJitterMaxFrames, context.scene.MhJitterMinRetracement)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        return ob.animation_data is not None