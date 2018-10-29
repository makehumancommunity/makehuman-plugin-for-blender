#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

handleHelperItems = []
handleHelperItems.append( ("MASK", "Mask", "Mask helper geometry", 1) )
handleHelperItems.append( ("NOTHING", "Leave be", "Leave helper geometry as is", 2) )
handleHelperItems.append( ("DELETE", "Delete", "Delete helper geometry", 3))

scaleModeItems = []
scaleModeItems.append( ("METER", "Meter", "1 BU = 1 Meter", 1) )
scaleModeItems.append( ("DECIMETER", "Decimeter", "1 BU = 1 Decimeter", 2) )
scaleModeItems.append( ("CENTIMETER", "Centimeter", "1 BU = 1 Centimeter", 3) )

importProxyItems = []
importProxyItems.append( ("BODY", "Only import body", "Only import the base mesh body", 1) )
importProxyItems.append( ("BODYPARTS", "Body + bodyparts", "Only import the body and body parts such as eyes and hair", 2) )
importProxyItems.append( ("EVERYTHING", "Body, parts, clothes", "Import everything", 3) )

handleMaterialsItems = []
handleMaterialsItems.append( ("CREATENEW", "Create new", "Create a new material with a different name", 1) )
handleMaterialsItems.append( ("REUSE", "Use existing", "Use the existing material as it is", 2) )
handleMaterialsItems.append( ("OVERWRITE", "Overwrite", "Overwrite the existing material", 3) )

handleHiddenItems = []
handleHiddenItems.append( ("NOTHING", "Leave as is", "Do not do anything specific concerning hidden surfaces", 1) )
handleHiddenItems.append( ("MASK", "Mask", "Add a mask modifier to hide hidden surfaces", 2) )
handleHiddenItems.append( ("MATERIAL", "Invis material", "Add an invisible material to hidden surfaces", 3) )
handleHiddenItems.append( ("DELETE", "Delete", "Delete vertices for hidden surfaces", 4) )

def registerImporterConstantsAndSettings():
    # Properties for human importer
    bpy.types.Scene.MhHandleHelper = bpy.props.EnumProperty(items=handleHelperItems, name="handle_helper", description="How to handle helpers (such as clothes helper geometry and joint cubes)", default="MASK")
    bpy.types.Scene.MhScaleMode = bpy.props.EnumProperty(items=scaleModeItems, name="Scale mode", description="How long in real world terms is a blender unit?", default="METER")
    bpy.types.Scene.MhDetailedHelpers = BoolProperty(name="Detailed helper groups", description="Create one vertex group per helper part. This is usually superfluous unless you want to work with MakeTarget or MakeClothes", default=False)

    bpy.types.Scene.MhImportWhat = bpy.props.EnumProperty(items=importProxyItems, name="Import what", description="What to import", default="EVERYTHING")
    bpy.types.Scene.MhPrefixProxy = BoolProperty(name="Prefix proxy names", description="Give all extra meshes (such as hair, clothes..) names that start with the name of the imported toon", default=True)
    bpy.types.Scene.MhMaskBase = BoolProperty(name="Mask base mesh if proxy available", description="If both the base mesh and a body proxy have been imported, then mask the base mesh.", default=True)
    bpy.types.Scene.MhAddSubdiv = BoolProperty(name="Add a subdivision", description="Add subdivision modifiers to all imported meshes", default=True)

    bpy.types.Scene.MhHandleMaterials = bpy.props.EnumProperty(items=handleMaterialsItems, name="When material exists", description="What to do if a material with the same name already exists", default="REUSE")
    bpy.types.Scene.MhMaterialObjectName = BoolProperty(name="Name material after object", description="When creating a material, give it a name based on what mesh object it belongs to.", default=True)
    bpy.types.Scene.MhPrefixMaterial = BoolProperty(name="Prefix material names", description="Give all materials a name that starts with the name of the imported toon", default=False)
    bpy.types.Scene.MhFixRoughness = BoolProperty(name="Fix bad roughness", description="If a material is stated as having a roughness value of < 0.1, assume that this is an error and set to 0.5 instead.", default=True)

    bpy.types.Scene.MhHiddenFaces = bpy.props.EnumProperty(items=handleHiddenItems, name="Handle hidden faces", description="What to do about faces (on the body and/or the body proxy) which are hidden behind clothes.", default="MASK")

    bpy.types.Scene.MhImportRig = BoolProperty(name="Import rig", description="Import the rig if it is set in MH", default=True)
    bpy.types.Scene.MhRigBody = BoolProperty(name="Rig body and bodyparts", description="Use the imported rig as a skeleton for rigging the body and body parts such as eyes and hair", default=True)
    bpy.types.Scene.MhRigClothes = BoolProperty(name="Rig clothes", description="Use the imported rig as a skeleton for rigging clothes", default=True)
    bpy.types.Scene.MhRigIsParent = BoolProperty(name="Use rig as parent", description="Use the rig as parent for all imported / created objects", default=True)

    # bpy.types.Scene.MhHandIK = BoolProperty(name="Hand IK", description="Create hand IK controls", default=False)
    # bpy.types.Scene.MhFootIK = BoolProperty(name="Foot IK", description="Create foot IK controls", default=False)
    # bpy.types.Scene.MhHideFK = BoolProperty(name="Hide FK", description="Hide FK bones that are part of an IK chain", default=True)

    bpy.types.Object.MhProxyName = StringProperty(name="Proxy name", description="This is what the proxy is called in MakeHuman", default="")
    bpy.types.Object.MhProxyUUID = StringProperty(name="Proxy UUID", description="This is the UUID of the proxy in MakeHuman", default="")
    bpy.types.Object.MhObjectType = StringProperty(name="Object type", description="This is what type of MakeHuman object this is (such as Clothes, Eyes...)", default="")

    # In case MHX2 isn't loaded
    bpy.types.Object.MhHuman = BoolProperty(default=False)

    # TODO: hidden faces                MhHiddenFaces
    # TODO: Rig body and parts          MhRigBody
    # TODO: Rig clothes                 MhRigClothes
    # TODO: Use rig as parent           MhRigIsParent

def addImporterUIToTab(layout, scn):

    importHumanBox = layout.box()
    importHumanBox.label(text="Import human", icon="MESH_DATA")

    importHumanBox.label(text="Import meshes:")
    importHumanBox.prop(scn, 'MhImportWhat', text="")
    importHumanBox.prop(scn, 'MhPrefixProxy', text="Prefix with toon")
    importHumanBox.prop(scn, 'MhMaskBase', text="When proxy, mask base mesh")
    importHumanBox.prop(scn, 'MhAddSubdiv', text="Add subdiv modifier")

    importHumanBox.separator()
    importHumanBox.label(text="Helper geometry:")
    importHumanBox.prop(scn, 'MhHandleHelper', text="")
    importHumanBox.prop(scn, 'MhDetailedHelpers', text="Detailed helper groups")

    #importHumanBox.separator()
    #importHumanBox.label(text="Body hidden faces:")
    #importHumanBox.prop(scn, 'MhHiddenFaces', text="")

    importHumanBox.separator()
    importHumanBox.label(text="Blender unit equals:")
    importHumanBox.prop(scn, 'MhScaleMode', text="")

    importHumanBox.separator()
    importHumanBox.label(text="Materials:")
    importHumanBox.prop(scn, 'MhHandleMaterials', text="")
    importHumanBox.prop(scn, 'MhMaterialObjectName', text="Name after object")
    importHumanBox.prop(scn, 'MhPrefixMaterial', text="Prefix with toon")
    importHumanBox.prop(scn, 'MhFixRoughness', text="Fix bad roughness")

    importHumanBox.separator()
    importHumanBox.label(text="Rig / posing:")
    importHumanBox.prop(scn, 'MhImportRig', text="Import rig")
    #importHumanBox.prop(scn, 'MhRigBody', text="Rig body + parts")
    #importHumanBox.prop(scn, 'MhRigClothes', text="Rig clothes")
    importHumanBox.prop(scn, 'MhRigIsParent', text="Use rig as parent")

    # importHumanBox.prop(scn, 'MhHandIK', text="Hand IK")
    # importHumanBox.prop(scn, 'MhFootIK', text="Foot IK")
    # importHumanBox.prop(scn, 'MhHideFK', text="Hide FK")

    importHumanBox.separator()
    importHumanBox.operator("mh_community.import_body", text="Import human")