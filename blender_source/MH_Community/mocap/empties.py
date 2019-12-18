from .capture_armature import *
from ..rig.riginfo import *

from mathutils import Vector
import bpy
#===============================================================================
ARMATURE_BASE = 'ARMATURE_BASE'
class Empties:
    def __init__(self, capturedRigInfo, sensorMappingToBones, sensorJointDict, firstBody):
        self.capturedRigInfo = capturedRigInfo
        self.capturedArmature = capturedRigInfo.armature
        self.sensorMappingToBones = sensorMappingToBones
        self.sensorJointDict = sensorJointDict
        self.firstBody = firstBody
        for jointName, parentName in self.sensorJointDict.items():
            if parentName is None:
                self.sensorRoot = jointName
                break

        self.constraintsApplied = False

        # grab stuff from rig info for scaling & placement
        self.pelvisInWorldSpace = capturedRigInfo.pelvisInWorldSpace()
        self.rootInWorldSpace   = capturedRigInfo.rootInWorldSpace()

        # Add all the empties in OBJECT Mode, one for each bone
        # use the Bone list, not bones though, since user could have removed fingers
        bpy.ops.object.mode_set(mode='OBJECT')
        self.empties = {}
        for jointName, parentName in self.sensorJointDict.items():
            self.addEmpty(jointName)

        #  add one for the base of the root bone
        self.addEmpty(ARMATURE_BASE)

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
            
        objs.remove(objs[ARMATURE_BASE], do_unlink = True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                       Location Assignment Methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def assign(self, jointData):
        if not hasattr(self, 'mult'): self.calibrate(jointData)

        # assign empties based on location
        for sensorName in jointData:
            if jointData[sensorName]['state'] != 'Not Tracked':
                loc = jointData[sensorName]['location']
                self.assignEmpty(sensorName, loc)

        if not self.constraintsApplied:
            self.addConstraints()

    def assignEmpty(self, sensorName, loc):
        empty = self.empties[sensorName]

        empty.location = Vector((loc['x'], loc['z'], loc['y']))

        if sensorName == self.sensorRoot:
            changeInRootLoc = (empty.location - self.sensorRootBasis) * self.mult
            # add-in current location, so recordings can be done when armature raised or moved when recording
            # This is only placing the empty, which will then converted back from world to local.
            self.empties[ARMATURE_BASE].location = changeInRootLoc + self.rootInWorldSpace

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                            Calibration Methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def calibrate(self, jointData):
        sensorRootLoc = jointData[self.sensorRoot]['location']
        # since using sensor data, switch y with z
        # for non-first bodies origin from sensor is first's; want to keep that
        if self.firstBody:
            self.sensorRootBasis = Vector((sensorRootLoc['x'], sensorRootLoc['z'], sensorRootLoc['y']))
        else:
            self.sensorRootBasis = Vector((                 0,                  0, sensorRootLoc['y']))
        
        self.mult = self.pelvisInWorldSpace.z / sensorRootLoc['y']
        print('sensor to armature multiplier: ' + str(self.mult) + ', armature pelvis height: ' +str(self.pelvisInWorldSpace.z) + ' over sensors: ' + str(sensorRootLoc['y']))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                      Constraints add & removal Methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addConstraints(self):
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.transforms_clear()

        for jointName, parentName in self.sensorJointDict.items():
            if parentName is None: continue

            # bone whose tail is at this joint
            boneName = self.sensorMappingToBones[jointName]
            if boneName is None or boneName not in self.capturedArmature.pose.bones: continue

            bone = self.capturedArmature.pose.bones[boneName]

            # add a COPY_LOCATION of the empty which is the parent
            locConstraint = bone.constraints.new('COPY_LOCATION')
            locConstraint.target = self.empties[parentName]
            locConstraint.name = 'MOCAP_LOC'

            # add a STRETCH_TO
            stretchConstraint = bone.constraints.new('STRETCH_TO')
            stretchConstraint.target = self.empties[jointName]
            stretchConstraint.name = 'MOCAP_STRETCH'
            
        # also add copy location for root bone
        bone = self.capturedArmature.pose.bones[self.capturedRigInfo.root]
        constraint = bone.constraints.new('COPY_LOCATION')
        constraint.target = self.empties[ARMATURE_BASE]
        constraint.name = 'MOCAP_LOC'

        self.constraintsApplied = True

    # remove any constraints on bones with the name starting with 'MOCAP'.
    # no need to check for hands, no constraint will found in this case
    def nukeConstraints(self):
        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.capturedArmature.pose.bones:
            for c in bone.constraints:
                if c.name == 'MOCAP_LOC' or c.name == 'MOCAP_STRETCH':
                    bone.constraints.remove(c)

        self.constraintsApplied = False