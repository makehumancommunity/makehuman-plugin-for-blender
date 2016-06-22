#!/usr/bin/python

from namespace import NameSpace

import mh
import humanmodifier
import material
import gui
import gui3d
import log
import os
from cStringIO import StringIO
from core import G
from codecs import open

class Modifiers(NameSpace):
    """This namespace wraps calls concerning modifiers and targets."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.human = api.internals.getHuman()
        self.trace()

    def applyModifier(self, modifierName, power):
        modifier = self.human.getModifier(modifierName)
        modifier.setValue(value)
        self.human.applyAllTargets()
        mh.redraw()

    def applyTarget(self,targetName,power):
        self.human.setDetail(mh.getSysDataPath("targets/" + targetName + ".target"), power)
        self.human.applyAllTargets()
        mh.redraw()

    def getAppliedTargets(self):
        targets = dict()
        print self.human.targetsDetailStack
        for target in self.human.targetsDetailStack.keys():
            paths = target.split('/data/targets/')
            targets[paths[1]] = self.human.targetsDetailStack[target]
        return targets

    def setAge(self,age):
        self.human.setAge(age)
        mh.redraw()

    def setWeight(self,weight):
        self.human.setWeight(weight)
        mh.redraw()

    def setMuscle(self,muscle):
        self.human.setMuscle(muscle)
        mh.redraw()

    def setHeight(self,height):
        self.human.setHeight(height)
        mh.redraw()

    def setGender(self,gender):
        self.human.setGender(gender)
        mh.redraw()

    def getAvailableModifierNames(self):
        return sorted( self.human.getModifierNames() )

    def applySymmetryLeft(self):
        self.human.applySymmetryLeft()

    def applySymmetryRight(self):
        self.human.applySymmetryRight()



