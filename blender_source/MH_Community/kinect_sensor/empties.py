from .to_kinect2 import *
from .calibrate_armature import *
from .capture_armature import *

import bpy
#===============================================================================
class Empties:
    # scaling is just for diagnostic purposes; kinect data is in meters; this allows capture skeleton to display better
    def __init__(self, armature, scaling = 1):
        self.armature = armature # member for nukeConstraints() & root bone rotation
        self.scaling = scaling
        self.constraintsApplied = False

        # record the bone lengths of the armture for scaling the location assignments
        self.rootLength = armature.pose.bones[ROOT_BONE].length

        # Add all the empties in OBJECT Mode, one for each bone
        # use the Bone list, not bones though, since user could have removed fingers
        bpy.ops.object.mode_set(mode='OBJECT')
        self.empties = {}
        for name in KINECT_BONES:
            o = bpy.data.objects.new( name, None )
            o.empty_draw_size = 0.2 if name == SHOULDER_LEFT or name == SHOULDER_RIGHT else 0.1
            o.empty_draw_type = 'ARROWS'
            o.show_name = True
            o.name = name

            bpy.context.scene.objects.link(o) # needed to make visible, not really required outside of dev
            self.empties[name] = o

    def nuke(self):
        objs = bpy.data.objects
        for name in KINECT_BONES:
            objs.remove(objs[name], True)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                       Location Assignment Methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def assign(self, bonesAnim):
        # assign empties based on location
        for boneName in bonesAnim:
            if bonesAnim[boneName]['state'] != 'Not Tracked':
                loc = bonesAnim[boneName]['location']
                self.assignEmpty(boneName, loc)

        # assign rotation to captured armature's rootbone from locations
        #if bonesAnim[ROOT_BONE]['state'] != 'Not Tracked':
        #    self.armature.pose.bones[ROOT_BONE].rotation_quaternion =  self.determineRootBoneRotation(bonesAnim)
        #self.determineRootBoneRotation(bonesAnim)
        
        if not self.constraintsApplied:
            self.addConstraints()

    def assignEmpty(self, boneName, loc):
        empty = bpy.data.objects[boneName]

        empty.location = Vector((loc['x']* self.scaling, loc['z']* self.scaling, loc['y']* self.scaling))
        
#        if boneName == ROOT_BONE:
#            empty.location.y -= self.rootLength
#            empty.location.z = 0 # when root bone on ground
            
    def determineRootBoneRotation(self, bonesAnim):        
        # direction based on https://social.msdn.microsoft.com/Forums/en-US/8f405acb-7758-4f5c-a297-24bdce27d042/understanding-subject-orientation?forum=kinectv2sdk
        sLeft  = bonesAnim[SHOULDER_LEFT ]['location']
        sRight = bonesAnim[SHOULDER_RIGHT]['location']
        sideToSide = Vector((sLeft['x'] - sRight['x'], sLeft['z'] - sRight['z'], sLeft['y'] - sRight['y'])).normalized()
        print('sideToSide          x:  ' + ('%.2f' % sideToSide.x) + ', y: ' + ('%.2f' % sideToSide.y) + ', z: ' + str('%.2f' % sideToSide.z))
        
        root = bonesAnim[SPINE_BASE]['location']
        head = bonesAnim[HEAD      ]['location']
        up = Vector((head['x'] - root['x'], head['z'] - root['z'], head['y'] - root['y'])).normalized()
        print('up           ' + str(up.x) + ',' + str(up.y) + ',' + str(up.z))
        print('up                  x:  ' + ('%.2f' % up.x) + ', y: ' + ('%.2f' % up.y) + ', z: ' + str('%.2f' % up.z))
        
        direction = sideToSide.cross(up)
        
        # from a direction to a rotation use https://gamedev.stackexchange.com/questions/118960/convert-a-direction-vector-normalized-to-rotation
        angle = atan2(direction.y, direction.x)
        rotXY = Quaternion((0.0, 0.0, 1.0), angle) #.to_matrix()
        euler = rotXY.to_euler()
        print(str(euler.x * 57.2958) + ', ' + str(euler.y * 57.2958) + ', ' + str(euler.z * 57.2958)) # 57.2958 is to degrees
        
 #       angleZ = asin(direction.z)
 #       rotZ = Quaternion((0.0, 1.0, 0.0), angleZ).to_matrix()

 #       ret = (rotXY * rotZ).to_quaternion()
 #       euler = ret.to_euler()
 #       print(str(euler.x * 57.2958) + ', ' + str(euler.y * 57.2958) + ', ' + str(euler.z * 57.2958))

        return rotXY

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                      Constraints add & removal Methods
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addConstraints(self):
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.transforms_clear()

        for bone in self.armature.pose.bones:
            # always add a COPY_LOCATION of the empty
            locConstraint = bone.constraints.new('COPY_LOCATION')
            locConstraint.target = self.empties['SpineBase' if bone.parent is None else bone.parent.name]
            locConstraint.name = 'KINECT_LOC'

            # only add a STRETCH_TO when not the root bone
            if bone.parent is not None:
                stretchConstraint = bone.constraints.new('STRETCH_TO')
                stretchConstraint.target = self.empties[bone.name]
                stretchConstraint.name = 'KINECT_STRETCH'

        self.constraintsApplied = True

    # remove any constraints on bones with the name 'KINECT'.
    # no need to check for hands, no constraint will found in this case
    def nukeConstraints(self):
        bpy.ops.object.mode_set(mode='POSE')
        for bone in self.armature.pose.bones:
            for c in bone.constraints:
                if c.name == 'KINECT_LOC' or c.name == 'KINECT_STRETCH':
                    bone.constraints.remove(c)

        self.constraintsApplied = False