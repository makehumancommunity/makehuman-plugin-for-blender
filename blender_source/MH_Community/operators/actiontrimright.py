#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class ActionTrimRightOperator(bpy.types.Operator):
    """Remove all keyframes, of the current action, after the current frame.\n\nCan be done with any armature based action against any rig."""
    bl_idname = 'mh_community.trim_right'
    bl_label = 'Right'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..animation_trimming import AnimationTrimming

        armature = context.object
        trimmer = AnimationTrimming(armature)
        trimmer.dropToRight()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        return ob.animation_data is not None