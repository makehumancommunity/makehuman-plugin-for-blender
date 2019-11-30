#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

HELPER_GROUPS = {'Body': ['body'],
                 'Tongue': ['helper-tongue'],
                 'Joints': ['joint-head-2', 'joint-head', 'joint-jaw', 'joint-l-ankle',
                            'joint-l-clavicle', 'joint-l-elbow', 'joint-l-eye', 'joint-l-eye-target', 
                            'joint-l-finger-1-1', 'joint-l-finger-1-2', 'joint-l-finger-1-3', 'joint-l-finger-1-4', 
                            'joint-l-finger-2-1', 'joint-l-finger-2-2', 'joint-l-finger-2-3', 'joint-l-finger-2-4', 
                            'joint-l-finger-3-1', 'joint-l-finger-3-2', 'joint-l-finger-3-3', 'joint-l-finger-3-4', 
                            'joint-l-finger-4-1', 'joint-l-finger-4-2', 'joint-l-finger-4-3', 'joint-l-finger-4-4', 
                            'joint-l-finger-5-1', 'joint-l-finger-5-2', 'joint-l-finger-5-3', 'joint-l-finger-5-4', 
                            'joint-l-foot-1', 'joint-l-foot-2', 'joint-l-hand-2', 'joint-l-hand-3', 'joint-l-hand', 
                            'joint-l-knee', 'joint-l-lowerlid', 'joint-l-scapula', 'joint-l-shoulder', 'joint-l-toe-1-1', 
                            'joint-l-toe-1-2', 'joint-l-toe-1-3', 'joint-l-toe-2-1', 'joint-l-toe-2-2', 
                            'joint-l-toe-2-3', 'joint-l-toe-2-4', 'joint-l-toe-3-1', 'joint-l-toe-3-2', 
                            'joint-l-toe-3-3', 'joint-l-toe-3-4', 'joint-l-toe-4-1', 'joint-l-toe-4-2', 
                            'joint-l-toe-4-3', 'joint-l-toe-4-4', 'joint-l-toe-5-1', 'joint-l-toe-5-2', 
                            'joint-l-toe-5-3', 'joint-l-toe-5-4', 'joint-l-upper-leg', 'joint-l-upperlid', 
                            'joint-mouth', 'joint-neck', 'joint-pelvis', 'joint-r-ankle', 'joint-r-clavicle', 
                            'joint-r-elbow', 'joint-r-eye', 'joint-r-eye-target', 'joint-r-finger-1-1', 
                            'joint-r-finger-1-2', 'joint-r-finger-1-3', 'joint-r-finger-1-4', 'joint-r-finger-2-1', 
                            'joint-r-finger-2-2', 'joint-r-finger-2-3', 'joint-r-finger-2-4', 'joint-r-finger-3-1', 
                            'joint-r-finger-3-2', 'joint-r-finger-3-3', 'joint-r-finger-3-4', 'joint-r-finger-4-1', 
                            'joint-r-finger-4-2', 'joint-r-finger-4-3', 'joint-r-finger-4-4', 'joint-r-finger-5-1', 
                            'joint-r-finger-5-2', 'joint-r-finger-5-3', 'joint-r-finger-5-4', 'joint-r-foot-1', 
                            'joint-r-foot-2', 'joint-r-hand-2', 'joint-r-hand-3', 'joint-r-hand', 'joint-r-knee', 
                            'joint-r-lowerlid', 'joint-r-scapula', 'joint-r-shoulder', 'joint-r-toe-1-1', 
                            'joint-r-toe-1-2', 'joint-r-toe-1-3', 'joint-r-toe-2-1', 'joint-r-toe-2-2', 
                            'joint-r-toe-2-3', 'joint-r-toe-2-4', 'joint-r-toe-3-1', 'joint-r-toe-3-2', 
                            'joint-r-toe-3-3', 'joint-r-toe-3-4', 'joint-r-toe-4-1', 'joint-r-toe-4-2', 
                            'joint-r-toe-4-3', 'joint-r-toe-4-4', 'joint-r-toe-5-1', 'joint-r-toe-5-2', 
                            'joint-r-toe-5-3', 'joint-r-toe-5-4', 'joint-r-upper-leg', 'joint-r-upperlid', 
                            'joint-spine-1', 'joint-spine-2', 'joint-spine-3', 'joint-spine-4', 'joint-tongue-1', 
                            'joint-tongue-2', 'joint-tongue-3', 'joint-tongue-4'],
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

    bl_idname = 'mh_community.add_simple_material'
    bl_label = 'Add simple material to Helpers'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return getattr(obj, 'MhHuman', False)

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
    for _ in range(len(obj.material_slots.keys())):
        bpy.ops.object.material_slot_remove()

def createMaterial(name: str, color=(0.0, 0.0, 0.0, 1.0)):
    material = bpy.data.materials.new(name)
    material.diffuse_color = color
    return material

def addMaterial(obj, name, color):
    slotCount = len(obj.material_slots.keys())
    material = createMaterial(name, color)
    bpy.ops.object.material_slot_add()
    obj.material_slots[slotCount].material = material
