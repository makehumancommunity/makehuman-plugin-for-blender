
import bpy
from . import DefaultRigInfo
from ..util import bl28


# ===============================================================================
class IkRig():
    def __init__(self, rigInfo):
        self.rigInfo = rigInfo
        self.armature = self.rigInfo.armature

    # ===============================================================================
    def add(self):
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()

        if bl28():
            self.armature.data.display_type = 'BBONE'
        else:
            self.armature.data.draw_type = 'BBONE'

        # make all regular bone slightly smaller, so IK's fit around
        unitMult = self.rigInfo.unitMultplierToExported()
        val = 0.6 * unitMult
        bpy.ops.transform.transform(mode='BONE_SIZE', value=(val, val, val, 0))
        bpy.ops.pose.select_all(action='DESELECT')

        self.changeLocks(False)

        self.addElbowAndHandIK(True)
        self.addElbowAndHandIK(False)

        self.addKneeAndFootIK(True)
        self.addKneeAndFootIK(False)
        bpy.ops.transform.transform(mode='BONE_SIZE', value=(unitMult, unitMult, unitMult, 0))

        if isinstance(self.rigInfo, DefaultRigInfo):
            pBones = self.armature.pose.bones
            locks = self.rigInfo.additionalLocks()

            for key in locks:
                lock = locks[key]
                bone = pBones[key]
                bone.lock_ik_x = lock["lockX"]
                bone.lock_ik_y = lock["lockY"]
                bone.lock_ik_z = lock["lockZ"]

                RADIAN = 3.14 / 180.0

                if not lock["limitXMin"] is None or not lock["limitXMax"] is None:
                    bone.use_ik_limit_x = True
                    if not lock["limitXMin"] is None:
                        bone.ik_min_x = lock["limitXMin"] * RADIAN
                    if not lock["limitXMax"] is None:
                        bone.ik_max_x = lock["limitXMax"] * RADIAN
                if not lock["limitYMin"] is None or not lock["limitYMax"] is None:
                    bone.use_ik_limit_y = True
                    if not lock["limitYMin"] is None:
                        bone.ik_min_y = lock["limitYMin"] * RADIAN
                    if not lock["limitYMax"] is None:
                        bone.ik_max_y = lock["limitYMax"] * RADIAN
                if not lock["limitZMin"] is None or not lock["limitZMax"] is None:
                    bone.use_ik_limit_z = True
                    if not lock["limitZMin"] is None:
                        bone.ik_min_z = lock["limitZMin"] * RADIAN
                    if not lock["limitZMax"] is None:
                        bone.ik_max_z = lock["limitZMax"] * RADIAN

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addElbowAndHandIK(self, isLeft):
        side = 'L' if isLeft else 'R'

        # add bones while in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        upperArmName = self.rigInfo.upperArm(isLeft)
        upperArm = eBones[upperArmName]

        lowerArmName = self.rigInfo.lowerArm(isLeft)

        handName = self.rigInfo.hand(isLeft)
        hand = eBones[handName]
        hand.hide = True
        # - - - - - - - -
        elbowHead = upperArm.tail.copy()
        elbowHead.y = abs(elbowHead.y) * -4  # always forward, negative
        elbowTail = elbowHead.copy()
        elbowTail.y = elbowTail.y * 2

        elbowIKName = 'elbow.ik.' + side
        elbowIK = eBones.new(elbowIKName)
        elbowIK.head = elbowHead
        elbowIK.tail = elbowTail
        #elbowIK.parent = eBones[self.rigInfo.root]
        elbowIK.use_deform = False
        elbowIK.select = True
        # - - - - - - - -
        handIKName = 'hand.ik.' + side
        handIK = eBones.new(handIKName)
        handIK.head = hand.head.copy()
        handIK.tail = hand.tail.copy()
        handIK.roll = hand.roll
        #handIK.parent = eBones[self.rigInfo.root]
        handIK.use_deform = False
        handIK.select = True
        # - - - - - - - -
        self.addIK_Constraint(upperArmName, elbowIKName, self.rigInfo.elbowIKChainLength)
        self.addIK_Constraint(lowerArmName, handIKName, self.rigInfo.handIKChainLength)
        self.addCopyRotation(handName, handIKName)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addKneeAndFootIK(self, isLeft):
        side = 'L' if isLeft else 'R'

        # add bones while in edit mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        thighName = self.rigInfo.thigh(isLeft)
        thigh = eBones[thighName]

        calfName = self.rigInfo.calf(isLeft)

        footName = self.rigInfo.foot(isLeft)
        foot = eBones[footName]
        foot.hide = True

        kneeHead = thigh.tail.copy()
        kneeHead.y = abs(kneeHead.y) * -10  # always forward, negative
        kneeTail = kneeHead.copy()
        kneeTail.y = kneeHead.y * 1.5

        kneeIKName = 'knee.ik.' + side
        kneeIK = eBones.new(kneeIKName)
        kneeIK.head = kneeHead
        kneeIK.tail = kneeTail
        #kneeIK.parent = eBones[self.rigInfo.root]
        kneeIK.use_deform = False
        kneeIK.select = True
        # - - - - - - - -
        footIKName = 'foot.ik.' + side
        footIK = eBones.new(footIKName)
        footIK.head = foot.head.copy()
        footIK.tail = foot.tail.copy()
        footIK.roll = foot.roll
        #footIK.parent = eBones[self.rigInfo.root]
        footIK.use_deform = False
        footIK.select = True
        # - - - - - - - -
        self.addIK_Constraint(thighName, kneeIKName, self.rigInfo.kneeIKChainLength)
        self.addIK_Constraint(calfName, footIKName, self.rigInfo.footIKChainLength)
        self.addCopyRotation(footName, footIKName)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addCopyRotation(self, boneName, subtargetName):
        print('adding copy rotation constraint to ' + boneName + ', with sub target ' + subtargetName)
        # apply constraints to the pose bone version
        bpy.ops.object.mode_set(mode='POSE')
        pBones = self.armature.pose.bones

        pBone = pBones[boneName]
        con = pBone.constraints.new('COPY_ROTATION')
        con.target = self.armature
        con.subtarget = subtargetName

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def addIK_Constraint(self, boneName, ikBoneName, chain_count):
        print('adding IK constraint to ' + boneName + ', with sub target ' + ikBoneName + ', and chain length ' + str(chain_count))
        # apply constraints to the pose bone version
        bpy.ops.object.mode_set(mode='POSE')
        pBones = self.armature.pose.bones

        pBone = pBones[boneName]
        con = pBone.constraints.new('IK')
        con.target = self.armature
        con.subtarget = ikBoneName
        con.chain_count = chain_count

    # ===============================================================================
    def changeLocks(self, locked):
        # take location locks off pelvis & clavicles
        pelvis = self.armature.pose.bones[self.rigInfo.pelvis]
        pelvis.lock_location[0] = locked
        pelvis.lock_location[1] = locked
        pelvis.lock_location[2] = locked

        lClavicle = self.armature.pose.bones[self.rigInfo.clavicle(True)]
        lClavicle.lock_location[0] = locked
        lClavicle.lock_location[1] = locked
        lClavicle.lock_location[2] = locked

        rClavicle = self.armature.pose.bones[self.rigInfo.clavicle(False)]
        rClavicle.lock_location[0] = locked
        rClavicle.lock_location[1] = locked
        rClavicle.lock_location[2] = locked

    # ===============================================================================
    def remove(self):
        self.changeLocks(True)
        self.removeSide(True)
        self.removeSide(False)
        # reverse making all regular bone slightly smaller, so IK's fit around
        unitMult = self.rigInfo.unitMultplierToExported()
        val = unitMult / 0.6
        bpy.ops.transform.transform(mode='BONE_SIZE', value=(val, val, val, 0))

        self.armature.data.draw_type = 'STICK'

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def removeSide(self, isLeft):
        side = 'L' if isLeft else 'R'
        self.demolish('elbow.ik.' + side, [self.rigInfo.upperArm(isLeft)])
        self.demolish('hand.ik.' + side, [self.rigInfo.lowerArm(isLeft), self.rigInfo.hand(isLeft)])
        self.demolish('knee.ik.' + side, [self.rigInfo.thigh(isLeft)])
        self.demolish('foot.ik.' + side, [self.rigInfo.calf(isLeft), self.rigInfo.foot(isLeft)])

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # no need of BoneSurgery module, since no weights to give back
    def demolish(self, controlBoneName, boneNames):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='DESELECT')
        self.armature.data.edit_bones[controlBoneName].select = True
        bpy.ops.armature.delete()

        bpy.ops.object.mode_set(mode='POSE')
        for bIndex, boneName in enumerate(boneNames):
            self.armature.data.bones[boneName].select = True
            self.armature.data.bones[boneName].hide = False

        for bone in bpy.context.selected_pose_bones:
            # Create a list of all the copy location constraints on this bone
            copyRotConstraints = [c for c in bone.constraints if c.type == 'COPY_ROTATION' or c.type == 'IK']

            # Iterate over all the bone's copy location constraints and delete them all
            for c in copyRotConstraints:
                bone.constraints.remove(c)  # Remove constraint
