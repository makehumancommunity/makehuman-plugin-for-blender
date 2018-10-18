#!/usr/bin/python
# -*- coding: utf-8 -*-

bl_info = {
    "name": "MH Community Plug-in",
    "author": "Joel Palmius",
    "version": (0, 4),
    "blender": (2, 80, 0),
    "location": "View3D > Properties > MH",
    "description": "MakeHuman interactive operations",
    "wiki_url": "https://github.com/makehumancommunity/community-plugins/tree/master/blender_source/MH_Community",
    "category": "MakeHuman"}

if "bpy" in locals():
    print("Reloading MH community plug-in v %d.%d" % bl_info["version"])
    import imp
    imp.reload(mh_sync)  # directory
    imp.reload(kinect_sensor)  # directory
    imp.reload(separate_eyes)
    imp.reload(snap_on_finger_rig)
    imp.reload(snap_on_ik_rig)
    imp.reload(rig_info)
    imp.reload(bone_surgery)
    imp.reload(animation_trimming)
else:
    print("Loading MH community plug-in v %d.%d" % bl_info["version"])
    from . import mh_sync # directory
    from . import kinect_sensor # directory
    from . import separate_eyes
    from . import snap_on_finger_rig
    from . import snap_on_ik_rig
    from . import rig_info
    from . import bone_surgery
    from . import animation_trimming

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

from .body_import_operator import BodyImportOperator

#===============================================================================
#===============================================================================
class Community_Panel(bpy.types.Panel):
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
            importHumanBox = layout.box()
            importHumanBox.label(text="Import human", icon="MESH_DATA")
            importHumanBox.label(text="Helper geom:")
            importHumanBox.prop(scn, 'handle_helper', text="")
            importHumanBox.separator()
            importHumanBox.operator("mh_community.import_body", text="Import human")

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
class MeshSyncOperator(bpy.types.Operator):
    """Synchronize the shape of a human with MH"""
    bl_idname = "mh_community.sync_mh_mesh"
    bl_label = "Synchronize MH Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .mh_sync.sync_mesh import SyncMesh
        SyncMesh()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'MESH'
#===============================================================================
HIPOLY_VERTS  = 1064
LOWPOLY_VERTS = 96
class SeparateEyesOperator(bpy.types.Operator):
    """Separate The Eye mesh into left & right meshes, and move origin to center of mass of each."""
    bl_idname = 'mh_community.separate_eyes'
    bl_label = 'Separate Eyes'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .separate_eyes import SeparateEyes

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
#===============================================================================
class PoseSyncOperator(bpy.types.Operator):
    """Synchronize the pose of the skeleton of a human with MH.  Requirements:\n\nMust be the Default armature.\nMust be exported in decimeters to allow location translation."""
    bl_idname = "mh_community.sync_pose"
    bl_label = "Synchronize MH Pose"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .mh_sync.sync_pose import SyncPose

        armature = context.object
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo.determineExportedUnits != 'DECIMETERS' and not bpy.context.scene.MhNoLocation:
            self.report({'ERROR'}, 'Location translation only possible when exported in decimeters to match MakeHuman.')
            return {'FINISHED'}

        SyncPose()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.isPoseCapable()
#===============================================================================
class ExpressionTransOperator(bpy.types.Operator):
    """Transfer MakeHuman expressions to a pose library.  Requirements:\n\nMust be the Default armature.\nMust be exported in decimeters to allow location translation.\nMust have a current Pose library."""
    bl_idname = "mh_community.expressions_trans"
    bl_label = "To Pose library"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .mh_sync.expr_to_poselib import ExprToPoselib

        armature = context.object
        rigInfo = RigInfo.determineRig(armature)
        if rigInfo.determineExportedUnits != 'DECIMETERS' and not bpy.context.scene.MhNoLocation:
            self.report({'ERROR'}, 'Location translation only possible when exported in decimeters to match MakeHuman.')
            return {'FINISHED'}

        ExprToPoselib()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE' or not ob.pose_library: return False

        # can now assume ob is an armature with an active pose library
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.isExpressionCapable()
#===============================================================================
# so small, no additional file required
class AmputateFingersOperator(bpy.types.Operator):
    """Remove finger bones, and assign their weights to hand bone"""
    bl_idname = "mh_community.amputate_fingers"
    bl_label = "Fingers"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo, Kinect2RigInfo
        from .bone_surgery import BoneSurgery
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        # find all meshes which use this armature
        meshes = rigInfo.getMeshesForRig(context.scene)

        BoneSurgery.amputate(armature, meshes, rigInfo.hand(True ))
        BoneSurgery.amputate(armature, meshes, rigInfo.hand(False))

        # kinect2 also needs to delete Thumbs, which got re-parent higher
        if rigInfo.name == 'Kinect2 Rig':
            BoneSurgery.deleteBone(armature, meshes, Kinect2RigInfo.boneFor('Thumb', True ), Kinect2RigInfo.boneFor('Hand', True ))
            BoneSurgery.deleteBone(armature, meshes, Kinect2RigInfo.boneFor('Thumb', False), Kinect2RigInfo.boneFor('Hand', False))

        self.report({'INFO'}, 'Amputated fingers to ' + rigInfo.name)
        return {'FINISHED'}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.hasFingers()
#===============================================================================
# so small, no additional file required
class AmputateFaceOperator(bpy.types.Operator):
    """Remove face bones, and assign their weights to head bone"""
    bl_idname = "mh_community.amputate_face"
    bl_label = "Face"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .bone_surgery import BoneSurgery
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        # find all meshes which use this armature
        meshes = rigInfo.getMeshesForRig(context.scene)

        # could still have face bones on Kinect2 rig, which has different name, so check by rig
        boneName = 'head' if rigInfo.name == 'Default Rig' else 'Head'
        BoneSurgery.amputate(armature, meshes, boneName)

        self.report({'INFO'}, 'Amputated fingers to ' + rigInfo.name)
        return {'FINISHED'}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.isExpressionCapable()
#===============================================================================
class SnapOnIkRigOperator(bpy.types.Operator):
    """Add bones which convert this to an IK Rig\n\nOnly Game or Kinect2 rigs."""
    bl_idname = 'mh_community.add_ik_rig'
    bl_label = '+'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .snap_on_ik_rig import IkRig
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        IkRig(rigInfo).add()

        self.report({'INFO'}, 'Added IK Rig to ' + rigInfo.name)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or not rigInfo.IKCapable(): return False

        # just need to check not already added
        return not rigInfo.hasIK()
#===============================================================================
class RemoveIkRigOperator(bpy.types.Operator):
    """Remove the IK rig previously added."""
    bl_idname = 'mh_community.remove_ik_rig'
    bl_label = '-'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .snap_on_ik_rig import IkRig
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        IkRig(rigInfo).remove()

        self.report({'INFO'}, 'Removed IK Rig')
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.hasIK()
#===============================================================================
class SnapOnFingerRigOperator(bpy.types.Operator):
    """Snap on finger control bones.\nNote an IK rig is always added with .ik in bones names, regardless of imported with MHX or Collada."""
    bl_idname = 'mh_community.add_finger_rig'
    bl_label = '+'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .snap_on_finger_rig import FingerRig
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        FingerRig(rigInfo).add()

        self.report({'INFO'}, 'Added finger IK Rig to ' + rigInfo.name)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or not rigInfo.fingerIKCapable(): return False

        # just need to check not already added
        return not rigInfo.hasFingerIK()
#===============================================================================
class RemoveFingerRigOperator(bpy.types.Operator):
    """Remove the finger IK rig previously added."""
    bl_idname = 'mh_community.remove_finger_rig'
    bl_label = '-'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .snap_on_finger_rig import FingerRig
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None:
            report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        FingerRig(rigInfo).remove()

        self.report({'INFO'}, 'Removed finger IK Rig')
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        return rigInfo is not None and rigInfo.hasFingerIK()
#===============================================================================
class ToKinect2Operator(bpy.types.Operator):
    """Transform a default Rig, with or without toes, to one suited for use with an XBox One Kinect-2 device.\n\nCannot be done after fingers have been amputated,\nor a finger IK has been added."""
    bl_idname = 'mh_community.to_kinect2'
    bl_label = 'Convert Rig'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .rig_info import RigInfo
        from .kinect_sensor.to_kinect2 import ToKinectV2
        armature = context.object

        rigInfo = RigInfo.determineRig(armature)
        if rigInfo is None or rigInfo.name != 'Default Rig':
            self.report({'ERROR'}, 'Rig is not the default Rig')
            return {'FINISHED'}

        #if not rigInfo.hasRestTpose():
        #    self.report({'ERROR'}, 'Must be exported in T-Pose to use sensor')
        #    return {'FINISHED'}

        ToKinectV2(rigInfo).convert()

        self.report({'INFO'}, 'Converted to a Kinect2 rig')
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or rigInfo.name != 'Default Rig' or not rigInfo.fingerIKCapable(): return False

        # just need to check IK rig not already added
        return not rigInfo.hasIKRigs()

#===============================================================================
class StartKinectRecordingOperator(bpy.types.Operator):
    """Begin a Kinect motion capture session.\n\nCan only be done on Windows."""
    bl_idname = 'mh_community.start_kinect'
    bl_label = 'Record'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor

        KinectSensor.capture()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor
        return KinectSensor.isKinectReady() and not KinectSensor.recording
#===============================================================================
class StopKinectRecordingOperator(bpy.types.Operator):
    """Complete a Kinect motion capture session."""
    bl_idname = 'mh_community.stop_kinect'
    bl_label = 'Stop'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor

        KinectSensor.close()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor
        return KinectSensor.isKinectReady() and KinectSensor.recording

    import bpy
#===============================================================================
class KinectAssignmentOperator(bpy.types.Operator):
    """Assign an animation to an action of the selected skeleton.\n\nCan only be done to a Kinect2 rig."""
    bl_idname = 'mh_community.assign_kinect'
    bl_label = 'Assign'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor

        armature = context.object
        baseActionName = context.scene.MhKinectBaseActionName
        excludeFingers = context.scene.MhExcludeFingers

        KinectSensor.assign(armature, context.scene.MhKinectAnimation_index, baseActionName, excludeFingers)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or rigInfo.name != 'Kinect2 Rig' or rigInfo.hasIKRigs(): return False

        return len(context.scene.MhKinectAnimations) > 0
#===============================================================================
class KinectRefreshOperator(bpy.types.Operator):
    """Re-populate any captures recorded with a previously loaded blend.\nGood for populating multi-character animation across .blend files."""
    bl_idname = 'mh_community.refresh_kinect'
    bl_label = 'Refresh List'
    bl_options = {'REGISTER'}

    def execute(self, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor

        KinectSensor.displayRecordings()
        return {'FINISHED'}
#===============================================================================
class PoseRightOperator(bpy.types.Operator):
    """This is a diagnostic operator, which poses both the capture & final armatures one frame at a time."""
    bl_idname = 'mh_community.pose_right'
    bl_label = '1 Right'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .kinect_sensor.kinect2_runtime import KinectSensor

        armature = context.object
        KinectSensor.oneRight(armature, context.scene.MhKinectAnimation_index)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        from .rig_info import RigInfo
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        # can now assume ob is an armature
        rigInfo = RigInfo.determineRig(ob)
        if rigInfo is None or rigInfo.name != 'Kinect2 Rig': return False

        return len(context.scene.MhKinectAnimations) > 0
#===============================================================================
class ActionTrimLeftOperator(bpy.types.Operator):
    """Remove all keyframes, of the current action, before the current frame, shifting remaining to the left.\n\nCan be done with any armature based action against any rig."""
    bl_idname = 'mh_community.trim_left'
    bl_label = 'Left'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .animation_trimming import AnimationTrimming

        armature = context.object
        trimmer = AnimationTrimming(armature)
        trimmer.deleteAndShift()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        return ob.animation_data is not None
#===============================================================================
class ActionTrimRightOperator(bpy.types.Operator):
    """Remove all keyframes, of the current action, after the current frame.\n\nCan be done with any armature based action against any rig."""
    bl_idname = 'mh_community.trim_right'
    bl_label = 'Right'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .animation_trimming import AnimationTrimming

        armature = context.object
        trimmer = AnimationTrimming(armature)
        trimmer.dropToRight()
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        return ob.animation_data is not None
#===============================================================================
class ActionJitterReducerOperator(bpy.types.Operator):
    """Smooth armature movements which get quickly reversed through data reduction.\n\nCan be done with any armature based action against any rig.\n\nDo not do multiple times.  Undo, change args, & do again."""
    bl_idname = 'mh_community.smooth_animation'
    bl_label = 'Smooth'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        from .kinect_sensor.jitter_reduction import JitterReduction

        armature = context.object
        JitterReduction(armature, context.scene.MhJitterMaxFrames, context.scene.MhJitterMinRetracement)
        return {'FINISHED'}
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        if ob is None or ob.type != 'ARMATURE': return False

        return ob.animation_data is not None
#===============================================================================
# extra classes to support animation lists
class Animation_items(bpy.types.UIList):
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

classes =  (
    Community_Panel,
    MeshSyncOperator,
    BodyImportOperator,
    SeparateEyesOperator,
    PoseSyncOperator,
    ExpressionTransOperator,
    AmputateFingersOperator,
    AmputateFaceOperator,
    SnapOnIkRigOperator,
    RemoveIkRigOperator,
    SnapOnFingerRigOperator,
    RemoveFingerRigOperator,
    ToKinect2Operator,
    StartKinectRecordingOperator,
    StopKinectRecordingOperator,
    KinectAssignmentOperator,
    KinectRefreshOperator,
    PoseRightOperator,
    ActionTrimLeftOperator,
    ActionTrimRightOperator,
    ActionJitterReducerOperator,
    Animation_items
)

handleHelperItems = []
handleHelperItems.append( ("MASK", "Mask", "Mask helper geometry", 1) )
handleHelperItems.append( ("NOTHING", "Leave be", "Leave helper geometry as is", 2) )
handleHelperItems.append( ("DELETE", "Delete", "Delete helper geometry", 3))

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.mhTabs = bpy.props.EnumProperty(
    name='meshOrBoneOrKinect',
    items = (
             (MESH_TAB  , "Mesh"  , "Operators related to Make Human meshes"),
             (BONE_TAB  , "Bone / IK"  , "IK & other bone operators on Make Human skeletons"),
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

    bpy.types.Scene.handle_helper = bpy.props.EnumProperty(items=handleHelperItems, name="handle_helper", description="Handle helpers", default="MASK")

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

    del bpy.types.Scene.handle_helper

if __name__ == "__main__":
    unregister()
    register()

print("MH community plug-in load complete")