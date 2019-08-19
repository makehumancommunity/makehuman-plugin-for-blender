from .empties import *
from ..rig import BoneSurgery, RigInfo

from math import radians
import bpy

TMP_SKEL_NAME = 'captureArmature'
#===============================================================================
class CaptureArmature:
    def __init__(self, rigInfo, sensorMappingToBones, sensorJointDict, firstBody):
        self.rigInfo = rigInfo
        self.retargetTo = rigInfo.armature
        self.sensorMappingToBones = sensorMappingToBones

        # need to get these while target skeleton is still the active object
        unitMult = self.rigInfo.unitMultplierToExported()
        bBoneSz = 0.06 * unitMult

        # target must be at rest before copying
        bpy.ops.object.mode_set(mode='POSE')
        self.setActiveObject(self.retargetTo)
        bpy.ops.pose.select_all(action = 'SELECT')
        bpy.ops.pose.transforms_clear()

        bpy.ops.object.mode_set(mode='OBJECT')
        self.retargetTo.select_set(True) # THIS is what is required to duplicate, not active
        bpy.ops.object.duplicate(linked=False)

        self.captureSkel = bpy.context.active_object
        self.captureSkel.name = TMP_SKEL_NAME
        BoneSurgery.connectSkeleton(self.captureSkel, False) # actually, False indicates to disconnect everything

        # - - - - - - - - - - - - - - - - - - - - - -
        # for better debug, change to b-bone
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action = 'SELECT')
        if bpy.app.version < (2, 80, 0):
            self.captureSkel.data.draw_type = 'BBONE'
        else:
            self.captureSkel.data.display_type = 'BBONE'

        bpy.ops.transform.transform(mode='BONE_SIZE', value=(bBoneSz, bBoneSz, bBoneSz, 0))

        self.constraintsAdded = False
        self.limitsAdded = False

        self.empties = Empties(RigInfo.determineRig(self.captureSkel), sensorMappingToBones, sensorJointDict, firstBody)

    #===========================================================================
    def addConstraints(self):
        # assign copyRotation from captured to retargeted
        bpy.ops.object.mode_set(mode='POSE')
        for jointName, boneName in self.sensorMappingToBones.items():
            if boneName is None or boneName not in self.retargetTo.pose.bones: continue

            bone = self.retargetTo.pose.bones[boneName]
            constraint = bone.constraints.new('COPY_ROTATION')
            constraint.target = self.captureSkel
            constraint.subtarget = bone.name

            # Any parts of an arm MUST be WORLD to WORLD, since TPose may not be how was imported.
            # Where as all vertical bones need to be LOCAL to LOCAL to avoid having to position bones.
            # The sensor also can very by temperature / clothes, so it impossible to come up with one.
            space = 'WORLD' if self.rigInfo.isArmBone(bone.name) else 'LOCAL'
            constraint.owner_space = space
            constraint.target_space = space

            constraint.name = 'RETARGET_ROT'

        # also add copy location for root bone, not in sensorMappingToBones
        bone = self.retargetTo.pose.bones[self.rigInfo.root]
        constraint = bone.constraints.new('COPY_LOCATION')
        constraint.target = self.captureSkel
        constraint.subtarget = bone.name
        constraint.name = 'RETARGET_LOC'

        self.constraintsAdded = True

    #===========================================================================
    def addLimits(self):
        bpy.ops.object.mode_set(mode='POSE')
        self.addRotationLimit(self.rigInfo.head           , -20, 40,    -40, 40,    -20, 20)
        self.addRotationLimit(self.rigInfo.neckBase       , -20, 25,    -40, 40,    -20, 20)
#        self.addRotationLimit(self.rigInfo.upperSpine     , -20, 30,    -40, 40,    -20, 20)
#        self.addRotationLimit(self.rigInfo.pelvis         , -20, 70,    -50, 50,    -35, 35)

#        self.addRotationLimit(self.rigInfo.clavicle(True ), -20, 20,    -20, 20,    -10, 10)
#        self.addRotationLimit(self.rigInfo.clavicle(False), -20, 20,    -20, 20,    -10, 10)

        self.addRotationLimit(self.rigInfo.hand(True )    , -20, 20,    -60, 50,    -50, 50)
        self.addRotationLimit(self.rigInfo.hand(False)    , -20, 20,    -60, 50,    -50, 50)

        self.addRotationLimit(self.rigInfo.thumb(True )   , -30, 45,    -40, 40,    -20, 20)
        self.addRotationLimit(self.rigInfo.thumb(False)   , -30, 45,    -40, 40,    -20, 20)

        self.addRotationLimit(self.rigInfo.handTip(True ) , -20, 10,    -20, 20,    -10, 10)
        self.addRotationLimit(self.rigInfo.handTip(False) , -20, 10,    -20, 20,    -10, 10)

#        self.addRotationLimit(self.rigInfo.thigh(True )   , -90, 50,    -30, 30,    -30, 10)
#        self.addRotationLimit(self.rigInfo.thigh(False)   , -90, 50,    -30, 30,    -10, 30)

#        self.addRotationLimit(self.rigInfo.calf(True )    ,  -1, 40,    -20, 20,    -10, 10)
#        self.addRotationLimit(self.rigInfo.calf(False)    ,  -1, 40,    -20, 20,    -10, 10)

        self.addRotationLimit(self.rigInfo.calf(True )    ,  -.1, 120,    0, 0,    0, 0)
        self.addRotationLimit(self.rigInfo.calf(False)    ,  -.1, 120,    0, 0,    0, 0)

        self.addRotationLimit(self.rigInfo.foot(True )    ,  -5, 10,     -1,  1,     -5,  5)
        self.addRotationLimit(self.rigInfo.foot(False)    ,  -5, 10,     -1,  1,     -5,  5)

        self.limitsAdded = True

    def addRotationLimit(self, boneName, xMin = 0, xMax = 0, yMin = 0, yMax = 0, zMin = 0, zMax = 0):
        if boneName is None or boneName is not boneName in self.retargetTo.pose.bones: return

        constraint = self.retargetTo.pose.bones[boneName].constraints.new('LIMIT_ROTATION')
        constraint.use_transform_limit = True
        constraint.owner_space = 'LOCAL'
        constraint.name = 'RETARGET_ROT_LIMIT'

        if xMin != 0 or xMax != 0:
            constraint.use_limit_x = True
            if xMin != 0:
                constraint.min_x = radians(xMin)
            if xMax != 0:
                constraint.max_x = radians(xMax)

        if yMin != 0 or yMax != 0:
            constraint.use_limit_y = True
            if yMin != 0:
                constraint.min_y = radians(yMin)
            if yMax != 0:
                constraint.max_y = radians(yMax)

        if zMin != 0 or zMax != 0:
            constraint.use_limit_z = True
            if zMin != 0:
                constraint.min_z = radians(zMin)
            if zMax != 0:
                constraint.max_z = radians(zMax)
    #===========================================================================
    # called every frame, after all the empties have been set, which the capture armature contrstrainted by
    def assignAndRetargetFrame(self, jointData):
        self.empties.assign(jointData)

        if not self.constraintsAdded:
            self.update()

            # set the first frame as the rest pose of the captured skeleton
            self.setActiveObject(self.captureSkel)
            bpy.ops.pose.armature_apply()

            # add the contraints from the captured skeleton to the target skeleton
            self.addConstraints()
            self.addLimits()

        # get changes applied for the next step
        self.update()
    #===========================================================================
    # nuke duplicate armature
    def cleanUp(self):
        # could have been refreshed in a new scene, double check that there is stuff to clean
        if TMP_SKEL_NAME not in bpy.data.objects: return

        self.empties.nukeConstraints()
        self.empties.nuke()

        bpy.ops.object.mode_set(mode='OBJECT')
        objs = bpy.data.objects
        objs.remove(objs[TMP_SKEL_NAME], do_unlink = True)

        self.setActiveObject(self.retargetTo)
        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.retargetTo.pose.bones:
            for c in bone.constraints:
                if 'RETARGET' in c.name:
                    bone.constraints.remove(c)

        # return target skeleton to rest pose
        bpy.ops.pose.select_all(action = 'SELECT')
        bpy.ops.pose.transforms_clear()

    #===========================================================================
    # abstracted for differences between Blender 2.79 & 2.80, nuke eventually
    def setActiveObject(self, object):
        if bpy.app.version < (2, 80, 0):
            bpy.context.scene.objects.active = object
        else:
            bpy.context.view_layer.objects.active = object

    # abstracted for differences between Blender 2.79 & 2.80, nuke eventually
    def update(self):
        if bpy.app.version < (2, 80, 0):
            bpy.context.scene.update()
        else:
            bpy.context.view_layer.update()
