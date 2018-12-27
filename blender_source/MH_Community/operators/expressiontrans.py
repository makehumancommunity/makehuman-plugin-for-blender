#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..rig import RigInfo

class MHC_OT_ExpressionTransOperator(bpy.types.Operator):
    """Transfer MakeHuman expressions to a pose library.  Requirements:\n\nMust be the Default armature.\nMust be exported in decimeters to allow location translation.\nMust have a current Pose library."""
    bl_idname = "mh_community.expressions_trans"
    bl_label = "Transfer"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mh_sync.expression_transfer import ExpressionTransfer
 
        armature = context.object
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo.determineExportedUnits() != 'DECIMETERS' and not bpy.context.scene.MhNoLocation:
            self.report({'ERROR'}, 'Location translation only possible when exported in decimeters to match MakeHuman.')
            return {'FINISHED'}

        toShapeKeys = context.scene.mhExprDestination == 'SHAPEKEYS'
        exprFilter = context.scene.MhExprFilterTag.lower()
        ExpressionTransfer(self, armature, toShapeKeys, exprFilter)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False
        if context.scene.mhExprDestination == 'POSELIBRARY' or not ob.pose_library: return False

        # can now assume ob is an armature with an active pose library
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.isExpressionCapable()