
import bpy

MIN_PCT_CHANGED = 5 
MIN_CHANGED = 50
#===============================================================================
def shapesFromPose(operator, skeleton, shapeName):
    nWarnings = 0
    scene = bpy.context.scene
    meshes = getMeshesForRig(scene, skeleton)
    allBones = getAllBones(skeleton)
    operator.report({'INFO'}, shapeName + ' stats:')

    for mesh in meshes:
        tVerts = len(mesh.data.vertices)

        # delete if key already exists
        deleteShape(mesh, shapeName)

        # get temporary version with modifiers applied
        depsgraph = bpy.context.evaluated_depsgraph_get()
        objectWithModifiers = mesh.evaluated_get(depsgraph)
        tmp = objectWithModifiers.to_mesh()

        # need to make sure the number of vertices, like no 'hide faces modifier'
        if tVerts != len(tmp.vertices):
            operator.report({'WARNING'}, '     ' + mesh.name + ':  Had to be skipped, since current modifiers change the number of vertices')
            nWarnings += 1
            continue

        # add an empty key (create a basis when none)
        key = mesh.shape_key_add(name = shapeName, from_mix = False)
        key.value = 0 # keep un-applied

        # get basis, so can write only verts different than
        basis = mesh.data.shape_keys.key_blocks['Basis']

        # assign the key the vert values of the current pose, when different than Basis
        nDiff = 0
        for v in tmp.vertices:
            # first pass; exclude verts not influenced by the Bones selected
            if not isVertexInfluenced(mesh.vertex_groups, v, allBones) : continue

            value   = v.co
            baseval = basis.data[v.index].co
            if not similar_vertex(value, baseval):
                key.data[v.index].co = value
                nDiff += 1

        if nDiff > 0:
            if 100 * nDiff / tVerts > MIN_PCT_CHANGED or nDiff >= MIN_CHANGED:
                operator.report({'INFO'}, '     ' + mesh.name + ':  ' + str(nDiff) + ' of ' + str(tVerts))
            else:
                operator.report({'WARNING'}, '     ' + mesh.name + ':  was skipped since the # of vertices changed was less then ' + str(MIN_PCT_CHANGED) + '%, and also less then the minimum # of ' + str(MIN_CHANGED) + ' (was ' + str(nDiff) + ' )')
                mesh.shape_key_remove(key)
        else:
            # when no verts different, delete key for this mesh
            mesh.shape_key_remove(key)

        # remove temp mesh
        mesh.to_mesh_clear()

    return nWarnings
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# determine all the meshes which are controlled by skeleton
def getMeshesForRig(scene, skeleton):
    meshes = []
    for object in [object for object in scene.objects]:
        if object.type == 'MESH' and len(object.vertex_groups) > 0 and skeleton == object.find_armature():
            meshes.append(object)
            # ensure that there is a Basis key
            if not object.data.shape_keys:
                object.shape_key_add(name = 'Basis')

    return meshes
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# This also returns hidden bones, critical for finger shape keys
def getAllBones(skeleton):
    vGroupNames = []
    for bone in skeleton.data.bones:
        vGroupNames.append(bone.name)

    return vGroupNames
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def deleteShape(mesh, shapeName):
    if not mesh.data.shape_keys:
        return

    for key_block in mesh.data.shape_keys.key_blocks:
        if key_block.name == shapeName:
            mesh.shape_key_remove(key_block)
            return
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def isVertexInfluenced(mesh_vertex_groups, vertex, allBones):
    for group in vertex.groups:
        for bone in allBones:
            if mesh_vertex_groups[group.group].name == bone:
                return True
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def similar_vertex(vertA, vertB, tolerance = 0.00015):
    if vertA is None or vertB is None: return False
    if (abs(vertA.x - vertB.x) > tolerance or
        abs(vertA.y - vertB.y) > tolerance or
        abs(vertA.z - vertB.z) > tolerance ):
        return False
    return True