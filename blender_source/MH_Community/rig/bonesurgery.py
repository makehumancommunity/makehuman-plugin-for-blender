import bpy

class BoneSurgery:
    @staticmethod
    def amputate(armature, meshes, sheerBoneName):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones
        sheerBone = eBones[sheerBoneName]

        # while still in edit mode select all child bones
        bpy.ops.armature.select_all(action='DESELECT')
        # could have already been done, or no toes exported
        if not BoneSurgery.selectChildBones(sheerBone, False) : return

        # get the names of all the donor bones / vertex groups, before bones deleted
        vGroupNames = []
        for editBone in armature.data.edit_bones:
            if editBone.select:
                vGroupNames.append(editBone.name)

        # while still in edit mode delete all selected bones, mesh vertex groups unchanged so can do afterward
        bpy.ops.armature.delete()

        # transfer the weights of the deleted bone onto the sheer point
        BoneSurgery.transferVertexGroups(meshes, vGroupNames, sheerBoneName)

        # a new vertex group may have needed to be added, changing active object; set back to armature
        # bpy.context.scene.objects.active = armature
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def deleteBone(armature, meshes, boneName, weightToBoneName, transferTail = False):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones

        # could have already been done
        if boneName in eBones:
            bone = eBones[boneName]
        else: return

        if weightToBoneName is not None:
            weightToBone = eBones[weightToBoneName]

            if transferTail:
                weightToBone.tail = bone.tail

        # select bone to go & nuke
        bpy.ops.armature.select_all(action='DESELECT')
        bone.select = True
        bpy.ops.armature.delete()

        # transfer the weights of the deleted bone onto the sheer point
        if weightToBoneName is not None:
            BoneSurgery.transferVertexGroups(meshes, [boneName], weightToBoneName)

        # a new vertex group may have needed to be added, changing active object; set back to armature
        # bpy.context.scene.objects.active = armature
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def transferVertexGroups(meshes, vGroupNames, weightToBoneName):
        # VertexGroup.add(), called in transferVertexGroup(), will not work in edit mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # assign the verts of the vertex groups of each mesh to the vertex group of the sheer bone
        for mesh in meshes:
            # find idx of sheer bone vertex group, when mesh participating
            weightToBoneVGroupIdx = BoneSurgery.isParticipating(mesh, vGroupNames, weightToBoneName)
            if weightToBoneVGroupIdx == -1: continue

            vgroups = mesh.vertex_groups

            for groupName in vGroupNames:
                donorGroupIdx = vgroups.find(groupName)
                if donorGroupIdx != -1:
                    BoneSurgery.transferVertexGroup(mesh, donorGroupIdx, weightToBoneVGroupIdx)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def isParticipating(mesh, vGroupNames, weightToBoneName):
        # if the weightToBone vertex group is already in the mesh, let it go thru as participating
        weightToBoneVGroupIdx = mesh.vertex_groups.find(weightToBoneName)
        if weightToBoneVGroupIdx != -1:
            return weightToBoneVGroupIdx

        # still need to check if there are vertex donor groups, then add group to donate to
        vgroups = mesh.vertex_groups
        particpating = False

        for groupName in vGroupNames:
            donorGroupIdx = vgroups.find(groupName)
            if donorGroupIdx != -1:
                particpating = True

        # when there is no current vertex group to the weight to bone, need to add an additional vertex group
        if particpating:
            print("need to add " + weightToBoneName + " group to " + mesh.name)
            mesh.vertex_groups.new(name = weightToBoneName)

            # need to re-find the new group
            weightToBoneVGroupIdx = mesh.vertex_groups.find(weightToBoneName)
            return weightToBoneVGroupIdx

        else: return -1
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def transferVertexGroup(mesh, donorGroupIdx, weightToBoneVGroupIdx):
        weightToBoneVGroup = mesh.vertex_groups[weightToBoneVGroupIdx]

        for vIndex, vertex in enumerate(mesh.data.vertices):
            for group in vertex.groups:
                if group.group == donorGroupIdx:
                    weight = group.weight
                    weightToBoneVGroup.add([vIndex], weight, 'ADD')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # RECURSIVE
    @staticmethod
    def selectChildBones(bone, thisBoneToo):
        ret = thisBoneToo

        # recursively call this method for each child
        for child in bone.children:
            BoneSurgery.selectChildBones(child, True)
            ret = True

        # select this bone too, if asked
        if thisBoneToo:
            bone.select = True

        return ret
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    @staticmethod
    def connectSkeleton(armature, connect = True, exceptions = []):
        bpy.ops.object.mode_set(mode='EDIT')
        eBones = armature.data.edit_bones

        for bone in eBones:
            if bone.parent is not None and bone.name not in exceptions:
                bone.use_connect = connect