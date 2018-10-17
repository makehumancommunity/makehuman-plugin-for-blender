from .animation_buffer import *

from struct      import calcsize # needed to figure out whether on 32 or 64 bit Blender
from ctypes      import cdll, c_char, c_char_p, c_void_p, CFUNCTYPE
from json        import loads
from os          import path
from sys         import platform

import bpy
#===============================================================================
#Dump of file KinectToJSON_x64.dll
#
#File Type: DLL
#
#  Section contains the following exports for KinectToJSON_x64.dll
#
#    00000000 characteristics
#    FFFFFFFF time date stamp
#        0.00 version
#           1 ordinal base
#           4 number of functions
#           4 number of names
#
#    ordinal hint RVA      name
#
#          1    0 000115D7 ?beginBodyTracking@@YAJP6AXPEAD@Z@Z = @ILT+1490(?beginBodyTracking@@YAJP6AXPEAD@Z@Z)
#          2    1 000114BA ?closeSensor@@YAXXZ = @ILT+1205(?closeSensor@@YAXXZ)
#          3    2 00011398 ?endBodyTracking@@YAXXZ = @ILT+915(?endBodyTracking@@YAXXZ)
#          4    3 0001109B ?openSensor@@YAJDDD@Z = @ILT+150(?openSensor@@YAJDDD@Z)

# ordinal seems to be alphabetical; calling by ordinal here
BEGIN_BODY_TRACKING = 1
CLOSE_SENSOR        = 2
END_BODY_TRACKING   = 3
OPEN_SENSOR         = 4

METERS_TO_INCHES = 39.3701
#===============================================================================
# all static class.
class KinectSensor():
    DLL = None
    callback_func = None # cannot be a local var, or segfault

    # state members for poll()
    ready = None
    recording = False

    # static so can be referenced in a static method callback
    # temporary holding places until recording complete
    frame_buffer = None
    trackedBodies = None
    dumped = False

    # permanent parsed animations by body
    animationBuffers = None

    @staticmethod
    def isKinectReady():
        # This test is only performed once.  Subsequent calls just echo first test, so can be used in UI polling
        if KinectSensor.ready is not None:
             return KinectSensor.ready

        # Sensor only works on windows.  Keep Linux, others from erroring
        if platform != "win32" and platform != "win64":
            print('Kinect only works on a Windows operating system.')
            KinectSensor.ready = False
            return False

        # actually try to load the dll, inside try block, in case they failed do to install Kinect runtime re-distributable
        try:
            is64Bit = calcsize("P") * 8 == 64  # using sys.platform is NOT reliable
            fileName = 'KinectToJSON_' + ('x64' if is64Bit else 'x86') + '.dll'
            moduleDirectory = path.dirname(__file__)
            filepath = path.join(moduleDirectory, fileName)
            KinectSensor.DLL = cdll.LoadLibrary(filepath)
            print('DLL: ' + fileName + ', loaded from: ' + moduleDirectory)

        except:
            print('DLL: ' + fileName + ', on path: ' + moduleDirectory +', failed to load.\nIs Kinect re-distributable installed?')
            KinectSensor.ready = False
            return False

        # the only way to be sure is to open the sensor & check the result
        KinectSensor.DLL[OPEN_SENSOR].argtypes = (c_char, c_char)
        hresult = KinectSensor.DLL[OPEN_SENSOR](c_char('\1'.encode()), c_char('F'.encode()))
        KinectSensor.ready = KinectSensor.SUCCEEDED(hresult)

        #when successful, have the side effect of sensor being open. Reverse that
        if KinectSensor.ready:
            KinectSensor.DLL[CLOSE_SENSOR]()
            print('Kinect is fully ready')
        else:
            print('Kinect open sensor failed.  Is it plugged in & connected?')
        return KinectSensor.ready

    @staticmethod
    def capture():
        KinectSensor.dumped = False

        # prep args & define to call
        tPoseStart = c_char('\1'.encode()) # always say true
        ForM  = c_char('F'.encode())
        KinectSensor.DLL[OPEN_SENSOR].argtypes = (c_char, c_char)

        hresult = KinectSensor.DLL[OPEN_SENSOR](tPoseStart, ForM)
        if not KinectSensor.SUCCEEDED(hresult): return

        # initialize temporary stores for returned data
        KinectSensor.frame_buffer  = []
        KinectSensor.trackedBodies = []

        # call to start tracking
        callback_type = CFUNCTYPE(c_void_p, c_char_p)
        KinectSensor.callback_func = callback_type(KinectSensor.bodyReaderCallback)

        KinectSensor.DLL[BEGIN_BODY_TRACKING].argtypes = [c_void_p, c_char_p]
        hresult = KinectSensor.DLL[BEGIN_BODY_TRACKING](KinectSensor.callback_func)
        KinectSensor.recording = KinectSensor.SUCCEEDED(hresult)

    @staticmethod
    def bodyReaderCallback(data):
        # dump the first frame to console
        if not KinectSensor.dumped:
            print(data.decode('ascii'))
            KinectSensor.dumped = True

        try:
            json_obj = loads(data.decode('ascii')) # parse the data into a collection, after converting from binary

        except:
            print ('problem in JSON:\n' + data.decode('ascii') + '\n')
            return

        for bod in json_obj['bodies']:
            thisId = bod['id']
            alreadyFound = False
            for id in KinectSensor.trackedBodies:
                if thisId == id:
                    alreadyFound = True
                    break

            if not alreadyFound:
                KinectSensor.trackedBodies.append(thisId)

        KinectSensor.frame_buffer.append(json_obj)

    @staticmethod
    def close():
        # closeSensor automatically closes body reader in DLL
        millis = KinectSensor.DLL[CLOSE_SENSOR]()
        bpy.context.scene.MhKinectCameraHeight = METERS_TO_INCHES * millis / 1000
        KinectSensor.recording = False

        maxBodies = len(KinectSensor.trackedBodies)
        nFrames = len(KinectSensor.frame_buffer)

        if maxBodies == 0 or nFrames == 0:
            print('No bodies / frames were captured.  No actions created.')
            return

        print ('Max bodies: ' + str(maxBodies) + ', n frames: ' + str(nFrames))

        # empty all previous animations
        KinectSensor.animationBuffers = []

        for idx, id in enumerate(KinectSensor.trackedBodies):
            # create a animation buffer & add it to the static array
            animation = AnimationBuffer('Body ' + str(idx))
            KinectSensor.animationBuffers.append(animation)

            # pull all the data for this body
            for data in KinectSensor.frame_buffer:
                # check that this body is in this frame, then add frame data
                for bod in data['bodies']:
                    if id == bod['id']:
                        animation.loadSensorFrame(data['frame'], bod['bones'], bod['hands'], data['floorClipPlane'])
                        break

        # update list of recordings
        KinectSensor.displayRecordings()

        # assign scene frame rate, beginning & end frame
        bpy.context.scene.render.fps = 30
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = nFrames - 1

        # clear temporary holding spots
        KinectSensor.frame_buffer  = None
        KinectSensor.trackedBodies = None

    # windows dll call return evaluater
    @staticmethod
    def SUCCEEDED(hresult):
        return hresult == 0
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # As KinectSensor is static class & also holds all data from last session,
    # these methods below are used to update body list, assign action, & animate
    # one frame at a time, using capture skeleton (diagnostic)
    @staticmethod
    def displayRecordings():
        # empty all previous list items
        collectionProperty = bpy.context.scene.MhKinectAnimations
        for i in range(len(collectionProperty) - 1, -1, -1):
            collectionProperty.remove(i)

        if KinectSensor.animationBuffers is None: return

        for i in range(len(KinectSensor.animationBuffers)):
            # add an item to the collection, so shows up in the list
            item = collectionProperty.add()
            item.id = i
            item.name = KinectSensor.animationBuffers[i].name

    @staticmethod
    def assign(armature, idx, baseActionName, excludeFingers):
        KinectSensor.animationBuffers[idx].assign(armature, baseActionName, excludeFingers)

    @staticmethod
    def oneRight(armature, idx):
        KinectSensor.animationBuffers[idx].oneRight(armature)
