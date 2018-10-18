#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

def createMHMaterial(name, materialSettingsHash, ifExists="create new"):
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
    output.location = (400, 10)

    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.location = (100, 10)
    #print(principled)
    #for i in principled.inputs:
    #    print(i)
    principled.inputs['Roughness'].default_value = 1.0 - materialSettingsHash["shininess"]

    links.new(output.inputs['Surface'], principled.outputs['BSDF'])

    return mat

