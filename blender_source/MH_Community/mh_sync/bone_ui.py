#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty

destinations = []
destinations.append( ("SHAPEKEYS", "Shape Keys", "Shapes keys on each mesh.  Check for pointless in Information area.", 1) )
destinations.append( ("POSELIBRARY", "Pose Library", "Write the expression to a Pose library", 2) )

def registerBoneConstantsAndSettings():
    # Properties for bone operations

    bpy.types.Scene.mhExprDestination = EnumProperty(items=destinations, name="Destination", description="Whether the resulting expressions are written as \nshape keys or into the current pose library.", default="SHAPEKEYS")
    bpy.types.Scene.MhNoLocation = BoolProperty(name="No Location Translation", description="Some Expressions have bone translation on locked bones.\nChecking this causes it to be cleared.  When false,\nALT-G will NOT clear these.", default=True)
    bpy.types.Scene.MhExprFilterTag = StringProperty(name="Tag", description="This is the tag to search for when getting expressions.\nBlank gets all expressions.", default="")


def addBoneUIToTab(layout, scn):
    
    layout.label(text="Bone Operations:", icon="ARMATURE_DATA")    

    rigifyBox = layout.box()
    rigifyBox.operator("mh_community.rigify")

    armSyncBox = layout.box()
    armSyncBox.label(text="Skeleton Sync:")
    armSyncBox.prop(scn, "MhNoLocation")
    armSyncBox.operator("mh_community.sync_pose", text="Sync with MH")
    armSyncBox.label(text="Expression Transfer:")
    armSyncBox.prop(scn, "mhExprDestination")
    armSyncBox.prop(scn, "MhExprFilterTag")
    armSyncBox.operator("mh_community.expressions_trans")

    layout.separator()
    ampBox = layout.box()
    ampBox.label(text="Amputations:")
    ampBox.operator("mh_community.amputate_fingers")
    ampBox.operator("mh_community.amputate_face")

    layout.separator()
    ikBox = layout.box()
    ikBox.label(text="IK Rig:")
    body = ikBox.row()
    body.operator("mh_community.add_ik_rig")
    body.operator("mh_community.remove_ik_rig")

    ikBox.label(text="Finger IK Rig:")
    finger = ikBox.row()
    finger.operator("mh_community.add_finger_rig")
    finger.operator("mh_community.remove_finger_rig")