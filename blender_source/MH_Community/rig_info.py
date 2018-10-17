import bpy

class RigInfo:
    @staticmethod
    def determineRig(armature):
        # in the case where a test bone (wt dot) is not truely unique, order of tests might be important
        game = GameRigInfo(armature)
        if game.matches(): return game

        default = DefaultRigInfo(armature)
        if default.matches(): return default

        cmu = CMURigInfo(armature)
        if cmu.matches(): return cmu

        kinect2 = Kinect2RigInfo(armature)
        if kinect2.matches(): return kinect2

        return None
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # pass not only a unique bone name, but one that has a dot.  Collada would change that to a '_'
    def __init__(self, armature, name, uniqueBoneName):
        self.armature = armature
        self.name = name
        self.uniqueBoneName = uniqueBoneName
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def matches(self):
        boneWithoutDot = self.uniqueBoneName.replace(".", "_")
        for bone in self.armature.data.bones:
            # test without dot version first in case skeleton has no dots
            if bone.name == boneWithoutDot:
                self.dot = '_'
                return True

            if bone.name == self.uniqueBoneName:
                self.dot = '.'
                return True

        return False
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasFeetOnGround(self):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        # test if the Z of calf is negative, should be negative when feet NOT on ground
        calfZ = eBones[self.calf(False)].head.z

        bpy.ops.object.mode_set(mode=current_mode)
        return calfZ > 0
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # While MHX2 may set this, do not to rely on MHX.
    def determineExportedUnits(self):
        if len(self.armature.data.exportedUnits) > 0: return self.armature.data.exportedUnits

        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        headTail = eBones[self.head].tail.z
        footTail = eBones[self.foot(False)].tail.z
        bpy.ops.object.mode_set(mode=current_mode)

        totalHeight = headTail - footTail # done this way to be feet on ground independent
        if totalHeight < 5: ret = 'METERS' # decimeter threshold
        elif totalHeight <= 22: ret = 'DECIMETERS' # 21.7 to 23.9 is sort of no man's land of decimeters of tallest & inches of smallest
        else: ret = 'INCHES'

        print ('armature exported units is ' + ret + ', headTail: ' + str(headTail) + ', footTail: ' + str(footTail))

        self.armature.data.exportedUnits = ret
        return ret
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def unitMultplierToExported(self):
        units = self.determineExportedUnits()

        if units == 'METERS': return 0.1
        elif units == 'DECIMETERS': return 1
        else: return 3.93701
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasIKRigs(self):
        return self.hasFingerIK() or self.hasIK()
    def hasFingerIK(self):
        return 'thumb.ik.L' in self.armature.data.bones
    def hasIK(self):
        return 'elbow.ik.L' in self.armature.data.bones
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def hasFingers(self):
        hand = self.hand(False)
        if hand not in self.armature.data.bones:
            return False

        for bone in self.armature.data.bones:
            if bone.parent is not None and bone.parent.name == hand:
                return True

        return False
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isExpressionCapable(self):
        return 'special03' in self.armature.data.bones
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def isPoseCapable(self):
        return self.name == 'Default Rig' and not self.hasIKRigs()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # determine all the meshes which are controlled by skeleton,
    def getMeshesForRig(self, scene):
        meshes = []
        for object in [object for object in scene.objects]:
            if object.type == 'MESH' and len(object.vertex_groups) > 0 and self.armature == object.find_armature():
                meshes.append(object)

        return meshes
#===============================================================================
class GameRigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'Game Rig', 'ball_r')

        self.pelvis = 'pelvis'
        self.root = 'Root'
        self.head = 'head'
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for IK rigging support
    def IKCapable(self): return True
    def clavicle(self, isLeft): return 'clavicle_' + ('l' if isLeft else 'r')
    def upperArm(self, isLeft): return 'upperarm_' + ('l' if isLeft else 'r')
    def lowerArm(self, isLeft): return 'lowerarm_' + ('l' if isLeft else 'r')
    def hand    (self, isLeft): return 'hand_'     + ('l' if isLeft else 'r') # also used for amputation
    # - - -
    def thigh   (self, isLeft): return 'thigh_'    + ('l' if isLeft else 'r')
    def calf    (self, isLeft): return 'calf_'     + ('l' if isLeft else 'r') # also used by super.hasFeetOnGround()
    def foot    (self, isLeft): return 'foot_'     + ('l' if isLeft else 'r') # also used for super.determineExportedUnits()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return self.pinkyFingerParent(False) in self.armature.data.bones
    def thumbParent(self, isLeft): return 'thumb_01_' + ('l' if isLeft else 'r')
    def thumbBones (self, isLeft):
        ret = []
        ret.append('thumb_02_' + ('l' if isLeft else 'r'))
        ret.append('thumb_03_' + ('l' if isLeft else 'r'))
        return ret

    def indexFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def indexFingerBones (self, isLeft):
        ret = []
        ret.append('index_01_' + ('l' if isLeft else 'r'))
        ret.append('index_02_' + ('l' if isLeft else 'r'))
        ret.append('index_03_' + ('l' if isLeft else 'r'))
        return ret

    def middleFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def middleFingerBones(self , isLeft):
        ret = []
        ret.append('middle_01_' + ('l' if isLeft else 'r'))
        ret.append('middle_02_' + ('l' if isLeft else 'r'))
        ret.append('middle_03_' + ('l' if isLeft else 'r'))
        return ret

    def ringFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def ringFingerBones(self , isLeft):
        ret = []
        ret.append('ring_01_' + ('l' if isLeft else 'r'))
        ret.append('ring_02_' + ('l' if isLeft else 'r'))
        ret.append('ring_03_' + ('l' if isLeft else 'r'))
        return ret

    def pinkyFingerParent(self, isLeft): return 'hand_' + ('l' if isLeft else 'r')
    def pinkyFingerBones(self , isLeft):
        ret = []
        ret.append('pinky_01_' + ('l' if isLeft else 'r'))
        ret.append('pinky_02_' + ('l' if isLeft else 'r'))
        ret.append('pinky_03_' + ('l' if isLeft else 'r'))
        return ret
#===============================================================================
class DefaultRigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'Default Rig', 'shoulder01.L')

        self.pelvis = 'spine05'
        self.root = 'root'
        self.head = 'head'
        self.kneeIKChainLength =  2
        self.footIKChainLength =  4
        self.handIKChainLength =  5
        self.elbowIKChainLength = 3
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # cannot be static, since dot is only at instance level
    def boneFor(self, baseName, isLeft):
        return baseName + self.dot + ('L' if isLeft else 'R')

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # specific to DefaultRigInfo
    def hasRestTpose(self):
        current_mode = bpy.context.object.mode
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        # test that both sides have wrist Z greater than the head of spine1 head, & are equal
        minZ = eBones['spine01'].head.z
        left  = round(eBones[self.hand(True )].tail.z, 4)
        right = round(eBones[self.hand(False)].tail.z, 4)

        bpy.ops.object.mode_set(mode=current_mode)
        return left > minZ and left == right

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for IK rigging support, which DefaultRig does not have
    def IKCapable(self): return False
    def hand(self, isLeft): return self.boneFor('wrist', isLeft) # also used for amputation
    def calf(self, isLeft): return self.boneFor('lowerleg01', isLeft) # used by super.hasFeetOnGround()
    def foot(self, isLeft): return self.boneFor('foot', isLeft) # used for super.determineExportedUnits()
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return self.pinkyFingerParent(False) in self.armature.data.bones
    def thumbParent(self, isLeft): return self.boneFor('finger1-1', isLeft)
    def thumbBones (self, isLeft):
        ret = []
        ret.append(self.boneFor('finger1-2', isLeft))
        ret.append(self.boneFor('finger1-3', isLeft))
        return ret

    def indexFingerParent(self, isLeft): return self.boneFor('metacarpal1', isLeft)
    def indexFingerBones (self, isLeft):
        ret = []
        ret.append(self.boneFor('finger2-1', isLeft))
        ret.append(self.boneFor('finger2-2', isLeft))
        ret.append(self.boneFor('finger2-3', isLeft))
        return ret

    def middleFingerParent(self, isLeft): return self.boneFor('metacarpal2', isLeft)
    def middleFingerBones(self , isLeft):
        ret = []
        ret.append(self.boneFor('finger3-1', isLeft))
        ret.append(self.boneFor('finger3-2', isLeft))
        ret.append(self.boneFor('finger3-3', isLeft))
        return ret

    def ringFingerParent(self, isLeft): return self.boneFor('metacarpal3', isLeft)
    def ringFingerBones(self , isLeft):
        ret = []
        ret.append(self.boneFor('finger4-1', isLeft))
        ret.append(self.boneFor('finger4-2', isLeft))
        ret.append(self.boneFor('finger4-3', isLeft))
        return ret

    def pinkyFingerParent(self, isLeft): return self.boneFor('metacarpal4', isLeft)
    def pinkyFingerBones(self , isLeft):
        ret = []
        ret.append(self.boneFor('finger5-1', isLeft))
        ret.append(self.boneFor('finger5-2', isLeft))
        ret.append(self.boneFor('finger5-3', isLeft))
        return ret
#===============================================================================
class CMURigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'CMU Rig', 'LeftUpLeg')

        self.pelvis = 'Hips'
        self.root = 'Hips'
        self.head = 'Head'
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for IK rigging support
    def IKCapable(self): return True
    def clavicle(self, isLeft): return ('Left' if isLeft else 'Right') + 'Shoulder'
    def upperArm(self, isLeft): return ('Left' if isLeft else 'Right') + 'Arm'
    def lowerArm(self, isLeft): return ('Left' if isLeft else 'Right') + 'ForeArm'
    def hand    (self, isLeft): return ('Left' if isLeft else 'Right') + 'Hand'  # also used for amputation
    # - - -
    def thigh   (self, isLeft): return ('Left' if isLeft else 'Right') + 'UpLeg'
    def calf    (self, isLeft): return ('Left' if isLeft else 'Right') + 'Leg' # also used by super.hasFeetOnGround()
    def foot    (self, isLeft): return ('Left' if isLeft else 'Right') + 'Foot' # also used for super.determineExportedUnits()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return False
#===============================================================================
class Kinect2RigInfo (RigInfo):
    def __init__(self, armature):
        super().__init__(armature, 'Kinect2 Rig', 'SpineShoulder')

        self.pelvis = 'SpineMid'
        self.root = 'SpineBase'
        self.head = 'Head'
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def boneFor(baseName, isLeft):
        return baseName + ('Left' if isLeft else 'Right')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
     # for IK rigging support
    def IKCapable(self): return True
    def clavicle(self, isLeft): return Kinect2RigInfo.boneFor('Shoulder', isLeft)
    def upperArm(self, isLeft): return Kinect2RigInfo.boneFor('Elbow'   , isLeft)
    def lowerArm(self, isLeft): return Kinect2RigInfo.boneFor('Wrist'   , isLeft)
    def hand    (self, isLeft): return Kinect2RigInfo.boneFor('Hand'    , isLeft) # also used for amputation
    # - - -
    def thigh   (self, isLeft): return Kinect2RigInfo.boneFor('Knee'    , isLeft)
    def calf    (self, isLeft): return Kinect2RigInfo.boneFor('Ankle'   , isLeft) # also used by super.hasFeetOnGround()
    def foot    (self, isLeft): return Kinect2RigInfo.boneFor('Foot'    , isLeft) # also used for super.determineExportedUnits()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def fingerIKCapable(self): return False
