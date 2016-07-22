import bpy

class RigInfo:
    @staticmethod
    def determineRig(armature):
        # in the case where a test bone (wt dot) is not truely unique, order of tests might be important
        game = GameRigInfo(armature)
        if game.matches(): return game

        default = DefaultRigInfo(armature)
        if default.matches(): return default

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
        self.kneeIKChainLength  = 1
        self.footIKChainLength  = 2
        self.handIKChainLength  = 2
        self.elbowIKChainLength = 1

    # for IK rigging support
    def upperArm(self, isLeft): return 'upperarm_' + ('l' if isLeft else 'r')
    def lowerArm(self, isLeft): return 'lowerarm_' + ('l' if isLeft else 'r')
    def hand    (self, isLeft): return 'hand_'     + ('l' if isLeft else 'r')
    # - - -
    def thigh   (self, isLeft): return 'thigh_'    + ('l' if isLeft else 'r')
    def calf    (self, isLeft): return 'calf_'     + ('l' if isLeft else 'r')
    def foot    (self, isLeft): return 'foot_'     + ('l' if isLeft else 'r')

    def ikSpecialProcessing(self):
        return
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
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
        super().__init__(armature, 'Default Rig', 'metacarpal1.L')

        self.pelvis = 'spine05'
        self.root = 'root'
        self.kneeIKChainLength =  2
        self.footIKChainLength =  4
        self.handIKChainLength =  5
        self.elbowIKChainLength = 3

    # for IK rigging support
    def upperArm(self, isLeft): return 'upperarm02' + self.dot + ('L' if isLeft else 'R')
    def lowerArm(self, isLeft): return 'lowerarm02' + self.dot + ('L' if isLeft else 'R')
    def hand    (self, isLeft): return 'wrist'      + self.dot + ('L' if isLeft else 'R')
    # - - -
    def thigh   (self, isLeft): return 'upperleg02' + self.dot + ('L' if isLeft else 'R')
    def calf    (self, isLeft): return 'lowerleg02' + self.dot + ('L' if isLeft else 'R')
    def foot    (self, isLeft): return 'foot'       + self.dot + ('L' if isLeft else 'R')

    def ikSpecialProcessing(self):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones

        newParent = eBones[self.pelvis]
        eBones['pelvis' + self.dot + 'L'].parent = newParent
        eBones['pelvis' + self.dot + 'R'].parent = newParent

        return
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # for Finger rigging support
    def thumbParent(self, isLeft): return 'finger1-1' + self.dot + ('L' if isLeft else 'R')
    def thumbBones (self, isLeft):
        ret = []
        ret.append('finger1-2' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger1-3' + self.dot + ('L' if isLeft else 'R'))
        return ret

    def indexFingerParent(self, isLeft): return 'metacarpal1' + self.dot + ('L' if isLeft else 'R')
    def indexFingerBones (self, isLeft):
        ret = []
        ret.append('finger2-1' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger2-2' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger2-3' + self.dot + ('L' if isLeft else 'R'))
        return ret

    def middleFingerParent(self, isLeft): return 'metacarpal2' + self.dot + ('L' if isLeft else 'R')
    def middleFingerBones(self , isLeft):
        ret = []
        ret.append('finger3-1' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger3-2' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger3-3' + self.dot + ('L' if isLeft else 'R'))
        return ret

    def ringFingerParent(self, isLeft): return 'metacarpal3' + self.dot + ('L' if isLeft else 'R')
    def ringFingerBones(self , isLeft):
        ret = []
        ret.append('finger4-1' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger4-2' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger4-3' + self.dot + ('L' if isLeft else 'R'))
        return ret

    def pinkyFingerParent(self, isLeft): return 'metacarpal4' + self.dot + ('L' if isLeft else 'R')
    def pinkyFingerBones(self , isLeft):
        ret = []
        ret.append('finger5-1' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger5-2' + self.dot + ('L' if isLeft else 'R'))
        ret.append('finger5-3' + self.dot + ('L' if isLeft else 'R'))
        return ret
