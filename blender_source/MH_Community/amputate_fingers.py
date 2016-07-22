from .rig_info import *

import bpy
from mathutils import Vector
#===============================================================================
class AmputateFingers(bpy.types.Operator):
    """Remove finger bones, and assign their weights to hand bone"""
    bl_idname = 'mh_community.amputate_fingers'
    bl_label = 'Amputate Fingers'

    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        self.armature = context.object

        self.rigInfo = RigInfo.determineRig(self.armature)
        if self.rigInfo is None:
            self.report({'ERROR'}, 'Rig cannot be identified')
            return {'FINISHED'}

        print("amputating fingers to " + self.rigInfo.name)
        # find all meshes which use this armature
        meshes = self.rigInfo.getMeshesForRig(context.scene)

        self.amputate(meshes, True)
        self.amputate(meshes, False)

        return {'FINISHED'}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @classmethod
    def poll(cls, context):
        ob = context.object
        return ob and ob.type == 'ARMATURE' and RigInfo.determineRig(ob) is not None
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def amputate(self, meshes, isLeft):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = self.armature.data.edit_bones
        sheerBone = eBones[self.rigInfo.hand(isLeft)]

        # while still in edit mode select all child bones
        bpy.ops.armature.select_all(action='DESELECT')
        self.selectChildBones(sheerBone, False)

        # get the names of all the donor bone / vertex groups, before bones deleted
        vGroupNames = []
        for editBone in self.armature.data.edit_bones:
            if editBone.select:
                vGroupNames.append(editBone.name)

        # while still in edit mode delete all selected bones, mesh vertex groups unchanged so can do afterward
        bpy.ops.armature.delete()

        # VertexGroup.add(), called in transferVertexGroup(), will not work in edit mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # assign the verts of the vertex groups of each mesh to the vertex group of the sheer bone
        for mesh in meshes:
            # find idx of sheer bone vertex group, when not found skip mesh
            sheerBoneVGroupIdx = mesh.vertex_groups.find(sheerBone.name)
            if sheerBoneVGroupIdx == -1: continue

            vgroups = mesh.vertex_groups

            for groupName in vGroupNames:
                donorGroupIdx = vgroups.find(groupName)
                if donorGroupIdx != -1:
                    self.transferVertexGroup(mesh, donorGroupIdx, sheerBoneVGroupIdx)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    def transferVertexGroup(self, mesh, donorGroupIdx, sheerBoneVGroupIdx):
        sheerBoneVGroup = mesh.vertex_groups[sheerBoneVGroupIdx]

        for vIndex, vertex in enumerate(mesh.data.vertices):
            for group in vertex.groups:
                if group.group == donorGroupIdx:
                    weight = group.weight
                    sheerBoneVGroup.add([vIndex], weight, 'ADD')
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # RECURSIVE
    def selectChildBones(self, bone, thisBoneToo):
        # recursively call this method for each child
        for child in bone.children:
            self.selectChildBones(child, True)

        # select this bone too, if asked
        if thisBoneToo:
            bone.select = True