#!/usr/bin/python

from namespace import NameSpace

class Modifiers(NameSpace):
    """This namespace wraps calls concerning modifiers and targets."""

    def __init__(self,api):
        self.api = api
        NameSpace.__init__(self)
        self.trace()

