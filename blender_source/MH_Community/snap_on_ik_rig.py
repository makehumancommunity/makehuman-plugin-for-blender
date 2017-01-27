from .rig_info import *

import bpy
from mathutils import Vector
#===============================================================================
class SnapOnIKKRig(bpy.types.Operator):
    """Add bones which convert this to an IK Rig"""
    bl_idname = 'mh_community.ik_rig'
    bl_label = 'Add IK Rig'

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.armature = context.object

        self.rigInfo = RigInfo.determineRig(self.armature)
        if self.rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        print("adding IK to " + self.rigInfo.name)

        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()

        self.armature.data.draw_type = 'BBONE'
        # make all regular bone slightly smaller, so IK's fit around
        bpy.ops.transform.transform(mode='BONE_SIZE', value=(0.6, 0.6, 0.6, 0))

        # perform anything special for this rig first
        self.rigInfo.ikSpecialProcessing()

        # take location locks off pelvis
        pelvis = self.armature.pose.bones[self.rigInfo.pelvis]
        pelvis.lock_location[0] = False
        pelvis.lock_location[1] = False
        pelvis.lock_location[2] = False
        
        lClavicle = self.armature.pose.bones[self.rigInfo.clavicle(True)]
        lClavicle.lock_location[0] = False
        lClavicle.lock_location[1] = False
        lClavicle.lock_location[2] = False
        
        rClavicle = self.armature.pose.bones[self.rigInfo.clavicle(False)]
        rClavicle.lock_location[0] = False
        rClavicle.lock_location[1] = False
        rClavicle.lock_location[2] = False

        self.addElbowAndHandIK(True)
        self.addElbowAndHandIK(False)

        self.addKneeAndFootIK(True)
        self.addKneeAndFootIK(False)

        # tell BabylonJS exporter not to export IK bones
        if hasattr(context.scene, "ignoreIKBones"):
            context.scene.ignoreIKBones = True

        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'ARMATURE' and RigInfo.determineRig(ob) is not None
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addElbowAndHandIK(self, isLeft):
        side = 'L' if isLeft else 'R'

        # add bones while in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        upperArm = eBones[self.rigInfo.upperArm(isLeft)]
        lowerArm = eBones[self.rigInfo.lowerArm(isLeft)]
        hand     = eBones[self.rigInfo.hand    (isLeft)]
        # - - - - - - - -
        elbowHead = upperArm.tail.copy()
        elbowHead.y = elbowHead.y * -4
        elbowTail = elbowHead.copy()
        elbowTail.y = elbowTail.y * 2

        elbowIKName = 'elbow.ik.' + side
        elbowIK = eBones.new(elbowIKName)
        elbowIK.head = elbowHead
        elbowIK.tail = elbowTail
        elbowIK.parent = eBones[self.rigInfo.root]
        elbowIK.use_deform = False
        # - - - - - - - -
        handIKName = 'hand.ik.' + side
        handIK = eBones.new(handIKName)
        handIK.head = hand.head.copy()
        handIK.tail = hand.tail.copy()
        handIK.roll = hand.roll
        handIK.parent = eBones[self.rigInfo.root]
        elbowIK.use_deform = False
        # - - - - - - - -
        self.addIK_Constraint(upperArm.name, elbowIKName, self.rigInfo.elbowIKChainLength)
        self.addIK_Constraint(lowerArm.name, handIKName , self.rigInfo.handIKChainLength )
        self.addCopyRotation(hand.name, handIKName)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addKneeAndFootIK(self, isLeft):
        side = 'L' if isLeft else 'R'

        # add bones while in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        thigh = eBones[self.rigInfo.thigh(isLeft)]
        calf  = eBones[self.rigInfo.calf (isLeft)]
        foot  = eBones[self.rigInfo.foot (isLeft)]

        kneeHead = thigh.tail.copy()
        kneeHead.y = kneeHead.y * 10
        kneeTail = kneeHead.copy()
        kneeTail.y = kneeHead.y * 1.5

        kneeIKName = 'knee.ik.' + side
        kneeIK = eBones.new(kneeIKName)
        kneeIK.head = kneeHead
        kneeIK.tail = kneeTail
        kneeIK.parent = eBones[self.rigInfo.root]
        kneeIK.use_deform = False
        # - - - - - - - -
        footIKName = 'foot.ik.' + side
        footIK = eBones.new(footIKName)
        footIK.head = foot.head.copy()
        footIK.tail = foot.tail.copy()
        footIK.roll = foot.roll
        footIK.parent = eBones[self.rigInfo.root]
        footIK.use_deform = False
        # - - - - - - - -
        self.addIK_Constraint(thigh.name, kneeIKName, self.rigInfo.kneeIKChainLength)
        self.addIK_Constraint(calf.name, footIKName , self.rigInfo.footIKChainLength )
        self.addCopyRotation(foot.name, footIKName)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCopyRotation(self, boneName, subtargetName):
        print ('adding copy rotation constraint to ' + boneName + ', with sub target ' + subtargetName)
        # apply constraints to the pose bone version
        bpy.ops.object.mode_set(mode='POSE')
        pBones = self.armature.pose.bones

        pBone = pBones[boneName]
        con = pBone.constraints.new('COPY_ROTATION')
        con.target = self.armature
        con.subtarget = subtargetName

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addIK_Constraint(self, boneName, ikBoneName, chain_count):
        print ('adding IK constraint to ' + boneName + ', with sub target ' + ikBoneName + ', and chain length ' + str(chain_count))
        # apply constraints to the pose bone version
        bpy.ops.object.mode_set(mode='POSE')
        pBones = self.armature.pose.bones

        pBone = pBones[boneName]
        con = pBone.constraints.new('IK')
        con.target = self.armature
        con.subtarget = ikBoneName
        con.chain_count = chain_count