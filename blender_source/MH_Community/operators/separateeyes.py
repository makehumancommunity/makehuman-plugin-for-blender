#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

HIPOLY_VERTS  = 1064
LOWPOLY_VERTS = 96
class SeparateEyesOperator(bpy.types.Operator):
    """Separate The Eye mesh into left & right meshes, and move origin to center of mass of each."""
    bl_idname = 'mh_community.separate_eyes'
    bl_label = 'Separate Eyes'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..separate_eyes import SeparateEyes

        SeparateEyes(context.object)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object

        # must be a mesh
        if not ob or ob.type != 'MESH':
            return False

        # vertex count must match
        nVerts = len(ob.data.vertices)
        return nVerts == HIPOLY_VERTS or nVerts == LOWPOLY_VERTS