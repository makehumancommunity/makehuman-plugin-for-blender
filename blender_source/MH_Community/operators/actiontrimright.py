#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_ActionTrimRightOperator(bpy.types.Operator):
    """Remove all keyframes, of the current action, after the current frame.\n\nCan be done with any armature based action against any rig."""
    bl_idname = 'mh_community.trim_right'
    bl_label = 'Right'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..animation_trimming import AnimationTrimming

        armature = context.object
        problemMsg = None
        if armature.animation_data is None:
            problemMsg = 'No current action on rig to trim'

        if problemMsg is not None:
            self.report({'ERROR'}, problemMsg)
        else:
            trimmer = AnimationTrimming(armature)
            trimmer.dropToRight()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob is not None and ob.type == 'ARMATURE'