import bpy
from ..util import bl28
from pprint import pprint

_SIDEDMATCHES = dict()

# Arm
_SIDEDMATCHES["shoulder.#"] = dict()
_SIDEDMATCHES["shoulder.#"]["head"] = "joint-#-clavicle"
_SIDEDMATCHES["shoulder.#"]["tail"] = "joint-#-scapula"
_SIDEDMATCHES["upper_arm.#"] = dict()
_SIDEDMATCHES["upper_arm.#"]["head"] = "joint-#-shoulder"
_SIDEDMATCHES["upper_arm.#"]["tail"] = "joint-#-elbow"
_SIDEDMATCHES["forearm.#"] = dict()
_SIDEDMATCHES["forearm.#"]["head"] = "joint-#-elbow"
_SIDEDMATCHES["forearm.#"]["tail"] = "joint-#-hand"
_SIDEDMATCHES["hand.#"] = dict()
_SIDEDMATCHES["hand.#"]["head"] = "joint-#-hand"
_SIDEDMATCHES["hand.#"]["tail"] = "joint-#-hand-3"

# Finger 5 (pinky)
_SIDEDMATCHES["palm.04.#"] = dict()
_SIDEDMATCHES["palm.04.#"]["head"] = "joint-#-hand-2"
_SIDEDMATCHES["palm.04.#"]["tail"] = "joint-#-finger-5-1"

_SIDEDMATCHES["f_pinky.01.#"] = dict()
_SIDEDMATCHES["f_pinky.01.#"]["head"] = "joint-#-finger-5-1"
_SIDEDMATCHES["f_pinky.01.#"]["tail"] = "joint-#-finger-5-2"

_SIDEDMATCHES["f_pinky.02.#"] = dict()
_SIDEDMATCHES["f_pinky.02.#"]["head"] = "joint-#-finger-5-2"
_SIDEDMATCHES["f_pinky.02.#"]["tail"] = "joint-#-finger-5-3"

_SIDEDMATCHES["f_pinky.03.#"] = dict()
_SIDEDMATCHES["f_pinky.03.#"]["head"] = "joint-#-finger-5-3"
_SIDEDMATCHES["f_pinky.03.#"]["tail"] = "joint-#-finger-5-4"

_SIDEDMATCHES["f_pinky.04.#"] = dict()
_SIDEDMATCHES["f_pinky.04.#"]["head"] = "joint-#-finger-5-4"
_SIDEDMATCHES["f_pinky.04.#"]["tail"] = "joint-#-finger-5-5"

# Finger 4 (ring)
_SIDEDMATCHES["palm.03.#"] = dict()
_SIDEDMATCHES["palm.03.#"]["head"] = "joint-#-hand-2"
_SIDEDMATCHES["palm.03.#"]["tail"] = "joint-#-finger-4-1"

_SIDEDMATCHES["f_ring.01.#"] = dict()
_SIDEDMATCHES["f_ring.01.#"]["head"] = "joint-#-finger-4-1"
_SIDEDMATCHES["f_ring.01.#"]["tail"] = "joint-#-finger-4-2"

_SIDEDMATCHES["f_ring.02.#"] = dict()
_SIDEDMATCHES["f_ring.02.#"]["head"] = "joint-#-finger-4-2"
_SIDEDMATCHES["f_ring.02.#"]["tail"] = "joint-#-finger-4-3"

_SIDEDMATCHES["f_ring.03.#"] = dict()
_SIDEDMATCHES["f_ring.03.#"]["head"] = "joint-#-finger-4-3"
_SIDEDMATCHES["f_ring.03.#"]["tail"] = "joint-#-finger-4-4"

_SIDEDMATCHES["f_ring.04.#"] = dict()
_SIDEDMATCHES["f_ring.04.#"]["head"] = "joint-#-finger-4-4"
_SIDEDMATCHES["f_ring.04.#"]["tail"] = "joint-#-finger-4-5"

# Finger 3 (middle)
_SIDEDMATCHES["palm.02.#"] = dict()
_SIDEDMATCHES["palm.02.#"]["head"] = "joint-#-hand-3"
_SIDEDMATCHES["palm.02.#"]["tail"] = "joint-#-finger-3-1"

_SIDEDMATCHES["f_middle.01.#"] = dict()
_SIDEDMATCHES["f_middle.01.#"]["head"] = "joint-#-finger-3-1"
_SIDEDMATCHES["f_middle.01.#"]["tail"] = "joint-#-finger-3-2"

_SIDEDMATCHES["f_middle.02.#"] = dict()
_SIDEDMATCHES["f_middle.02.#"]["head"] = "joint-#-finger-3-2"
_SIDEDMATCHES["f_middle.02.#"]["tail"] = "joint-#-finger-3-3"

_SIDEDMATCHES["f_middle.03.#"] = dict()
_SIDEDMATCHES["f_middle.03.#"]["head"] = "joint-#-finger-3-3"
_SIDEDMATCHES["f_middle.03.#"]["tail"] = "joint-#-finger-3-4"

_SIDEDMATCHES["f_middle.04.#"] = dict()
_SIDEDMATCHES["f_middle.04.#"]["head"] = "joint-#-finger-3-4"
_SIDEDMATCHES["f_middle.04.#"]["tail"] = "joint-#-finger-3-5"

# Finger 2 (index)
_SIDEDMATCHES["palm.01.#"] = dict()
_SIDEDMATCHES["palm.01.#"]["head"] = "joint-#-hand-3"
_SIDEDMATCHES["palm.01.#"]["tail"] = "joint-#-finger-2-1"

_SIDEDMATCHES["f_index.01.#"] = dict()
_SIDEDMATCHES["f_index.01.#"]["head"] = "joint-#-finger-2-1"
_SIDEDMATCHES["f_index.01.#"]["tail"] = "joint-#-finger-2-2"

_SIDEDMATCHES["f_index.02.#"] = dict()
_SIDEDMATCHES["f_index.02.#"]["head"] = "joint-#-finger-2-2"
_SIDEDMATCHES["f_index.02.#"]["tail"] = "joint-#-finger-2-3"

_SIDEDMATCHES["f_index.03.#"] = dict()
_SIDEDMATCHES["f_index.03.#"]["head"] = "joint-#-finger-2-3"
_SIDEDMATCHES["f_index.03.#"]["tail"] = "joint-#-finger-2-4"

_SIDEDMATCHES["f_index.04.#"] = dict()
_SIDEDMATCHES["f_index.04.#"]["head"] = "joint-#-finger-2-4"
_SIDEDMATCHES["f_index.04.#"]["tail"] = "joint-#-finger-2-5"

# Finger 1 (thumb)
_SIDEDMATCHES["thumb.01.#"] = dict()
_SIDEDMATCHES["thumb.01.#"]["head"] = "joint-#-finger-1-1"
_SIDEDMATCHES["thumb.01.#"]["tail"] = "joint-#-finger-1-2"

_SIDEDMATCHES["thumb.02.#"] = dict()
_SIDEDMATCHES["thumb.02.#"]["head"] = "joint-#-finger-1-2"
_SIDEDMATCHES["thumb.02.#"]["tail"] = "joint-#-finger-1-3"

_SIDEDMATCHES["thumb.03.#"] = dict()
_SIDEDMATCHES["thumb.03.#"]["head"] = "joint-#-finger-1-3"
_SIDEDMATCHES["thumb.03.#"]["tail"] = "joint-#-finger-1-4"

_SIDEDMATCHES["thumb.04.#"] = dict()
_SIDEDMATCHES["thumb.04.#"]["head"] = "joint-#-finger-1-4"
_SIDEDMATCHES["thumb.04.#"]["tail"] = "joint-#-finger-1-5"

# Leg

_SIDEDMATCHES["thigh.#"] = dict()
_SIDEDMATCHES["thigh.#"]["head"] = "joint-#-upper-leg"
_SIDEDMATCHES["thigh.#"]["tail"] = "joint-#-knee"

_SIDEDMATCHES["shin.#"] = dict()
_SIDEDMATCHES["shin.#"]["head"] = "joint-#-knee"
_SIDEDMATCHES["shin.#"]["tail"] = "joint-#-ankle"

_SIDEDMATCHES["foot.#"] = dict()
_SIDEDMATCHES["foot.#"]["head"] = "joint-#-ankle"
_SIDEDMATCHES["foot.#"]["tail"] = "joint-#-foot-1"

_SIDEDMATCHES["toe.#"] = dict()
_SIDEDMATCHES["toe.#"]["head"] = "joint-#-foot-1"
_SIDEDMATCHES["toe.#"]["tail"] = "joint-#-foot-2"

# Eye

_SIDEDMATCHES["eye.#"] = dict()
_SIDEDMATCHES["eye.#"]["head"] = "joint-#-eye"
_SIDEDMATCHES["eye.#"]["tail"] = "joint-#-eye-target"



_BONEMATCHER = dict()

# Spine
_BONEMATCHER["spine"] = dict()
_BONEMATCHER["spine"]["head"] = "joint-pelvis"
_BONEMATCHER["spine"]["tail"] = "joint-spine-4"
_BONEMATCHER["spine.001"] = dict()
_BONEMATCHER["spine.001"]["head"] = "joint-spine-4"
_BONEMATCHER["spine.001"]["tail"] = "joint-spine-3"
_BONEMATCHER["spine.002"] = dict()
_BONEMATCHER["spine.002"]["head"] = "joint-spine-3"
_BONEMATCHER["spine.002"]["tail"] = "joint-spine-2"
_BONEMATCHER["spine.003"] = dict()
_BONEMATCHER["spine.003"]["head"] = "joint-spine-2"
_BONEMATCHER["spine.003"]["tail"] = "joint-spine-1"
_BONEMATCHER["spine.004"] = dict()
_BONEMATCHER["spine.004"]["head"] = "joint-spine-1"
_BONEMATCHER["spine.004"]["tail"] = "joint-neck"
_BONEMATCHER["spine.005"] = dict()
_BONEMATCHER["spine.005"]["head"] = "joint-neck"
_BONEMATCHER["spine.005"]["tail"] = "joint-head"
_BONEMATCHER["spine.006"] = dict()
_BONEMATCHER["spine.006"]["head"] = "joint-head"
_BONEMATCHER["spine.006"]["tail"] = "joint-head-2"

# Face meta bone - same place but half the height of spine.006
_BONEMATCHER["face"] = dict()
_BONEMATCHER["face"]["head"] = "joint-head"
_BONEMATCHER["face"]["tail"] = "joint-head | joint-head-2"

# Heel rollers
_BONEMATCHER["heel.02.R"] = dict()
_BONEMATCHER["heel.02.R"]["head"] = 15455
_BONEMATCHER["heel.02.R"]["tail"] = 15452
_BONEMATCHER["heel.02.L"] = dict()
_BONEMATCHER["heel.02.L"]["head"] = 16759
_BONEMATCHER["heel.02.L"]["tail"] = 16756

# Pelvis movers
_BONEMATCHER["pelvis.R"] = dict()
_BONEMATCHER["pelvis.R"]["head"] = "joint-pelvis"
_BONEMATCHER["pelvis.R"]["tail"] = 4284
_BONEMATCHER["pelvis.L"] = dict()
_BONEMATCHER["pelvis.L"]["head"] = "joint-pelvis"
_BONEMATCHER["pelvis.L"]["tail"] = 10914

# Breast
_BONEMATCHER["breast.R"] = dict()
_BONEMATCHER["breast.R"]["head"] = 3956
_BONEMATCHER["breast.R"]["tail"] = 1764
_BONEMATCHER["breast.L"] = dict()
_BONEMATCHER["breast.L"]["head"] = 10619
_BONEMATCHER["breast.L"]["tail"] = 8436

for side in ['l', 'r']:
    sideUp = side.upper()    
    for boneNameSided in _SIDEDMATCHES.keys():
        boneName = str(boneNameSided).replace("#", sideUp)
        head = str(_SIDEDMATCHES[boneNameSided]["head"]).replace("#", side)
        tail = str(_SIDEDMATCHES[boneNameSided]["tail"]).replace("#", side)    
        _BONEMATCHER[boneName] = dict()
        _BONEMATCHER[boneName]["head"] = head
        _BONEMATCHER[boneName]["tail"] = tail

class RigifyUtils:
    
    def __init__(self, obj):
        self._vgNameToIndex = dict()
        self._vgIndexToName = dict()   
        self._vertCoords = dict()     
        self._vgVerts = dict();
        self._vgMeans = dict();
        
        self._obj = obj
        self._buildJointGroupRefs()
        if self.hasDetailedHelpers():
            self._buildVertIndexRefs()
        
    def _buildJointGroupRefs(self):            
        for vg in self._obj.vertex_groups:
            if "joint" in vg.name:        
                self._vgNameToIndex[vg.name] = vg.index
                self._vgIndexToName[vg.index] = vg.name

    def _buildVertIndexRefs(self):  
        for vg in self._obj.vertex_groups:
            if "joint" in vg.name:        
                self._vgVerts[vg.index] = []
                self._vgMeans[vg.name] = None
                
        for v in self._obj.data.vertices:
            self._vertCoords[v.index] = v.co
            for vg in v.groups:
                if (vg.group) in self._vgVerts:
                    self._vgVerts[vg.group].append(v.co)

        for idx in self._vgVerts.keys():
            name = self._vgIndexToName[idx]
            x = 0
            y = 0
            z = 0
            for co in self._vgVerts[idx]:
                x = x + co[0]
                y = y + co[1]
                z = z + co[2]
            x = x / len(self._vgVerts[idx])
            y = y / len(self._vgVerts[idx])
            z = z / len(self._vgVerts[idx])    
            self._vgMeans[name] = [x,y,z]
                              
    def hasDetailedHelpers(self):        
        return "joint-r-knee" in self._vgNameToIndex.keys()
    
    def _average(self, arrayOfArrays):
        count = len(arrayOfArrays)
        size = len(arrayOfArrays[0])
        result = []
        for i in range(size):
            result.append(0.0)
        for n in range(count):
            for i in range(size):
                result[i] = result[i] + arrayOfArrays[n][i]
        for i in range(size):
            result[i] = result[i] / count            
        return result
        
            
    def _getPositionFromMatch(self, boneName, part): 
        match = _BONEMATCHER[boneName]
        matchSub = match[part]        
        if str(matchSub).isnumeric():
            position = self._vertCoords[int(matchSub)]
        else:
            if "|" in matchSub:
                (left, right) = str(matchSub).split("|", 2)
                left = str(left).strip()
                right = str(right).strip()
                position = self._average([self._vgMeans[left], self._vgMeans[right]])        
            else:                    
                position = self._vgMeans[matchSub]
        return position
    
    def _createRig(self):
        bpy.ops.object.armature_human_metarig_add()
        bpy.ops.object.location_clear()
        bpy.ops.object.rotation_clear()
        bpy.ops.object.scale_clear()
        self._rig = bpy.context.object
        print("RIG: " + str(self._rig))
        
    def _moveBonePositions(self):
        bpy.ops.object.mode_set(mode='EDIT')
        for bone in self._rig.data.edit_bones:
            if bone.name in _BONEMATCHER:                                    
                headPosition = self._getPositionFromMatch(bone.name, "head")
                tailPosition = self._getPositionFromMatch(bone.name, "tail")
                for i in [0,1,2]:            
                    bone.head[i] = headPosition[i]
                    bone.tail[i] = tailPosition[i]
        bpy.ops.object.mode_set(mode='OBJECT')    
        
    def createMetaRig(self):
        self._createRig()
        self._moveBonePositions()
        pprint(_BONEMATCHER)
        