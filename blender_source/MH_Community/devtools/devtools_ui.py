import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

def registerDevtoolsConstantsAndSettings():
    pass

def addDevtoolsToTab(layout, scn):

    devtoolsBox = layout.box()
    devtoolsBox.label(text="Developer tools", icon="MESH_DATA")
    devtoolsBox.operator("mh_community.print_vertex_groups", text="Dump vgroups")

