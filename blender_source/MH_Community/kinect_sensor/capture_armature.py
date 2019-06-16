from .to_kinect2 import *

import bpy
#===============================================================================
TMP_SKEL_NAME = 'captureArmature'
class CaptureArmature:
    def __init__(self, retargetTo):
        self.scene = bpy.context.scene

        self.retargetTo = retargetTo

        self.captureSkel = self.scene.objects.get(TMP_SKEL_NAME)
        # duplicate the capture skeleton
        if self.captureSkel is None:
            bpy.ops.object.mode_set(mode='OBJECT')
            self.setActiveObject(self.retargetTo)                
            bpy.ops.object.duplicate(linked=False)

            self.captureSkel = bpy.context.active_object
            self.captureSkel.name = TMP_SKEL_NAME
            ToKinectV2.connectBones(self.captureSkel, False) # actually, False indicates to disconnect everything

            # assign copyRotation from captured to retargeted
            bpy.ops.object.mode_set(mode='POSE')
            for bone in self.retargetTo.pose.bones:
                constraint = bone.constraints.new('COPY_ROTATION')
                constraint.target = self.captureSkel
                constraint.subtarget = bone.name
                constraint.name = 'RETARGET'

    # nuke duplicate armature & remove any constraints on bones with the name 'RETARGET'
    def cleanUp(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        self.setActiveObject(self.captureSkel)
        bpy.ops.object.delete(use_global = False)

        self.setActiveObject(self.retargetTo)
        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.retargetTo.pose.bones:
            for c in bone.constraints:
                if c.name == 'RETARGET':
                    bone.constraints.remove(c)
                    
    def setActiveObject(self, object):
        if bpy.app.version < (2, 80, 0):
            self.scene.objects.active = object
        else:
            bpy.context.view_layer.objects.active = object
