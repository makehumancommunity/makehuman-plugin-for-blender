#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

if "bpy" in locals():
    print("Reloading sync plug-in")
    import imp
    imp.reload(sync_ops)
    imp.reload(sync_mesh)
    imp.reload(sync_pose)
    imp.reload(import_body_binary)
    imp.reload(directory_ops)
    imp.reload(expr_to_poselib)
else:
    print("Loading sync plug-in")
    from . import sync_ops
    from . import sync_mesh
    from . import sync_pose
    from . import import_body_binary
    from . import directory_ops
    from . import expr_to_poselib

import bpy
print("sync plug-in loaded")