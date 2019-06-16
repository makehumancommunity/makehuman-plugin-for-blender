#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty, CollectionProperty, FloatProperty

# extra classes to support animation lists
class MHC_UL_AnimationItems(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon='ARMATURE_DATA')

class AnimationProps(bpy.types.PropertyGroup):
    id: IntProperty()
    name: StringProperty()

#===============================================================================
def registerKinectConstantsAndSettings():
    bpy.utils.register_class(MHC_UL_AnimationItems)
    bpy.utils.register_class(AnimationProps)
    
    # Properties for kinect operations

    bpy.types.Scene.MhKinectCameraHeight = FloatProperty(name="Sensor Height", description="How high the sensor THINKS it is above floor in inches.\nMake sure this matches reality.  If not, adjust angle.", default = -1)

    bpy.types.Scene.MhKinectAnimations = CollectionProperty(type=AnimationProps)
    bpy.types.Scene.MhKinectAnimation_index = IntProperty(default=0)
    bpy.types.Scene.MhKinectBaseActionName = StringProperty(name="Action", description="This is the base name of the action to create.  To handle multiple bodies, this will be prefixed by armature.", default="untitled")
    bpy.types.Scene.MhExcludeFingers = BoolProperty(name="Exclude Fingers", default = False, description="When true, actions will not have key frames for finger & thumb bones")

    bpy.types.Scene.MhJitterMaxFrames = IntProperty(name='Max Duration', default=5, description="The maximum number of frames to detect that a bone quickly reversed itself.")
    bpy.types.Scene.MhJitterMinRetracement = FloatProperty(name='Min % Retracement', default=45, description="The percent of the move to be reversed to qualify as a jerk.")

def unregisterKinect():
    bpy.utils.unregister_class(AnimationProps)
    bpy.utils.unregister_class(MHC_UL_AnimationItems)
    bts = bpy.types.Scene
    del bts.MhKinectCameraHeight
    del bts.MhKinectAnimations
    del bts.MhKinectAnimation_index
    del bts.MhKinectBaseActionName
    del bts.MhExcludeFingers
    del bts.MhJitterMaxFrames
    del bts.MhJitterMinRetracement

KINECT_DEBUG_OPS = False

def addKinectUIToTab(layout, scn):
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
    kinectBoxAssignment.template_list("MHC_UL_AnimationItems", "", scn, "MhKinectAnimations", scn, "MhKinectAnimation_index")
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

    if KINECT_DEBUG_OPS:
       layout.operator("mh_community.pose_right")