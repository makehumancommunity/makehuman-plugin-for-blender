#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class ActionTrimLeftOperator(bpy.types.Operator):
    """Remove all keyframes, of the current action, before the current frame, shifting remaining to the left.\n\nCan be done with any armature based action against any rig."""
    bl_idname = 'mh_community.trim_left'
    bl_label = 'Left'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..animation_trimming import AnimationTrimming

        armature = context.object
        trimmer = AnimationTrimming(armature)
        trimmer.deleteAndShift()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        return ob.animation_data is not None