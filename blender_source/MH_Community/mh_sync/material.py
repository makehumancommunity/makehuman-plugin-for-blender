#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os

def _createMHImageTextureNode(nodes, imagePathAbsolute):
    fn = os.path.basename(imagePathAbsolute)
    print(bpy.data.images)
    if fn in bpy.data.images:
        print("image existed")
        image = bpy.data.images[fn]
    else:
        image = bpy.data.images.load(imagePathAbsolute)
    print(image)

    texnode = nodes.new("ShaderNodeTexImage")
    texnode.image = image
    return texnode

def createMHMaterial(name, materialSettingsHash, ifExists="create new"):

    x = 0
    y = 400

    mat = None
    if ifExists == "update existing" or ifExists == "use existing":
        mat = bpy.data.materials.get(name)
        if not mat is None and ifExists == "use existing":
            return mat

    if mat is None:
        mat = bpy.data.materials.new(name)

    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    while nodes:
        nodes.remove(nodes[0])

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (x+400, y+10)

    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.inputs['Roughness'].default_value = 1.0 - materialSettingsHash["shininess"]

    print(principled)
    for i in principled.inputs:
        print(i)

    diffuse = materialSettingsHash["diffuseTexture"]
    if not diffuse is None and diffuse != "":
        diffuseTexture = _createMHImageTextureNode(nodes, diffuse)
        diffuseTexture.location = (x-500, y+100)
        print(diffuseTexture)
        diffuseAlphaMix = nodes.new("ShaderNodeMixShader")
        diffuseAlphaMix.location = (x+100, y+50)
        principled.location = (x-200, y-50)
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        transparent.location = (x-200, y+100)

        links.new(output.inputs['Surface'], diffuseAlphaMix.outputs['Shader'])
        links.new(diffuseAlphaMix.inputs[2], principled.outputs['BSDF'])
        links.new(diffuseAlphaMix.inputs[0], diffuseTexture.outputs['Alpha'])
        links.new(principled.inputs['Base Color'], diffuseTexture.outputs['Color'])
        links.new(diffuseAlphaMix.inputs[1], transparent.outputs['BSDF'])
    else:
        principled.location = (x+100, y+10)
        links.new(output.inputs['Surface'], principled.outputs['BSDF'])

    return mat

