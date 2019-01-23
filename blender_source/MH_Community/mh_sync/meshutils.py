#!/usr/bin/python

import numpy as np

def convertBufferToShapedNumpyArray(data, typeCode, shape, scaleFactor = None):
    numpyRawMesh = np.frombuffer(data, np.dtype(typeCode))
    if scaleFactor is None:
        numpyScaledMesh = numpyRawMesh
    else:
        numpyScaledMesh = np.multiply(numpyRawMesh, scaleFactor)
    numpyMesh = numpyScaledMesh.reshape(shape)
    return numpyMesh

def addNumpyArrayAsVerts(bm, numpyMesh, vertCache = None, vertPosCache = None):
    iMax = len(numpyMesh)
    i = 0
    while i < iMax:
        # Coordinate order from MH is XZY
        x = numpyMesh[i][0]
        z = numpyMesh[i][1]
        y = numpyMesh[i][2]

        vert = bm.verts.new((x, -y, z))
        vert.index = i

        if not vertCache is None:
            vertCache.append(vert)

        if not vertPosCache is None:
            vertPosCache[i][0] = x
            vertPosCache[i][1] = y
            vertPosCache[i][2] = z

        i = i + 1

def addNumpyArrayAsFaces(bm, numpyMesh, vertCache, faceCache=None, smooth = True):
    iMax = len(numpyMesh)

    i = 0
    while i < iMax:

        verts = [None, None, None, None]
        vertIdxs = numpyMesh[i]

        stride = 0
        while stride < 4:
            vertIdx = numpyMesh[i][stride]
            vert = vertCache[vertIdx]
            verts[stride] = vert
            stride = stride + 1

        face = bm.faces.new(verts)
        face.index = i
        face.smooth = smooth
        if not faceCache is None:
            faceCache.append(face)
        i = i + 1
