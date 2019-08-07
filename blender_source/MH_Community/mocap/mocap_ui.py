#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy.props import BoolProperty, EnumProperty, StringProperty, IntProperty, CollectionProperty, FloatProperty

sensorTypeItems = []
sensorTypeItems.append( ('KINECT2', 'Kinect2', 'A Kinect2 either from an XBox 1, or from an XBox 360 with the USB adapter kit', 1) )

# extra classes to support animation lists
class MHC_UL_AnimationItems(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False, translate=False, icon='ARMATURE_DATA')

class AnimationProps(bpy.types.PropertyGroup):
    id: IntProperty()
    name: StringProperty()

#===============================================================================
def registerMocapConstantsAndSettings():
    bpy.utils.register_class(MHC_UL_AnimationItems)
    bpy.utils.register_class(AnimationProps)

    # Properties for mocap operations
    bpy.types.Scene.MhSensorType = EnumProperty(items = sensorTypeItems, name = 'Type', description = 'The type of sensor you have connected to your computer', default = 'KINECT2' )

    bpy.types.Scene.MhSensorCameraHeight = FloatProperty(name="Sensor Height", description="How high the sensor THINKS it is above floor in inches.\nMake sure this matches reality.  If not, adjust angle.", default = -1)

    bpy.types.Scene.MhSensorAnimations = CollectionProperty(type=AnimationProps)
    bpy.types.Scene.MhSensorAnimation_index = IntProperty(default=0)
    bpy.types.Scene.MhSensorBaseActionName = StringProperty(name="Action", description="This is the base name of the action to create.  To handle multiple bodies, this will be prefixed by armature.", default="untitled")
    bpy.types.Scene.MhExcludeFingers = BoolProperty(name="Exclude Fingers", default = False, description="When true, actions will not have key frames for finger & thumb bones")

    bpy.types.Scene.MhReversalMinRetracement = FloatProperty(name='Min % Retracement', default=45, description="The percent of the move to be reversed to qualify as a reversal.")

def unregisterMocap():
    bpy.utils.unregister_class(AnimationProps)
    bpy.utils.unregister_class(MHC_UL_AnimationItems)
    bts = bpy.types.Scene
    del bts.MhSensorType
    del bts.MhSensorCameraHeight
    del bts.MhSensorAnimations
    del bts.MhSensorAnimation_index
    del bts.MhSensorBaseActionName
    del bts.MhExcludeFingers
    del bts.MhReversalMinRetracement

MOCAP_DEBUG_OPS = False

def addMocapUIToTab(layout, scn):
    layout.label(text="Sensor Integration:", icon="CAMERA_DATA")
    sensorDevice = layout.box()
    sensorDevice.label(text="Sensor Device:")
    sensorDevice.prop(scn, "MhSensorType")
    sensorDevice.operator("mh_community.to_sensor_rig")

    BoxCapture = layout.box()
    BoxCapture.label(text="Motion Capture:")
    recordBtns = BoxCapture.row()
    recordBtns.operator("mh_community.start_mocap", icon="RENDER_ANIMATION")
    recordBtns.operator("mh_community.stop_mocap", icon="CANCEL")
    results = BoxCapture.row()
    results.prop(scn, "MhSensorCameraHeight")
    results.enabled = False

    boxAssignment = layout.box()
    boxAssignment.label(text="Action Assignment:")
    boxAssignment.operator("mh_community.refresh_mocap")
    boxAssignment.template_list("MHC_UL_AnimationItems", "", scn, "MhSensorAnimations", scn, "MhSensorAnimation_index")
    boxAssignment.prop(scn, "MhSensorBaseActionName")
    boxAssignment.prop(scn, "MhExcludeFingers")
    boxAssignment.operator("mh_community.assign_mocap")

    actionTrimming = layout.box()
    actionTrimming.label(text="Action Trimming:")
    cuts = actionTrimming.row()
    cuts.operator("mh_community.trim_left")
    cuts.operator("mh_community.trim_right")

    actionSmoothing = layout.box()
    actionSmoothing.label(text="Key Frame Reduction:")
    actionSmoothing.prop(scn, "MhReversalMinRetracement")
    actionSmoothing.operator("mh_community.keyframe_animation")

    if MOCAP_DEBUG_OPS:
       layout.operator("mh_community.pose_right")