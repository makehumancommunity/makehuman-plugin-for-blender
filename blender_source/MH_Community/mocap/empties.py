from .capture_armature import *
from ..rig.riginfo import *

from mathutils import Vector
import bpy
#===============================================================================
ARMATURE_BASE = 'ARMATURE_BASE'
class Empties:
    def __init__(self, captureArmature, targetRigInfo, mappingToBones, sensorJointDict):
        self.armature = captureArmature # member for nukeConstraints() & root bone rotation
        self.targetRigInfo = targetRigInfo
        self.sensorJointDict = sensorJointDict
        self.mappingToBones = mappingToBones

        self.constraintsApplied = False
        self.mult = Vector((1, 1, 1))

        # record the bone lengths of the armature getting proper location root bone base
        self.rootLength = self.armature.pose.bones[targetRigInfo.root].length
        self.spineBaseHeightWorldSpace = targetRigInfo.getSpineBaseHeightWorldSpace()

        # Add all the empties in OBJECT Mode, one for each bone
        # use the Bone list, not bones though, since user could have removed fingers
        bpy.ops.object.mode_set(mode='OBJECT')
        self.empties = {}
        for jointName, parentName in self.sensorJointDict.items():
            self.addEmpty(jointName)

        #  add one for the base of the root bone
#        self.addEmpty(ARMATURE_BASE)

    def addEmpty(self, jointName):
        o = bpy.data.objects.new(jointName, None)

        if bpy.app.version < (2, 80, 0):
            o.empty_draw_size = 0.1
            o.empty_draw_type = 'ARROWS'
            o.name = jointName
#            o.show_name = True
            bpy.context.scene.objects.link(o) # needed to make visible, not really required outside of dev
        else:
            o.empty_display_size = 0.1
            o.empty_display_type = 'PLAIN_AXES'
#                o.show_name = True
            bpy.context.scene.collection.objects.link(o) # needed to make visible, not really required outside of dev

        self.empties[jointName] = o

    def nuke(self):
        objs = bpy.data.objects
        for jointName, parentName in self.sensorJointDict.items():
            objs.remove(objs[jointName], do_unlink = True)
#        objs.remove(objs[ARMATURE_BASE], do_unlink = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                       Location Assignment Methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def assign(self, jointData):
#        if not hasattr(self, 'mult'): self.calibrate(jointData[SENSOR_ROOT]['location'])

        # assign empties based on location
        for sensorName in jointData:
            if jointData[sensorName]['state'] != 'Not Tracked':
                loc = jointData[sensorName]['location']
                self.assignEmpty(sensorName, loc)

        if not self.constraintsApplied:
            self.addConstraints()

    def assignEmpty(self, sensorName, loc):
        empty = self.empties[sensorName]

        empty.location = Vector((loc['x']* self.mult.z, loc['z']* self.mult.z, loc['y']* self.mult.z))

#        if sensorName == SENSOR_ROOT:
#            self.empties[ARMATURE_BASE].location = empty.location.copy()
#            self.empties[ARMATURE_BASE].location.z -= self.rootLength

    def calibrate(self, skeletonLoc):
        self.mult.z = self.spineBaseHeightWorldSpace / skeletonLoc['y']
        print('location multiplier- x: ' + str(self.mult.x) + ', y: ' + str(self.mult.y) + ', z: ' + str(self.mult.z))
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                      Constraints add & removal Methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addConstraints(self):
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.transforms_clear()


        for jointName, parentName in self.sensorJointDict.items():
            if parentName is None: continue

            # bone whose tail is at this joint
            boneName = self.mappingToBones[jointName]
            if boneName is None: continue

            bone = self.armature.pose.bones[boneName]

            # add a COPY_LOCATION of the empty which is the parent
            locConstraint = bone.constraints.new('COPY_LOCATION')
            locConstraint.target = self.empties[parentName]
            locConstraint.name = 'MOCAP_LOC'

            # add a STRETCH_TO
            stretchConstraint = bone.constraints.new('STRETCH_TO')
            stretchConstraint.target = self.empties[jointName]
            stretchConstraint.name = 'MOCAP_STRETCH'

        self.constraintsApplied = True

    # remove any constraints on bones with the name starting with 'MOCAP'.
    # no need to check for hands, no constraint will found in this case
    def nukeConstraints(self):
        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.armature.pose.bones:
            for c in bone.constraints:
                if c.name == 'MOCAP_LOC' or c.name == 'MOCAP_STRETCH':
                    bone.constraints.remove(c)

        self.constraintsApplied = False