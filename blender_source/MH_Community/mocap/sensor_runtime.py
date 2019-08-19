from .animation_buffer import *
from ..rig.riginfo import *

from json import loads

import bpy

METERS_TO_INCHES = 39.3701
#===============================================================================
# all static class.  Allows data to be retrieved across .blends
class Sensor():
    # state members for poll()
    recording = False

    # static so can be referenced in a static method callback
    # temporary holding places until recording complete
    sensorType = None
    jointDict = None
    frame_buffer = None
    trackedBodies = None
    dumped = False

    # permanent parsed animations by body
    animationBuffers = None

    @staticmethod
    def beginRecording(sensorType = 'KINECT2'):
        Sensor.dumped = False
        # initialize temporary stores for returned data
        Sensor.frame_buffer  = []
        Sensor.trackedBodies = []

        if sensorType == 'KINECT2':
            from .kinect2.kinect2_sensor import Kinect2Sensor
            Sensor.sensorInfo = Kinect2Sensor.getSensorInfo()
            problemMsg = Kinect2Sensor.capture()

        elif sensorType == 'KINECT_AZURE':
            pass

        if problemMsg is not None:
            return problemMsg
        else:
            Sensor.recording = True
            Sensor.sensorType = sensorType
            return None

    @staticmethod
    def process(data):
        # dump the first frame to console
        if not Sensor.dumped:
            print(data.decode('ascii'))
            Sensor.dumped = True

        try:
            json_obj = loads(data.decode('ascii')) # parse the data into a collection, after converting from binary

        except:
            print ('problem in JSON:\n' + data.decode('ascii') + '\n')
            return

        for bod in json_obj['bodies']:
            thisId = bod['id']
            alreadyFound = False
            for id in Sensor.trackedBodies:
                if thisId == id:
                    alreadyFound = True
                    break

            if not alreadyFound:
                Sensor.trackedBodies.append(thisId)

        Sensor.frame_buffer.append(json_obj)

    @staticmethod
    def stopRecording():
        if Sensor.sensorType == 'KINECT2':
            from .kinect2.kinect2_sensor import Kinect2Sensor
            millisFromFloor = Kinect2Sensor.close()

        elif Sensor.sensorType == 'KINECT_AZURE':
            return

        inches = METERS_TO_INCHES * millisFromFloor / 1000
        bpy.context.scene.MhSensorCameraHeight = ('%.1f' % inches) + ' inches, ' + ('%.3f' % (millisFromFloor / 1000)) + ' meters'
        Sensor.recording = False

        maxBodies = len(Sensor.trackedBodies)
        nFrames = len(Sensor.frame_buffer)
        if maxBodies == 0 or nFrames == 0:
            return 'No bodies / frames were captured.  No actions created.'

        # not using nFrames, if using multi-bodies, with missing frames due to testing mult-bodies using single person
        lastFrame = Sensor.frame_buffer[nFrames - 1]['frame']
        print ('Max bodies: ' + str(maxBodies) + ', n frames: ' + str(nFrames) + ' (0 - ' + str(lastFrame) + ')')

        # empty all previous animations
        Sensor.animationBuffers = []

        for idx, id in enumerate(Sensor.trackedBodies):
            # create a animation buffer & add it to the static array
            animation = AnimationBuffer('Body ' + str(idx), idx == 0)
            Sensor.animationBuffers.append(animation)

            # pull all the data for this body
            n = 0
            for data in Sensor.frame_buffer:
                # check that this body is in this frame, then add frame data
                for bod in data['bodies']:
                    if id == bod['id']:
                        # hands might not be in data, when not Kinect2
                        hands = bod['hands'] if 'hands' in bod else []
                        animation.loadSensorFrame(data['frame'], bod['joints'], hands, data['floorClipPlane'])
                    #    print('frame ' + str(n) + ', clip plane ' + str(data['floorClipPlane']['w']) + ', root location: ' + str(bod['joints']['SpineBase']['location']['y']))
                        break

            animation.removeTwitching(Sensor.sensorInfo.jointDict)

        # update list of recordings
        Sensor.displayRecordings()

        # assign scene frame rate, beginning & end frame
        bpy.context.scene.render.fps = 30
        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = lastFrame

        # clear temporary holding spots
        Sensor.frame_buffer  = None
        Sensor.trackedBodies = None

        return None

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # As Sensor is static class & also holds all data from last session,
    # these methods below are used to update body list, assign action, & animate
    # one frame at a time, using capture skeleton (diagnostic)
    @staticmethod
    def displayRecordings():
        # empty all previous list items
        collectionProperty = bpy.context.scene.MhSensorAnimations
        for i in range(len(collectionProperty) - 1, -1, -1):
            collectionProperty.remove(i)

        if Sensor.animationBuffers is None: return

        for i in range(len(Sensor.animationBuffers)):
            # add an item to the collection, so shows up in the list
            item = collectionProperty.add()
            item.id = i
            item.name = Sensor.animationBuffers[i].name

    @staticmethod
    def assign(rigInfo, idx, baseActionName):
        Sensor.animationBuffers[idx].assign(rigInfo, baseActionName, rigInfo.getSensorMapping(Sensor.sensorType), Sensor.sensorInfo.jointDict)

    @staticmethod
    def assignIk(rigInfo, idx, baseActionName):
        Sensor.animationBuffers[idx].assignIk(rigInfo, baseActionName, Sensor.sensorInfo)

    @staticmethod
    def oneRight(rigInfo, idx):
        Sensor.animationBuffers[idx].oneRight(rigInfo, rigInfo.getSensorMapping(Sensor.sensorType), Sensor.sensorInfo.jointDict)
        
#===============================================================================
class SensorInfo():
    
    def setJointDict(self, value):
        self.jointDict = value
        
    def setPelvisName(self, value):
        self.pelvisName = value    
        
    def setAnkleNames(self, left, right):
        self.leftAnkleName = left
        self.rightAnkleName = right
        
    def setKneeNames(self, left, right):
        self.leftKneeName = left
        self.rightKneeName = right
        
    def setWristNames(self, left, right):
        self.leftWristName = left
        self.rightWristName = right
        
    def setElbowNames(self, left, right):
        self.leftElbowName = left
        self.rightElbowName = right
        