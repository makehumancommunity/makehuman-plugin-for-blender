#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_MeshSyncOperator(bpy.types.Operator):
    """Synchronize the shape of a human with MH"""
    bl_idname = "mh_community.sync_mh_mesh"
    bl_label = "Synchronize MH Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from ..mh_sync.sync_mesh import SyncMesh
        SyncMesh()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'MESH'