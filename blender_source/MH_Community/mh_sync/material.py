#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
import pprint

from ..util import *

pp = pprint.PrettyPrinter(indent=4)

def _createMHImageTextureNode(nodes, imagePathAbsolute):
    fn = os.path.basename(imagePathAbsolute)
    #print(bpy.data.images)
    if fn in bpy.data.images:
        print("image existed")
        image = bpy.data.images[fn]
    else:
        image = bpy.data.images.load(imagePathAbsolute)
    #print(image)

    texnode = nodes.new("ShaderNodeTexImage")
    texnode.image = image
    return texnode

def createMHMaterial(name, materialSettingsHash, ifExists="CREATENEW", eeveeOpaque=False):

    #pp.pprint(materialSettingsHash)
    x = 0
    y = 400

    fixrough = bpy.context.scene.MhFixRoughness

    mat = None
    if ifExists == "OVERWRITE" or ifExists == "REUSE":
        mat = bpy.data.materials.get(name)
        if not mat is None and ifExists == "REUSE":
            print("Resuing existing material " + name)
            return mat
        else:
            if not mat is None:
                print("Overwriting existing material " + name)

    if mat is None:
        print("Creating new material " + name)
        mat = bpy.data.materials.new(name)

    if bl28() and not eeveeOpaque:
        mat.blend_method = 'BLEND'

    mat.use_nodes = True
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    while nodes:
        nodes.remove(nodes[0])

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (x+400, y+10)

    principled = nodes.new("ShaderNodeBsdfPrincipled")
    roughness = 1.0 - materialSettingsHash["shininess"]
    if fixrough and roughness < 0.1 and not "eye" in name.lower():
        roughness = 0.5
    principled.inputs['Roughness'].default_value = roughness

    #print(principled)
    #for i in principled.inputs:
    #    print(i)

    diffuse = materialSettingsHash["diffuseTexture"]
    if not diffuse is None and diffuse != "":
        diffuseTexture = _createMHImageTextureNode(nodes, diffuse)
        diffuseTexture.location = (x-500, y+100)

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

