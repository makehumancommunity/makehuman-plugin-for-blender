#!/usr/bin/python

from namespace import NameSpace

class API(NameSpace):

    def __init__(self,app):
        self._app = app
        NameSpace.__init__(self)
        self.trace()

        from _assets import Assets
        self.assets = Assets(self)

        from _internals import Internals
        self.internals = Internals(self)

        from _mesh import Mesh
        self.mesg = Mesh(self)

        from _locations import Locations
        self.locations = Locations(self)

        from _version import Version
        self.version = Version(self)

        from _viewport import Viewport
        self.viewport = Viewport(self)

        from _modifiers import Modifiers
        self.modifiers = Modifiers(self)

        from _ui import UI
        self.ui = UI(self)

