#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os

bl_info = {
    "name": "MH Sync Mesh",
    "author": "Joel Palmius",
    "version": (0, 1),
    "blender": (2, 6, 76),
    "location": "View3D > Properties > MH",
    "description": "SyncMesh",
    "category": "MakeHuman"}


if "bpy" in locals():
    print("Reloading plugin")
    import imp
    imp.reload(SyncMeshOperator)
    imp.reload(SyncPanel)
else:
    print("Loading plugin")

    from . import SyncMeshOperator
    from . import SyncPanel

import bpy
from bpy.props import *
from bpy_extras.io_utils import ImportHelper, ExportHelper


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()


