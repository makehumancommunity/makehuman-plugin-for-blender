#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "MH Community Plug-in",
    "author": "Joel Palmius",
    "version": (0, 2),
    "blender": (2, 77, 0),
    "location": "View3D > Properties > MH",
    "description": "Post import MakeHuman operations",
    "wiki_url": "https://github.com/makehumancommunity/community-plugins/tree/master/blender_source/MH_Community",
    "category": "MakeHuman"}

if "bpy" in locals():
    print("Reloading MH community plug-in v %d.%d" % bl_info["version"])
    import imp
    imp.reload(mh_sync)  # directory
    imp.reload(separate_eyes)
    imp.reload(snap_on_finger_rig)
    imp.reload(snap_on_ik_rig)
    imp.reload(amputate_fingers)
    imp.reload(rig_info)
else:
    print("Loading MH community plug-in v %d.%d" % bl_info["version"])
    from . import mh_sync # directory
    from . import separate_eyes
    from . import snap_on_finger_rig
    from . import snap_on_ik_rig
    from . import amputate_fingers
    from . import rig_info

import bpy

class Community_Panel(bpy.types.Panel):
    bl_label = "Community"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MakeHuman"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Mesh Operations:", icon="MESH_DATA")
        layout.operator("mh_community.sync_mh_mesh", text="Sync with MH")
        layout.operator("mh_community.separate_eyes", text="Separate Eyes")

        layout.separator()

        layout.label(text="Bone Operations:", icon="ARMATURE_DATA")
        layout.operator("mh_community.sync_pose", text="Sync with MH")
        layout.operator("mh_community.ik_rig", text="Convert to IK rig")
        layout.operator("mh_community.finger_rig", text="Add Finger IK Bones")
        layout.operator("mh_community.amputate_fingers", text="Remove Finger Bones")

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    unregister()
    register()

print("MH community plug-in load complete")