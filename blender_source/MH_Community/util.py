import bpy

def bl28():
    return bpy.app.version >= (2, 80, 0)

def linkObject(obj):
    if bl28():
        bpy.context.collection.objects.link(obj)
    else:
        bpy.context.scene.objects.link(obj)

def activateObject(obj):
    if bl28():
        bpy.context.view_layer.objects.active = obj
    else:
        bpy.context.scene.objects.active = obj

def selectObject(obj):
    if bl28():
        obj.select_set(True)
    else:
        obj.select = True

def deselectObject(obj):
    if bl28():
        obj.select_set(False)
    else:
        obj.select = False
