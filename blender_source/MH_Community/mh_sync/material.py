#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
import json

from ..util import *
import pprint

def _createMHImageTextureNode(nodes, imagePathAbsolute, color_space='sRGB'):
    fn = os.path.basename(imagePathAbsolute)
    if fn in bpy.data.images:
        print("image existed: " + imagePathAbsolute)
        image = bpy.data.images[fn]
    else:
        image = bpy.data.images.load(imagePathAbsolute)

    texnode = nodes.new("ShaderNodeTexImage")
    if bl28():
        image.colorspace_settings.name = color_space
    else:
        if color_space == 'Non-Color':
            texnode.color_space = 'NONE'
    texnode.image = image
    return texnode

def _updatePrincipled(materialDefinition, materialSettingsHash, baseColor=(0.8, 0.8, 0.8, 1.0)):

    name = materialSettingsHash["name"]
    fixrough = bpy.context.scene.MhFixRoughness

    principled = materialDefinition["nodes"]["principled"]

    roughness = 1.0 - materialSettingsHash["shininess"]
    if fixrough and roughness < 0.1 and not "eye" in name.lower():
        roughness = 0.5

    principled["values"]["Roughness"] = roughness

    if 'diffuseColor' in materialSettingsHash:
        col = materialSettingsHash.get('diffuseColor')
        while len(col) < 4:
            col.append(1.0)
        principled["values"]["Base Color"] = col

def _updateDiffuseTexture(materialDefinition, materialSettingsHash):

    diffuse = materialSettingsHash.get("diffuseTexture")
    if diffuse:
        diffuseDef = materialDefinition["nodes"]["diffuseTexture"]
        diffuseDef["imageData"]["path"] = diffuse
        diffuseDef["create"] = True

def _updateNormalMapAndBumpmapTexture(materialDefinition, materialSettingsHash):
    # TODO: Modify intensity ("Strength") for normal map and bump map
    nmap = materialSettingsHash.get("normalMapTexture")
    if nmap:
        nmapDef = materialDefinition["nodes"]["normalMapTexture"]
        nmapDef["imageData"]["path"] = nmap
        nmapDef["create"] = True

    bmap = materialSettingsHash.get("bumpMapTexture")
    if bmap:
        bmapDef = materialDefinition["nodes"]["bumpMapTexture"]
        bmapDef["imageData"]["path"] = bmap
        bmapDef["create"] = True
        materialDefinition["nodes"]["bumpMap"]["create"] = True

    if nmap or bmap:
        if nmap and bmap:
            materialDefinition["nodes"]["bumpAndNormal"]["create"] = True
        else:
            materialDefinition["nodes"]["bumpOrNormal"]["create"] = True

def createMakeSkinMaterial(name, materialSettingsHash, obj, ifExists="CREATENEW", importBlendMat=False, onlyBlendMat=False):

    # TODO: Support overwriting existing material
    # TODO: This will cause problem with blendMat attachments in second import
    mat = bpy.data.materials.get(name)
    if not mat is None and ifExists == "REUSE":
        print("Resuing existing material " + name)
        return mat
    scn = bpy.context.scene

    from makeskin import MHMat, blendMatLoad
    mhmat = MHMat(fileName=materialSettingsHash["materialFile"])
    mat = None
    if importBlendMat and "blendMaterial" in mhmat.settings and mhmat.settings["blendMaterial"]:
        if not onlyBlendMat:
            mat = mhmat.assignAsNodesMaterialForObj(scn, obj, True)
            mat.name = name
        path = mhmat.settings["blendMaterial"]
        if not mat:
            mat = blendMatLoad(path, obj)
            mat.name = name
        else:
            mat2 = blendMatLoad(path, obj)
            mat2.name = name + ".blendMat"
    else:
        mat = mhmat.assignAsNodesMaterialForObj(scn, obj, True)
        mat.name = name
    return mat


def createMHMaterial2(name, materialSettingsHash, baseColor=(0.8, 0.8, 0.8, 1.0), ifExists="CREATENEW", materialFile="defaultMaterial.json"):

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

    mat.use_nodes = True
    if bl28():
        mat.blend_method = 'HASHED'
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    while nodes:
        nodes.remove(nodes[0])

    nodesDir = os.path.join(os.path.dirname(__file__),"..","data","nodes")
    texturesDir = os.path.join(os.path.dirname(__file__),"..","data","textures")

    materialPath = os.path.join(nodesDir,materialFile)

    with open(materialPath,"r") as f:
        defaultMaterial = json.load(f)

    for groupName in defaultMaterial["groups"].keys():
        groupDef = defaultMaterial["groups"][groupName]
        if groupDef["create"]:
            formalGroupName = name + '_' + groupName
            print("About to create " + formalGroupName)
            groupDef["nodes"] = bpy.data.node_groups.new(formalGroupName, 'ShaderNodeTree')

            for inputSocket in groupDef["inputs"].keys():
                type = groupDef["inputs"][inputSocket]["type"]
                input = groupDef["nodes"].inputs.new(type, inputSocket)
                if "value" in groupDef["inputs"][inputSocket]:
                    input.default_value = groupDef["inputs"][inputSocket]["value"]

            for outputSocket in groupDef["outputs"].keys():
                type = groupDef["outputs"][outputSocket]["type"]
                groupDef["nodes"].outputs.new(type, outputSocket)

            groupDef["object"] = nodes.new("ShaderNodeGroup")
            groupDef["object"].node_tree = bpy.data.node_groups[formalGroupName]
            groupDef["object"].location = groupDef["location"]

    _updatePrincipled(defaultMaterial, materialSettingsHash, baseColor)
    _updateDiffuseTexture(defaultMaterial, materialSettingsHash)
    _updateNormalMapAndBumpmapTexture(defaultMaterial, materialSettingsHash)

    if "sss" in materialFile.lower():
        sss = defaultMaterial["nodes"].get("ssstex")
        if sss:
            sss["imageData"]["path"] = os.path.join(texturesDir,"sss.png")

    for nodeName in defaultMaterial["nodes"].keys():
        nodeDef = defaultMaterial["nodes"][nodeName]
        usedNodes = nodes
        if nodeDef["create"]:
            print("Will create node " + nodeName + " with type " + nodeDef["type"])
            if nodeDef["group"]:
                groupName = nodeDef["group"]
                if defaultMaterial["groups"][groupName]["create"]:
                    usedNodes = defaultMaterial["groups"][groupName]["nodes"].nodes
            if "imageData" in nodeDef:
                nodeDef["object"] = _createMHImageTextureNode(usedNodes, nodeDef["imageData"]["path"], color_space=nodeDef["imageData"]["colorspace_settings_name"])
            else:
                nodeDef["object"] = usedNodes.new(nodeDef["type"])
            nodeDef["object"].location = nodeDef["location"]
            nodeDef["object"].label = nodeDef["label"] + " (" + nodeName + ")"

            for propertyName in nodeDef["values"].keys():
                value = nodeDef["values"][propertyName]
                print("Will attempt to set " + nodeName + "[" + propertyName + "] to " + str(value))
                nodeDef["object"].inputs[propertyName].default_value = value

            if nodeDef["type"] == "ShaderNodeMath":
                nodeDef["object"].operation = nodeDef["operation"]

            if nodeDef["type"] == "ShaderNodeValToRGB":
                elements = nodeDef["object"].color_ramp.elements
                numStopsInNode = len(elements)
                numStopsInDef = len(nodeDef["stops"])

                while numStopsInNode < numStopsInDef:
                    elements.new(1.0)
                    numStopsInNode = len(elements)

                i = 0
                for stop in elements:
                    stop.position = nodeDef["stops"][i]
                    i = i + 1


    for connection in defaultMaterial["connections"]:

        inputName = connection["inputNode"]
        outputName = connection["outputNode"]        

        if inputName in defaultMaterial["nodes"] and outputName in defaultMaterial["nodes"]:
            outputNodeDef = defaultMaterial["nodes"][outputName]
            inputNodeDef = defaultMaterial["nodes"][inputName]

            if outputNodeDef["create"] and inputNodeDef["create"]: # If either doesn't exist, it doesn't make sense to link
                usedLinks = links
                if outputNodeDef["group"]:
                    usedLinks = defaultMaterial["groups"][outputNodeDef["group"]]["nodes"].links
                outputNode = outputNodeDef["object"]
                inputNode = inputNodeDef["object"]
                outputSocket = connection["outputSocket"]
                inputSocket = connection["inputSocket"]
                print("Will attempt to link " + connection["outputNode"] + "[" + str(outputSocket) + "] to " + connection["inputNode"] + "[" + str(inputSocket) + "]")

                usedLinks.new(outputNode.outputs[outputSocket], inputNode.inputs[inputSocket])
        else:
            # either side or both is probably a group
            inputNode = None
            if inputName in defaultMaterial["nodes"]:
                if defaultMaterial["nodes"][inputName]["create"]:
                    inputNode = defaultMaterial["nodes"][inputName]["object"]
            else:
                if inputName in defaultMaterial["groups"]:
                    if defaultMaterial["groups"][inputName]["create"]:
                        inputNode = defaultMaterial["groups"][inputName]["object"]
            outputNode = None
            if outputName in defaultMaterial["nodes"]:
                if defaultMaterial["nodes"][outputName]["create"]:
                    outputNode = defaultMaterial["nodes"][outputName]["object"]
            else:
                if outputName in defaultMaterial["groups"]:
                    if defaultMaterial["groups"][outputName]["create"]:
                        outputNode = defaultMaterial["groups"][outputName]["object"]
            if inputNode and outputNode:
                outputSocket = connection["outputSocket"]
                inputSocket = connection["inputSocket"]
                print("Will attempt to link " + connection["outputNode"] + "[" + str(outputSocket) + "] to " + connection["inputNode"] + "[" + str(inputSocket) + "]")
                # We won't support groups inside groups, so always assume this is top level
                links.new(outputNode.outputs[outputSocket], inputNode.inputs[inputSocket])

    if len(mat.diffuse_color) == 4:
        mat.diffuse_color = baseColor
    else: # This section is for backward compatibility with Blender 2.79 and should be removed asap
        mat.diffuse_color = baseColor[:-1]

    return mat

def createMHMaterial(name, materialSettingsHash, baseColor=(0.8, 0.8, 0.8, 1.0), ifExists="CREATENEW"):


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

    mat.use_nodes = True
    if bl28():
        mat.blend_method = 'HASHED'
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    while nodes:
        nodes.remove(nodes[0])

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (x + 250, y + 10)

    principled = nodes.new("ShaderNodeBsdfPrincipled")
    roughness = 1.0 - materialSettingsHash["shininess"]
    if fixrough and roughness < 0.1 and not "eye" in name.lower():
        roughness = 0.5
    principled.inputs['Roughness'].default_value = roughness
    if len(principled.inputs['Base Color'].default_value) == 4:
        if 'diffuseColor' in materialSettingsHash:
            col = materialSettingsHash.get('diffuseColor')
            while len(col) < 4:
                col.append(1.0)
            principled.inputs['Base Color'].default_value = col
        else:
            principled.inputs['Base Color'].default_value = baseColor
    else: # This section is for backward compatibility with Blender 2.79 and should be removed asap
        principled.inputs['Base Color'].default_value = materialSettingsHash.get('diffuseColor', baseColor[:-1])


    diffuse = materialSettingsHash.get("diffuseTexture")
    if diffuse:
        diffuseTexture = _createMHImageTextureNode(nodes, diffuse)
        diffuseTexture.location = (x - 500, y + 100)

        principled.location = (x - 100, y - 50)

        links.new(output.inputs['Surface'], principled.outputs['BSDF'])
        links.new(principled.inputs['Base Color'], diffuseTexture.outputs['Color'])
        links.new(principled.inputs['Alpha'], diffuseTexture.outputs['Alpha'])
    else:
        principled.location = (x + 100, y + 10)
        links.new(output.inputs['Surface'], principled.outputs['BSDF'])

    nmtex = materialSettingsHash.get("normalMapTexture")
    bmtex = materialSettingsHash.get("bumpMapTexture")

    if nmtex and bmtex: # Material has bump- and normalmap

        bmTexture = _createMHImageTextureNode(nodes, bmtex, 'Non-Color')
        bmTexture.location = (x - 700, y - 300)

        bmap = nodes.new("ShaderNodeBump")
        bmap.location = (x - 400, y - 300)

        links.new(bmap.inputs['Height'], bmTexture.outputs['Color'])
        links.new(principled.inputs['Normal'], bmap.outputs['Normal'])

        bmap.inputs['Strength'].default_value = materialSettingsHash.get('bumpMapIntensity', 1.0)

        nmTexture = _createMHImageTextureNode(nodes, nmtex, 'Non-Color')
        nmTexture.location = (x - 800, y - 900)

        nmap = nodes.new("ShaderNodeNormalMap")
        nmap.location = (x - 600, y - 700)

        links.new(nmap.inputs['Color'], nmTexture.outputs['Color'])
        links.new(bmap.inputs['Normal'], nmap.outputs['Normal'])
        nmap.inputs['Strength'].default_value = materialSettingsHash.get('normalMapIntensity', 1.0)

    else:

        if nmtex: # Material has only normalmap
            nmTexture = _createMHImageTextureNode(nodes, nmtex, 'Non-Color')
            nmTexture.location = (x - 700, y - 300)

            nmap = nodes.new("ShaderNodeNormalMap")
            nmap.location = (x - 400, y - 300)

            links.new(nmap.inputs['Color'], nmTexture.outputs['Color'])
            links.new(principled.inputs['Normal'], nmap.outputs['Normal'])

            nmap.inputs['Strength'].default_value = materialSettingsHash.get('normalMapIntensity', 1.0)

        elif bmtex: # Material has only bumpmap
            bmTexture = _createMHImageTextureNode(nodes, bmtex, 'Non-Color')
            bmTexture.location = (x - 700, y - 300)

            bmap = nodes.new("ShaderNodeNormalMap")
            bmap.location = (x - 400, y - 300)

            links.new(bmap.inputs['Height'], bmTexture.outputs['Color'])
            links.new(principled.inputs['Normal'], bmap.outputs['Normal'])

            bmap.inputs['Strength'].default_value = materialSettingsHash.get('bumpMapIntensity', 1.0)

        else:
            pass


    if len(mat.diffuse_color) == 4:
        mat.diffuse_color = baseColor
    else: # This section is for backward compatibility with Blender 2.79 and should be removed asap
        mat.diffuse_color = baseColor[:-1]

    return mat

