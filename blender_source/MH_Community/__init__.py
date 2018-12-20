#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "MH Community Plug-in",
    "author": "Joel Palmius",
    "version": (0, 4),
    "blender": (2, 79, 0),
    "location": "View3D > Properties > MH",
    "description": "MakeHuman interactive operations",
    "wiki_url": "https://github.com/makehumancommunity/community-plugins/tree/master/blender_source/MH_Community",
    "category": "MakeHuman"}

if "bpy" in locals():
    print("Reloading MH community plug-in v %d.%d" % bl_info["version"])
    import imp
    imp.reload(mh_sync)  # directory
    imp.reload(kinect_sensor)  # directory
    imp.reload(rig)  # directory
    imp.reload(separate_eyes)
    imp.reload(animation_trimming)
else:
    print("Loading MH community plug-in v %d.%d" % bl_info["version"])
    from . import mh_sync # directory
    from . import kinect_sensor # directory
    from . import separate_eyes
    from .rig import RigInfo, BoneSurgery, IkRig, FingerRig
    from . import animation_trimming

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty
from .mh_sync.importer_ui import addImporterUIToTab, registerImporterConstantsAndSettings

#===============================================================================
class MHC_PT_Community_Panel(bpy.types.Panel):
    bl_label = "MakeHuman"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "MakeHuman"

    def draw(self, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor
        layout = self.layout
        scn = context.scene

        layout.prop(scn, 'mhTabs', expand=True)

        if scn.mhTabs == MESH_TAB:

            # Broken out to mh_sync/importer_ui
            addImporterUIToTab(layout, scn)

            layout.separator()

            generalSyncBox = layout.box()
            generalSyncBox.label(text="Various")
            generalSyncBox.operator("mh_community.sync_mh_mesh", text="Sync with MH")
            generalSyncBox.operator("mh_community.separate_eyes")

        elif scn.mhTabs == BONE_TAB:
            layout.label(text="Bone Operations:", icon="ARMATURE_DATA")
            armSyncBox = layout.box()
            armSyncBox.label(text="Skeleton Sync:")
            armSyncBox.prop(scn, "MhNoLocation")
            armSyncBox.operator("mh_community.sync_pose", text="Sync with MH")
            armSyncBox.label(text="Expression Transfer:")
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

        else:
            layout.label(text="Kinect V2 Integration:", icon="CAMERA_DATA")
            kinectBoxConversion = layout.box()
            kinectBoxConversion.label(text="Rig Conversion:")
            kinectBoxConversion.operator("mh_community.to_kinect2")

            kinectBoxCapture = layout.box()
            kinectBoxCapture.label(text="Motion Capture:")
            recordBtns = kinectBoxCapture.row()
            recordBtns.operator("mh_community.start_kinect", icon="RENDER_ANIMATION")
            recordBtns.operator("mh_community.stop_kinect", icon="CANCEL")
            results = kinectBoxCapture.row()
            results.prop(scn, "MhKinectCameraHeight")
            results.enabled = False

            kinectBoxAssignment = layout.box()
            kinectBoxAssignment.label(text="Action Assignment:")
            kinectBoxAssignment.operator("mh_community.refresh_kinect")
            kinectBoxAssignment.template_list("Animation_items", "", scn, "MhKinectAnimations", scn, "MhKinectAnimation_index")
            kinectBoxAssignment.prop(scn, "MhKinectBaseActionName")
            kinectBoxAssignment.prop(scn, "MhExcludeFingers")
            kinectBoxAssignment.operator("mh_community.assign_kinect")

            actionTrimming = layout.box()
            actionTrimming.label(text="Action Trimming:")
            cuts = actionTrimming.row()
            cuts.operator("mh_community.trim_left")
            cuts.operator("mh_community.trim_right")

            actionSmoothing = layout.box()
            actionSmoothing.label(text="Jitter Reduction:")
            actionSmoothing.prop(scn, "MhJitterMaxFrames")
            actionSmoothing.prop(scn, "MhJitterMinRetracement")
            actionSmoothing.operator("mh_community.smooth_animation")

            layout.operator("mh_community.pose_right")

#===============================================================================
# extra classes to support animation lists
class MHC_UL_AnimationItems(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon='BORDER_RECT')

class AnimationProps(bpy.types.PropertyGroup):
    id = IntProperty()
    name = StringProperty()

bpy.utils.register_class(AnimationProps)
#===============================================================================
MESH_TAB   = 'A'
BONE_TAB   = 'B'
KINECT_TAB = 'C'

# While MHX2 may set this, do not to rely on MHX.
bpy.types.Armature.exportedUnits = bpy.props.StringProperty(
    name='Exported Units',
    description='either METERS, DECIMETERS, or INCHES.  determined in RigInfo.determineExportedUnits().  Stored in armature do only do once.',
    default = ''
)

classes =  [
    MHC_PT_Community_Panel,
    MHC_UL_AnimationItems
]

from .operators import *

classes.extend(OPERATOR_CLASSES)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.mhTabs = bpy.props.EnumProperty(
    name='meshOrBoneOrKinect',
    items = (
             (MESH_TAB  , "Mesh"  , "Operators related to Make Human meshes"),
             (BONE_TAB  , "Rig"  , "IK & other bone operators on Make Human skeletons"),
             (KINECT_TAB, "Kinect", "Motion Capture using Kinect V2 for converted Make Human meshes"),
        ),
    default = MESH_TAB
)
    bpy.types.Scene.MhNoLocation = BoolProperty(name="No Location Translation", description="Some Expressions have bone translation on locked bones.\nChecking this causes it to be cleared.  When false,\nALT-G will NOT clear these.", default=True)
    bpy.types.Scene.MhExprFilterTag = StringProperty(name="Tag", description="This is the tag to search for when getting expressions.\nBlank gets all expressions.", default="")
    bpy.types.Scene.MhKinectCameraHeight = FloatProperty(name="Sensor Height", description="How high the sensor THINKS it is above floor in inches.\nMake sure this matches reality.  If not, adjust angle.", default = -1)

    bpy.types.Scene.MhKinectAnimations = CollectionProperty(type=AnimationProps)
    bpy.types.Scene.MhKinectAnimation_index = IntProperty(default=0)
    bpy.types.Scene.MhKinectBaseActionName = StringProperty(name="Action", description="This is the base name of the action to create.  To handle multiple bodies, this will be prefixed by armature.", default="untitled")
    bpy.types.Scene.MhExcludeFingers = BoolProperty(name="Exclude Fingers", default = False, description="When true, actions will not have key frames for finger & thumb bones")

    bpy.types.Scene.MhJitterMaxFrames = IntProperty(name='Max Duration', default=5, description="The maximum number of frames to detect that a bone quickly reversed itself.")
    bpy.types.Scene.MhJitterMinRetracement = FloatProperty(name='Min % Retracement', default=90, description="The percent of the move to be reversed to qualify as a jerk.")

    registerImporterConstantsAndSettings()


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.MhNoLocation
    del bpy.types.Scene.MhExprFilterTag

    del bpy.types.Scene.MhKinectCameraHeight
    del bpy.types.Scene.MhKinectBaseActionName

    del bpy.types.Scene.MhKinectAnimations
    del bpy.types.Scene.MhKinectAnimation_index
    del bpy.types.Scene.MhExcludeFingers
    
    del bpy.types.Scene.MhJitterMaxFrames
    del bpy.types.Scene.MhJitterMinRetracement

    del bpy.types.Scene.MhHandleHelper
    del bpy.types.Scene.MhScaleMode

if __name__ == "__main__":
    unregister()
    register()

print("MH community plug-in load complete")