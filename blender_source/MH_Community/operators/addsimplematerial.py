#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

HELPER_GROUPS = {'Body': ['body'],
                 'Tongue': ['helper-tongue'],
                 'Joints': ['JointCubes'],
                 'Eyes': ['helper-l-eye', 'helper-r-eye'],
                 'Eyelashes': ['helper-l-eyelashes', 'helper-r-eyelashes'],
                 'Teeth': ['helper-upper-teeth','helper-lower-teeth'],
                 'Genitals': ['helper-genital'],
                 'Tights': ['helper-tights'],
                 'Skirt': ['helper-skirt'],
                 'Hair': ['helper-hair'],
                 'Ground': ['joint-ground']
                 }


COLORS = {'Body': (1.0, 1.0, 1.0, 1.0),
          'Tongue': (0.5, 0.0, 0.5, 1.0),
          'Joints': (0.0, 1.0, 0.0, 1.0),
          'Eyes': (0.0, 1.0, 1.0, 1.0),
          'Eyelashes': (1.0, 0.0, 1.0, 1.0),
          'Teeth': (0.0, 0.5, 0.5, 1.0),
          'Genitals': (0.5, 0.0, 1.0, 1.0),
          'Tights': (1.0, 0.0, 0.0, 1.0),
          'Skirt': (0.0, 0.0, 1.0, 1.0),
          'Hair': (1.0, 1.0, 0.0, 1.0),
          'Ground': (1.0, 0.5, 0.5, 1.0)}


class MHC_OT_AddSimpleMaterials(bpy.types.Operator):

    bl_idname = 'mh_community.add_simple_materials'
    bl_label = 'Add simple material to Helpers'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        # Check if the MhHuman property is True and if the mesh has detailed vertex groups,
        # assuming this is True when the joint-ground vertex group exists.
        return getattr(obj, 'MhHuman', False) and obj.vertex_groups.find('joint-ground') >= 0

    def execute(self, context):
        context = bpy.context
        obj = context.object

        clearMaterialSlots(obj)

        bpy.ops.object.mode_set(mode='EDIT')

        for name, groups in HELPER_GROUPS.items():
            addMaterial(obj, name, COLORS.get(name, (0.0, 0.0, 0.0, 1.0)))
            bpy.ops.mesh.select_all(action='DESELECT')
            for group in groups:
                vgIdx = obj.vertex_groups.find(group)
                obj.vertex_groups.active_index = vgIdx
                bpy.ops.object.vertex_group_select()
            mslotIdx = obj.material_slots.find(name)
            obj.active_material_index = mslotIdx
            bpy.ops.object.material_slot_assign()

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


def clearMaterialSlots(obj):
    for _ in obj.material_slots.keys():
        bpy.ops.object.material_slot_remove()

def createMaterial(name: str, color=(0.0, 0.0, 0.0, 1.0)):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    return material

def addMaterial(obj, name: str, color=(0.0, 0.0, 0.0, 1.0)):
    slotCount = len(obj.material_slots.keys())
    material = createMaterial(name, color)
    bpy.ops.object.material_slot_add()
    obj.material_slots[slotCount].material = material
