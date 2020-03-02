import bpy
import time

_startMillis = None
_lastMillis = None

ENABLE_PROFILING=True

def profile(position = "timestamp"):
    global ENABLE_PROFILING
    if not ENABLE_PROFILING:
        return

    global _startMillis
    global _lastMillis

    if _startMillis is None:
        _startMillis = int(round(time.time() * 1000))
        _lastMillis = _startMillis - 1

    currentMillis = int(round(time.time() * 1000))
    print(position + ": " + str(currentMillis - _startMillis) + " / " + str(currentMillis - _lastMillis))
    _lastMillis = currentMillis


def bl28():
    return bpy.app.version >= (2, 80, 0)

def linkObject(obj, parent=None):
    if bl28():
        if parent:
            parent.objects.link(obj)
        else:
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

def showMessageBox(message='', title='MessageBox', icon='INFO'):

    def draw(self, context):
        lines = message.split('\n')
        for line in lines:
            self.layout.label(text=line)

    print(message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)
