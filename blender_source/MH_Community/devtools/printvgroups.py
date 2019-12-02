#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import pprint

class MHC_OT_PrintVGroupsOperator(bpy.types.Operator):
    """Import a human from MH"""
    bl_idname = "mh_community.print_vertex_groups"
    bl_label = "Dump vertex groups of active object to /tmp/vgroups.py"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == 'MESH' and hasattr(obj, "MhObjectType")

    def execute(self, context):
        obj = context.object
        objuuid = "basemesh"

        if obj.MhObjectType != "Basemesh":
            objuuid = obj.MhProxyUUID

        vgroupsRoot = dict()
        vgroupsRoot[objuuid] = dict()
        vgroups = vgroupsRoot[objuuid]

        vgIdxToName = dict()

        if obj:
            with open("/tmp/vgroups.py","w") as f:
                f.write("#!/usr/bin/python\n")
                f.write("# -*- coding: utf-8 -*-\n\n")
                f.write("vgroupInfo = dict()\n")
                vn = "groupInfo[\"" + objuuid + "\"]"
                f.write(vn + " = dict()\n")

                for vg in obj.vertex_groups:
                    vgroups[vg.name] = []
                    vgIdxToName[vg.index] = vg.name

                for vert in obj.data.vertices:
                    for groupe in vert.groups:
                        group = vgIdxToName[groupe.group]
                        vgroups[group].append(vert.index)
                for vgname in vgroups.keys():
                    f.write(vn + "[\"" + vgname + "\"] = ")
                    pprint.pprint(vgroups[vgname],f,width=50000,compact=True)

        else:
            self.report({'ERROR'}, "No object")

        self.report({'INFO'}, "Wrote " + objuuid + " to /tmp/vgroups.py")

        return {'FINISHED'}
