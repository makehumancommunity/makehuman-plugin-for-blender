#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

if "bpy" in locals():
    print("Reloading sync plug-in")
    import imp
    imp.reload(SyncOperator)
    imp.reload(SyncMeshOperator)
    imp.reload(SyncPoseOperator)
else:
    print("Loading sync plug-in")
    from . import SyncOperator
    from . import SyncMeshOperator
    from . import SyncPoseOperator

import bpy
print("sync plug-in loaded")